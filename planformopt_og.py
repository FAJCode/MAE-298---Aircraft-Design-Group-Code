"""A openmdao based optimization for an aicraft using optvl"""

# the x-start and x-end comments are for integration with the documentation
# they are not necessary for normal scripts
import openmdao.api as om
from optvl import OVLGroup, Differencer, OVLMeshReader
import numpy as np
import matplotlib.pyplot as plt
from optvl import OVLSolver
import glob
import os
import pyoptsparse


#class ScaleYComp(om.ExplicitComponent):
    # """
    # Scale the reference mesh Y coordinates to a desired physical wing span.

    # It will detect whether mesh Y is half-wing (all non-negative) or full
    # (symmetric +/-) and compute the correct scaling factor.
    # """
    #def initialize(self):
    #    self.options.declare("assume_half_span_if_nonneg", types=bool, default=True)

    #def setup(self):
        # mesh_y is the raw y coordinates read from the .avl file (e.g., 0..2)
    #     self.add_input("mesh_y", shape_by_conn=True)
    #     self.add_input("wing_span", val=55.0, units="m")   # desired full span (user)
    #     self.add_output("mesh_y_scaled", copy_shape="mesh_y")
    #     self.add_output("semi_span_ref", val=0.0, units="m")  # reference half-span (diagnostic)

    #     self.declare_partials("*", "*", method="cs")

    # def compute(self, inputs, outputs):
    #     raw_y = inputs["mesh_y"].ravel()
    #     desired_span = float(inputs["wing_span"])

    #     # determine reference span in the mesh:
    #     ymax = np.max(np.abs(raw_y))

        # decide if mesh contains only half-wing (non-negative Ys)
        # if np.all(raw_y >= 0.0):
        #     # mesh lists +Y only → reference half-span = ymax
        #     ref_half_span = ymax
        # else:
        #     # mesh contains +/-Y → reference half-span = ymax
        #     ref_half_span = ymax

        # # scaling factor to map reference half-span -> desired half-span
        # desired_half_span = desired_span / 2.0
        # if ref_half_span <= 0:
        #     scale = 1.0
        # else:
        #     scale = desired_half_span / ref_half_span

        # outputs["mesh_y_scaled"] = raw_y * scale
        # outputs["semi_span_ref"] = ref_half_span


# geom-start
class GeometryParametrizationComp(om.ExplicitComponent):
    def setup(self):
        # Input variables
        self.add_input("yles_in", shape_by_conn=True, desc="Baseline y leading edge coordinates")
        self.add_input("root_chord", val=3.0, desc="Baseline y leading edge coordinates")
        self.add_input("c/4_sweep", val=15.0, desc="shear Sweep")
        self.add_input("taper_ratio", val=0.6, desc="taper ratio of the wing") #Ma et al 2025
        self.add_input("dihedral", val=1.5, desc="dihedral of wing") #Ma et al 2025
        self.add_input("aspect_ratio", val=19.55, desc="wing aspect ratio") 
        self.add_input("wing_span", val=55.0, desc="wing aspect ratio") #m, https://www.boeing.com/content/dam/boeing/boeingdotcom/features/innovation-quarterly/2023/11/X-66A_Q4_2023.pdf

        # Output variables
        self.add_output("xles_out", copy_shape="yles_in", desc="Transformed xyz leading edge coordinates")
        self.add_output("zles_out", copy_shape="yles_in", desc="Transformed xyz leading edge coordinates")
        self.add_output("chords_out", copy_shape="yles_in", desc="Transformed chord array")

        # Finite difference partials
        self.declare_partials("*", "*", method="cs")

    def compute(self, inputs, outputs):
        # Extracting input values
        yles = inputs["yles_in"]
        chord_root = inputs["root_chord"]
        tr = inputs["taper_ratio"]
        span = inputs["wing_span"]

        relative_span = yles / span
        
        chords = ((tr - 1) * relative_span + 1) * chord_root

        zles = inputs["dihedral"] * relative_span

        # do some math to figure out the quarter chord sweeep
        outputs["xles_out"] = inputs["c/4_sweep"] * relative_span + (chord_root - chords) / 4
        outputs["zles_out"] = zles
        outputs["chords_out"] = chords


# geom-end


