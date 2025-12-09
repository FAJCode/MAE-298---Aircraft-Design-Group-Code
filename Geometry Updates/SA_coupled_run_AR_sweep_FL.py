#File for testing phases and 2DOF
import os
#Cloned aviary repo location
#from aviary.models.missions.height_energy_default import phase_info
import aviary.api as av


# # === Choose your output directory here ===
output_dir = r"/Users/carissa/Desktop/Aircraft/mae298-kamm/output_files"  # <-- change this
os.makedirs(output_dir, exist_ok=True)
os.chdir(output_dir)  # all Aviary output files will now be saved here

import openmdao.api as om
import numpy as np

# ====== Adding Span Calculation as explicit component
class SpanFromAspectRatio(om.ExplicitComponent):
    def setup(self):
        self.add_input('aspect_ratio', units=None)
        self.add_input('wing_area', units='m**2')

        self.add_output('span', units='m')

        self.declare_partials(of='span', wrt='aspect_ratio')
        self.declare_partials(of='span', wrt='wing_area')

    def compute(self, inputs, outputs):
        AR = inputs['aspect_ratio']
        S = inputs['wing_area']
        outputs['span'] = np.sqrt(AR * S)

    def compute_partials(self, inputs, J):
        AR = inputs['aspect_ratio']
        S = inputs['wing_area']
        root = np.sqrt(AR * S)

        J['span', 'aspect_ratio'] = 0.5 * S / root
        J['span', 'wing_area']   = 0.5 * AR / root

# ===== Define mission phases
mission_distance = 3000.0  # nmi

phase_info = {
    'pre_mission': {'include_takeoff': False, 'optimize_mass': True},
    'climb_1': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 5,
            'order': 3,
            'mach_optimize': False,
            'mach_polynomial_order': 1,
            'mach_initial': (0.2, 'unitless'),
            'mach_final': (0.72, 'unitless'),
            'mach_bounds': ((0.18, 0.84), 'unitless'),
            'altitude_optimize': False,
            'altitude_polynomial_order': 1,
            'altitude_initial': (0.0, 'ft'),
            'altitude_final': (33000.0, 'ft'),
            'altitude_bounds': ((0.0, 35000.0), 'ft'),
            'throttle_enforcement': 'path_constraint',
            'time_initial_bounds': ((0.0, 0.0), 'min'),
            'time_duration_bounds': ((25.0, 55.0), 'min'),
        },
        'initial_guesses': {'time': ([0, 80], 'min')},
    },
    'cruise': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 5,
            'order': 3,
            'mach_optimize': False,
            'mach_polynomial_order': 1,
            'mach_initial': (0.72, 'unitless'),
            'mach_final': (0.78, 'unitless'),
            'mach_bounds': ((0.7, 0.84), 'unitless'),
            'altitude_optimize': False,
            'altitude_polynomial_order': 1,
            'altitude_initial': (33000.0, 'ft'),
            'altitude_final': (35000.0, 'ft'),
            'altitude_bounds': ((33000.0, 35000.0), 'ft'),
            'throttle_enforcement': 'boundary_constraint',
            'time_initial_bounds': ((95.0, 260.0), 'min'), #### Check if this time makes sense
            'time_duration_bounds': ((55.5, 410.5), 'min'),
        },
        'initial_guesses': {'time': ([70, 193], 'min')},
    },
    'descent_1': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 5,
            'order': 3,
            'mach_optimize': False,
            'mach_polynomial_order': 1,
            'mach_initial': (0.78, 'unitless'),
            'mach_final': (0.21, 'unitless'),
            'mach_bounds': ((0.19, 0.84), 'unitless'),
            'altitude_optimize': False,
            'altitude_polynomial_order': 1,
            'altitude_initial': (35000.0, 'ft'),
            'altitude_final': (0.0, 'ft'),
            'altitude_bounds': ((0.0, 35500.0), 'ft'),
            'throttle_enforcement': 'path_constraint',
            'time_initial_bounds': ((25.5, 50.5), 'min'), #Check if this makes sense
            'time_duration_bounds': ((25.0, 55.0), 'min'),
        },
        'initial_guesses': {'time': ([273, 50], 'min')},
    },
    'post_mission': {
        'include_landing': False,
        'constrain_range': True,
        'target_range': (3000, 'nmi'), #2860 is the limit
    },
}


#==== Set up and run Aviary problem ====

aircraft_filename =  'aviary/models/aircraft/advanced_single_aisle_new/advanced_single_aisle_FLOPS.csv' #'models/aircraft/test_aircraft/aircraft_for_bench_FwFm.csv'
optimizer = 'IPOPT'  #'SLSQP'
make_plots = True
max_iter = 100

prob = av.AviaryProblem()

# Load aircraft and options data from user
# Allow for user overrides here
prob.load_inputs(aircraft_filename, phase_info)

# ===== add span calc as subsystem
'''
prob.add_subsystem(
    'span_from_AR',
    SpanFromAspectRatio(),
    promotes_inputs=[('aspect_ratio', av.Aircraft.Wing.ASPECT_RATIO),
                     ('wing_area',  av.Aircraft.Wing.AREA)],
    promotes_outputs=[('span', av.Aircraft.Wing.SPAN)]
)
'''
prob.check_and_preprocess_inputs()

prob.build_model()

prob.add_driver(optimizer, max_iter=max_iter)

prob.add_design_variables()

# The following line is an example of how to add a design variable for the aspect ratio of the wing

prob.model.add_design_var(av.Aircraft.Wing.ASPECT_RATIO, lower=10, upper=25, ref=20)

prob.model.add_design_var(av.Aircraft.Wing.SWEEP, lower=10.0, upper=35.0, ref=23.63)

prob.model.add_design_var(av.Aircraft.Fuselage.LENGTH, lower=120, upper=150, ref=125)


# Load optimization problem formulation
# Detail which variables the optimizer can control
prob.add_objective('fuel_burned')

prob.setup()

prob.run_aviary_problem(make_plots=make_plots)