#File for testing phases and 2DOF
#OPtimized mission analysis for

import os
#Cloned aviary repo location
#from aviary.models.missions.height_energy_default import phase_info
import aviary.api as av


# # === Choose your output directory here ===
# output_dir = r"/Users/ciscoj/Desktop/School/Davis/Grad_school/Classes_Work/Aircraft_Design/mae298-Jackson2/Output_files"  # <-- change this
# os.makedirs(output_dir, exist_ok=True)
# os.chdir(output_dir)  # all Aviary output files will now be saved here


# ===== Define mission phases
mission_distance = 3000.0  # nmi

phase_info = {
    'pre_mission': {'include_takeoff': False, 'optimize_mass': True},
    'climb_1': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 5,
            'order': 3,
            'mach_optimize': True,
            'mach_polynomial_order': 1,
            'mach_initial': (0.2, 'unitless'),
            'mach_final': (0.74, 'unitless'),
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
            'mach_optimize': True,
            'mach_polynomial_order': 1,
            'mach_initial': (0.74, 'unitless'),
            'mach_final': (0.76, 'unitless'),
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
            'mach_optimize': True,
            'mach_polynomial_order': 1,
            'mach_initial': (0.76, 'unitless'),
            'mach_final': (0.20, 'unitless'),
            'mach_bounds': ((0.18, 0.84), 'unitless'),
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
        'target_range': (mission_distance, 'nmi'), #2860 is the limit
    },
}

#==== Set up and run Aviary problem ====

aircraft_filename =  'aviary/models/aircraft/advanced_single_aisle/advanced_single_aisle_FLOPS.csv' #'models/aircraft/test_aircraft/aircraft_for_bench_FwFm.csv'
optimizer = 'IPOPT'  #'SLSQP'
make_plots = True
max_iter = 100

prob = av.run_aviary(
    aircraft_filename, phase_info, optimizer=optimizer, make_plots=make_plots, max_iter=max_iter
)