# mass-start
class MassProperties(om.ExplicitComponent):
    # compute the new estimated center of gravity
    # the weight of each section is proportional to the planform area

    def initialize(self):
        self.options.declare("density", types=float, default=1.0, desc="volume density of building material in kg/m**3")

    def setup(self):
        # input variables
        self.add_input("xles", shape_by_conn=True, desc="Baseline x leading edge coordinates", units="m")
        self.add_input("yles", shape_by_conn=True, desc="Baseline y leading edge coordinates", units="m")
        self.add_input("chords", shape_by_conn=True, desc="chord distribution", units="m")

        self.add_output("x_cg", desc="x postion of the CG in the same axis as the xles coordinate", units="m")
        self.add_output("weight", desc="estimated weight of the airplane", units="N")
        self.add_output("area", desc="planform area", units="m**2")

        # Finite difference partials
        self.declare_partials("*", "*", method="cs")

    def compute(self, inputs, outputs):
        xles = inputs["xles"]
        yles = inputs["yles"]
        chords = inputs["chords"]

        density = self.options["density"]
        g = 9.81  # acceleration due to gravity

        k = 0.680883333333  # areea of a NACA 4 digit airfoil for unit chord divied by thickness from http://louisgagnon.com/scBlog/airfoilCenter.html
        t = 0.12  # thicknes of airfoil
        f = 0.4  # approximate centroid of an airfoil
        # area is  t*c = 0.680883333333*(0.12*c)*c

        # we are going to find the mass, and center of mass for each of the wing sections
        # we assume that the wing is of uniform density
        x_cg = 0
        mass = 0
        xcg_numerator = 0
        planform_area = 0
        for idx in range(len(xles) - 1):
            x1 = xles[idx]
            y1 = yles[idx]
            c1 = chords[idx]

            x2 = xles[idx + 1]
            y2 = yles[idx + 1]
            c2 = chords[idx + 1]
            dy = y2 - y1

            planform_area += 0.5 * (c1 + c2) * dy  # area of trapizoid

            s = (c2 - c1) / dy  # change in chord per span

            mass += density * k * t * (s**2 * dy**3 / 3 + s * c1 * dy**2 + c1**2 * dy)

            m = (x2 - x1) / dy  # change in xles per span

            A = m + f * s
            B = x1 + f * c1

            xcg_numerator += (
                density
                * t
                * k
                * (
                    A / 4 * s**2 * dy**4
                    + 2 * A / 3 * s * c1 * dy**3
                    + A / 2 * c1**2 * dy**2
                    + B / 3 * s**2 * dy**3
                    + 2 * B / 2 * s * c1 * dy**2
                    + B * c1**2 * dy
                )
            )

        x_cg = xcg_numerator / mass

        if not self.under_approx:
            print("Weight ", mass * g, "x_cg", x_cg)

        outputs["weight"] = mass * g
        outputs["x_cg"] = x_cg
        outputs["area"] = planform_area


# mass-end
# glide-start
class SteadyPoweredFlight(om.ExplicitComponent):
    """
    Computes airspeed, lift-to-drag ratio, and flight time for
    steady powered level flight at a given altitude.
    """
    def setup(self):
        self.add_input("weight", desc="weight of the aircraft", units="N")
        self.add_input("CL", desc="lift coefficient")
        self.add_input("CD", desc="drag coefficient")
        self.add_input("Sref", desc="planform area", units="m**2")
        self.add_input("altitude", val=11430.0, desc="flight altitude", units="m")
        self.add_input("rho_air", val=0.364, desc="air density at altitude", units="kg/m**3")  # approx at 11.43 km
        self.add_input("c", val=343, desc="speed of sound", units ="m/s")  # approx at 11.43 km
        self.add_input("mach", val=0.9, desc="mach")

        # optional: thrust or fuel flow inputs if you want fuel burn
        # self.add_input("thrust", val=0.0, units="N")

        self.add_output("airspeed", desc="steady level flight airspeed", units="m/s")
        self.add_output("L_to_D", desc="lift-to-drag ratio")
        self.add_output("power_required", desc="power required to maintain level flight", units="W")

        self.declare_partials("*", "*", method="cs")

    def compute(self, inputs, outputs):
        W = inputs["weight"]
        CL = inputs["CL"]
        CD = inputs["CD"]
        S = inputs["Sref"]
        rho = inputs["rho_air"]
        c = inputs["c"]
        M = inputs["mach"]

        # Compute steady level flight speed: lift = weight
        V = M * c
        V = np.sqrt(2 * W / (rho * S * CL))

        # Compute lift-to-drag ratio
        L_to_D = CL / CD

        # Power required (thrust * velocity)
        D = 0.5 * rho * V**2 * S * CD
        power_req = D * V  # in Watts
    

        # Output
        outputs["airspeed"] = V
        outputs["L_to_D"] = L_to_D
        outputs["power_required"] = power_req

        if not hasattr(self, "under_approx") or not self.under_approx:
            print("Airspeed:", V, "L/D:", L_to_D, "Power:", power_req/1e3, "Lift Coefficient:", CL, "Drag Coefficient", CD)


