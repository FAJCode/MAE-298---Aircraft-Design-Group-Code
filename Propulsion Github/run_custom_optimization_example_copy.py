"""
This is an example of running constrained optimization in Aviary using the "level 2" API. It runs
the same aircraft and mission as the level1_example.py script, but it uses the AviaryProblem class
to set up the problem.

The same ".csv" file is used to define the aircraft, but wing area and engine scale factor are added
as design variables. Then, wing loading and thrust-to-weight ratio are constrained to arbitrary
limits. If this example is run without these constraints, wing area is increased to its upper bound
and engine scale factor is reduced to its lower bound.
"""

# from aviary.models.missions.height_energy_default import phase_info
import aviary.api as av

# Suppress outputs
prob = av.AviaryProblem(verbosity=0)

# Minimum cruise speed Mach ≥ 0.76
# Assume ISA conditions, fuel reserves of 5% + 45-min hold at 1,500 ft, and taxi fuel for 15 min
# our design must achieve at least a 15% reduction in fuel burn or lifecycle CO₂ emissions per
# passenger-mile, relative to the baseline aircraft.

mission_distance = 3000.0  # nmi

phase_info = {
    'pre_mission': {'include_takeoff': False, 'optimize_mass': True},

    'climb': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 10,
            'order': 3,
            'mach_optimize': True,
            'mach_polynomial_order': 1,
            'mach_initial': (0.21, 'unitless'),
            'mach_bounds': ((0.20, 0.88), 'unitless'),
            'altitude_optimize': True,
            'altitude_polynomial_order': 1,
            'altitude_initial': (0.0, 'ft'),
            'altitude_bounds': ((0.0, 40000.0), 'ft'),
            'throttle_enforcement': 'path_constraint',
            'time_initial_bounds': ((0.0, 0.0), 'min'),
            'time_duration_bounds': ((12.1, 180.0), 'min'),
            'no_descent': True,
        },
        'initial_guesses': {
            'time': ([0, 60.0], 'min'),
            # 'altitude': ([35,37000.0], 'ft'),
            # 'mach': ([0.21, 0.76], 'unitless'),
        },
    },

    'cruise': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 5,
            'order': 3,
            'mach_optimize': True,
            'mach_polynomial_order': 1,
            # 'mach_initial': (0.76, 'unitless'),
            'mach_bounds': ((0.76, 0.88), 'unitless'),
            'altitude_optimize': True,
            'altitude_polynomial_order': 1,
            'altitude_bounds': ((36000.0, 40000.0), 'ft'),
            'throttle_enforcement': 'boundary_constraint',
            'time_initial_bounds': ((95.0, 260.0), 'min'),
            'time_duration_bounds': ((55.5, 410.5), 'min'),
            'no_descent': True,
        },
        'initial_guesses': {
            'time': ([70, 193], 'min'),
            # 'altitude': ([37000.0, 37000.0], 'ft'),
            # 'mach': ([0.76, 0.76], 'unitless'),
        },
    },

    'descent': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 10,
            'order': 3,
            'mach_optimize': True,
            'mach_polynomial_order': 1,
            # 'mach_initial': (0.76, 'unitless'),
            'mach_final': (0.21, 'unitless'),
            'mach_bounds': ((0.20, 0.88), 'unitless'),
            'altitude_optimize': True,
            'altitude_polynomial_order': 1,
            # 'altitude_initial': (37000.0, 'ft'),
            'altitude_final': (0.0, 'ft'),
            'altitude_bounds': ((0.0, 40000.0), 'ft'),
            'throttle_enforcement': 'path_constraint',
            'time_initial_bounds': ((20.5, 50.5), 'min'),
            'time_duration_bounds': ((20.0, 80.0), 'min'),
            'no_climb': True,
        },
        # 'initial_guesses': {'time': ([50, 273], 'min')},
    },

    'post_mission': {
        'include_landing': True,
        'constrain_range': True,
        'target_range': (mission_distance, 'nmi'),
    },
}

# Load aircraft and options data from provided sources
# prob.load_inputs('models/aircraft/test_aircraft/aircraft_for_bench_FwFm.csv', phase_info)
# prob.load_inputs('models/aircraft/advanced_single_aisle/advanced_single_aisle_FLOPS.csv', phase_info)
prob.load_inputs('advanced_single_aisle_FLOPS_copy.csv', phase_info)

prob.check_and_preprocess_inputs()
prob.add_pre_mission_systems()
prob.add_phases()
prob.add_post_mission_systems()
prob.link_phases()

# Optimizer and iteration limit are optional provided here
prob.add_driver('IPOPT', max_iter=50)

# Add the default design variables needed to size the aircraft
prob.add_design_variables()

# Add wing area and engine scaling as additional design variables
prob.model.add_design_var(av.Aircraft.Engine.SCALE_FACTOR, lower=0.9, upper=1.3, ref=1)
# prob.model.add_design_var(av.Aircraft.Wing.AREA, lower=1200, upper=1800, units='ft**2', ref=1370)
prob.model.add_design_var(av.Aircraft.Engine.WING_LOCATIONS, lower=0.2, upper=0.4, ref=0.27)
# prob.model.add_design_var(av.Aircraft.Engine.MASS, lower=5000, upper=8000.0, ref=6293.8, units='lbm')

prob.add_objective('fuel_burned')

# Constraints
# prob.model.add_constraint(av.Aircraft.Design.WING_LOADING, lower=120, units='lbf/ft**2')
# prob.model.add_constraint(av.Aircraft.Design.THRUST_TO_WEIGHT_RATIO, lower=0.26, upper=0.37, ref=0.3)

prob.model.add_constraint(av.Aircraft.Propulsion.TOTAL_SCALED_SLS_THRUST,lower=40000, upper=58000, ref=44400, units="lbf")
prob.model.add_constraint(av.Aircraft.Engine.MASS, lower=6500, upper=8000.0)
# What I am saying is that there is no way in hell that the mass could be less than the baseline.
prob.model.add_constraint(av.Aircraft.Engine.MASS_SCALER, lower=1.2, upper=1.4)
prob.model.add_constraint(av.Aircraft.Nacelle.WETTED_AREA_SCALER, lower=1.15, upper=1.35)

prob.setup()
prob.set_val('target_range', 3000.0, units='nmi')

# prob.set_val('av.Aircraft.Engine.SCALE_FACTOR', 1.0)
# prob.set_val('av.Aircraft.Engine.WING_LOCATIONS', 0.27)

prob.run_aviary_problem()

fuel_burn = prob.get_val(av.Mission.Summary.FUEL_BURNED, units='lbm')

print(f'\nTakeoff Gross Weight = {prob.get_val(av.Mission.Summary.GROSS_MASS, units="lbm")} lbm')

print('\nDesign Variables\n---------------')
print(f'Engine Scale Factor (started at 1) = {prob.get_val(av.Aircraft.Engine.SCALE_FACTOR)}')
print(f'Engine Location (started at 0.27) = {prob.get_val(av.Aircraft.Engine.WING_LOCATIONS)}')

print('\nConstraints\n-----------')
print("Total Mission Fuel Burn =", fuel_burn)

# print(f'Wing Area (started at 1370) = {prob.get_val(av.Aircraft.Wing.AREA, units="ft**2")} ft^2')
# print(f'Wing Loading = {prob.get_val(av.Aircraft.Design.WING_LOADING, units="lbf/ft**2")} lbf/ft^2')
# print(f'Thrust/Weight Ratio = {prob.get_val(av.Aircraft.Design.THRUST_TO_WEIGHT_RATIO)}')
