"""Run the a mission with a simple external component that computes the wing and horizontal tail mass."""

from copy import deepcopy

import aviary.api as av
from aviary.examples.external_subsystems.custom_aero.custom_lift_builder import LiftDragBuilder

mission_distance = 3000.0

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
                'throttle_enforcement': 'path_constraint', #'path_constraint',
                'time_initial_bounds': ((0.0, 0.0), 'min'),
                'time_duration_bounds': ((12.1, 180.0), 'min'), #Was 160
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
                'time_initial_bounds': ((95.0, 260.0), 'min'), #### Check if this time makes sense
                'time_duration_bounds': ((55.5, 410.5), 'min'), #was 410
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
                'throttle_enforcement': 'path_constraint', #'path_constraint',
                'time_initial_bounds': ((20.5, 50.5), 'min'), #Check if this makes sense
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
# Here we just add the simple weight system to only the pre-mission
phase_info['pre_mission']['external_subsystems'] = [LiftDragBuilder()]

if __name__ == '__main__':
    prob = av.AviaryProblem()

    # Load aircraft and options data from user
    # Allow for user overrides here
    prob.load_inputs('Aviary/aviary/models/aircraft/advanced_single_aisle/advanced_single_aisle_FLOPS.csv', phase_info)

    prob.check_and_preprocess_inputs()

    prob.build_model()

    prob.add_driver('IPOPT', max_iter=200)

    prob.add_design_variables()

    prob.add_objective()

    prob.setup()

    prob.run_aviary_problem(suppress_solver_print=True)

    print('Lift Coefficient', prob.get_val(av.Aircraft.Wing.HIGH_LIFT_MASS_COEFFICIENT))

    print('done')