# glide-end

model = om.Group()
geom_dvs = model.add_subsystem("geom_dvs", om.IndepVarComp())

geom_dvs.add_output("aincs", shape_by_conn=True)
geom_dvs.add_output("aspect_ratio", val=19.55)
geom_dvs.add_output("wing_span", val=55.0, units="m") #scale
geom_dvs.add_output("taper_ratio", val=0.6)
geom_dvs.add_output("root_chord", val=3.0) #meters
#geom_dvs.add_output("dihedral", val=-1.5)


model.connect("geom_dvs.aincs", "ovlsolver.Wing:aincs")
model.connect("geom_dvs.aspect_ratio", "geom_param.aspect_ratio")
model.connect("geom_dvs.taper_ratio", "geom_param.taper_ratio")
model.connect("geom_dvs.root_chord",    "geom_param.root_chord")
#model.connect("geom_dvs.dihedral",     "geom_param.dihedral")

model.add_subsystem("mesh", OVLMeshReader(geom_file='/Users/yasmin/git/mae298-zaman/OptVL/examples/rectangle.avl'))
model.add_subsystem("geom_param", GeometryParametrizationComp())
model.connect("mesh.Wing:yles", ["geom_param.yles_in"])

# assuming composite from vani
model.add_subsystem("mass_props", MassProperties(density=1522.0)) 
model.connect("geom_param.xles_out", ["mass_props.xles"])
model.connect("mesh.Wing:yles", ["mass_props.yles"])
model.connect("geom_param.chords_out", ["mass_props.chords"])

#model.add_subsystem("scale_y", ScaleYComp()) #scale
#model.connect("geom_dvs.wing_span", "scale_y.wing_span") #scale
#model.connect("mesh.Wing:yles", "scale_y.mesh_y") #scale


model.add_subsystem(
    "ovlsolver",
    OVLGroup(
        geom_file='/Users/yasmin/git/mae298-zaman/OptVL/examples/rectangle.avl',
        output_stability_derivs=True,
        write_grid=True,
        input_param_vals=True,
        input_ref_vals=True,
        output_dir="opt_output_sweep",
    ),
)
model.connect("geom_param.xles_out", ["ovlsolver.Wing:xles"])
model.connect("geom_param.zles_out", ["ovlsolver.Wing:zles"])
model.connect("geom_param.chords_out", ["ovlsolver.Wing:chords"])
model.connect("mass_props.x_cg", ["ovlsolver.X cg"])
model.connect("mass_props.area", ["ovlsolver.Sref"])

model.add_subsystem("flight", SteadyPoweredFlight())
model.connect("mass_props.weight", ["flight.weight"])
model.connect("mass_props.area", ["flight.Sref"])
model.connect("ovlsolver.CL", ["flight.CL"])
model.connect("ovlsolver.CD", ["flight.CD"])

model.add_subsystem("differ_aincs", Differencer())
model.connect("geom_dvs.aincs", "differ_aincs.input_vec")

# design variables modify the planform and twist distribution
#model.add_design_var("geom_param.taper_ratio", lower=0.1, upper=2.0)
#model.add_design_var("geom_param.root_chord", lower=0.5, upper=5.0)
model.add_design_var("ovlsolver.Wing:aincs", lower=-30, upper=30)
model.add_design_var("geom_param.c/4_sweep", lower=-5.0, upper=35.0)
model.add_design_var("geom_param.dihedral", lower=-2.0, upper=2.0)
#model.add_design_var("geom_param.wing_span", lower=30.0, upper=60.0)
#model.add_design_var("geom_param.aspect_ratio", lower=16, upper=25.0)

#model.add_constraint("ovlsolver.Cm", equals=0.0, scaler=1e2)
#model.add_constraint("ovlsolver.static margin", upper=0.5, lower=0.1, scaler=1e1)


# this spiral parameter makes the problem harder to solve but more realistic
#model.add_constraint("ovlsolver.spiral parameter", lower=1.0, scaler=1e0)

# you can optionally add dihedral as a design variable too
#model.add_design_var("geom_param.dihedral", lower=0.0, upper=-1.5)

# make sure CL stays slightly positive to avoid
model.add_constraint("ovlsolver.CL", lower=0.1, scaler=1)


# Some variables (like chord, dihedral, x and z leading edge position) can lead to local minimum.
# To help fix this add a constraint that keeps the variable monotonic
model.add_constraint("differ_aincs.diff_vec", upper=0.0, linear=True)  # twist can only decrease

#force area to match aspect ratio
#model.add_constraint("mass_props.area", upper="mass_props.area_target", linear=True)


# scale down the l/d
# negative scaler because the optimizer only minimizes
model.add_objective("flight.L_to_D", scaler=-1/20)

prob = om.Problem(model)


prob.driver = om.pyOptSparseDriver()
prob.driver.options["optimizer"] = "IPOPT"
prob.driver.options["debug_print"] = ["desvars", "ln_cons", "nl_cons", "objs"]
#prob.driver.options["atol"] = 1e-3
prob.driver.opt_settings["max_iter"] = 100
#prob.driver.options["disp"] = True


prob.driver.add_recorder(om.SqliteRecorder("opt_history.sql"))


prob.driver.recording_options["includes"] = ["*"]
prob.driver.recording_options["record_objectives"] = True
prob.driver.recording_options["record_constraints"] = True
prob.driver.recording_options["record_desvars"] = True

prob.model.approx_totals(method='fd', step=1e-4)

prob.setup(mode="rev")
prob.run_driver()
om.n2(prob, show_browser=False, outfile="vlm_opt.html")

prob.model.linear_solver = om.ScipyKrylov()

prob.model.nonlinear_solver = om.NewtonSolver()
prob.model.nonlinear_solver.options["solve_subsystems"] = True
prob.model.nonlinear_solver.options["maxiter"] = 200
prob.model.nonlinear_solver.options["atol"] = 1e-6
prob.model.nonlinear_solver.options["rtol"] = 1e-3

prob.setup(force_alloc_complex=True)
prob.run_model()
# prob.check_totals(
#     method='cs',
#     step=1e-4,
#     rtol=1e-3,
#     atol=1e-12,
# )
prob.check_totals()


# RESULTS 

cr = om.CaseReader("./planformopt_out/opt_history.sql")
driver_cases = cr.list_cases("driver", out_stream=None)
obj_arr = np.zeros(len(driver_cases))
for idx_case in range(len(driver_cases)):
    obj_arr[idx_case] = cr.get_case(driver_cases[idx_case])["flight.L_to_D"]

plt.plot(obj_arr)
plt.xlabel("iteration")
plt.ylabel("duration [s]")
plt.show()

# search the output directory for the latest file with a .dat extension
# Use glob to find all .dat files in the given directory
output_dir = "opt_output_sweep"
files = glob.glob(os.path.join(output_dir, "*.avl"))

# Find the .dat file with the latest modification time
latest_file = max(files, key=os.path.getmtime)

ovl = OVLSolver(geo_file=latest_file)

ovl.plot_geom()

ovl.execute_run()


strip_data = ovl.get_strip_forces()


# Create a figure and two subplots that share the x-axis
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))


for surf_key in strip_data:
    span_distance = strip_data[surf_key]["Y LE"]
    ax1.plot(span_distance, strip_data[surf_key]["chord"], color="blue", label="chord")
    ax1.plot(span_distance, strip_data[surf_key]["twist"], color="red", label="twist")
    ax2.plot(span_distance, strip_data[surf_key]["lift dist"], color="C0", label="list dist")

ax1.legend(["chord", "twist"])
ax2.legend(["lift dist"])
ax2.set_xlabel("span location")
plt.show()