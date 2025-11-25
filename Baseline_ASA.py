#File for baseline run with Advanced Single Asile aircraft phase info 

#Cloned aviary repo location
#from aviary.models.missions.height_energy_default import phase_info
import aviary.api as av
import os

# # === Choose your output directory here ===
output_dir = r"/Users/ciscoj/Desktop/School/Davis/Grad_school/Classes_Work/Aircraft_Design/mae298-Jackson2/Result_files"  # <-- change this
os.makedirs(output_dir, exist_ok=True)
os.chdir(output_dir)  # all Aviary output files will now be saved here

# ===== Define mission phases
mission_distance = 3000.0  # nmi

phase_info = {
    'pre_mission': {'include_takeoff': False, 'optimize_mass': True},
    'climb': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 10,
            'order': 3,
                'mach_optimize': False,
                'mach_polynomial_order': 2,
                'mach_initial': (0.2, 'unitless'),
                'mach_final': (0.82, 'unitless'),
                'mach_bounds': ((0.18, 0.84), 'unitless'),
                'altitude_optimize': False,
                'altitude_polynomial_order': 2,
                'altitude_initial': (0.0, 'ft'),
                'altitude_final': (37000.0, 'ft'),
                'altitude_bounds': ((0.0, 37000.0), 'ft'),
                'throttle_enforcement': 'path_constraint', #'path_constraint',
                'time_initial_bounds': ((0.0, 0.0), 'min'),
                'time_duration_bounds': ((12.1, 130.0), 'min'),
                'no_descent': True,
        },
        'initial_guesses': {
            'time': ([0, 50.0], 'min'),
            'altitude': ([35, 37000.0], 'ft'),
            'mach': ([0.2, 0.78], 'unitless'),
        },
    },
    'cruise': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 5,
            'order': 3,
                'mach_optimize': False,
                'mach_polynomial_order': 1,
                'mach_initial': (0.80, 'unitless'),
                'mach_final': (0.80, 'unitless'),
                'mach_bounds': ((0.7, 0.84), 'unitless'),
                'altitude_optimize': False,
                'altitude_polynomial_order': 1,
                'altitude_initial': (37000.0, 'ft'),
                'altitude_final': (38000.0, 'ft'),
                'altitude_bounds': ((36000.0, 39000.0), 'ft'),
                'throttle_enforcement': 'boundary_constraint',
                'time_initial_bounds': ((95.0, 260.0), 'min'), #### Check if this time makes sense
                'time_duration_bounds': ((55.5, 410.5), 'min'),
                'no_descent': True,
            },
        'initial_guesses': {
            'time': ([70, 193], 'min'),
            'altitude': ([38000.0, 38000.0], 'ft'),
            'mach': ([0.80, 0.80], 'unitless'),
        },
    },
    'descent': {
        'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
        'user_options': {
            'num_segments': 5,
                'order': 3,
                'mach_optimize': False,
                'mach_polynomial_order': 2,
                'mach_initial': (0.80, 'unitless'),
                'mach_final': (0.21, 'unitless'),
                'mach_bounds': ((0.19, 0.84), 'unitless'),
                'altitude_optimize': False,
                'altitude_polynomial_order': 2,
                'altitude_initial': (38000.0, 'ft'),
                'altitude_final': (0.0, 'ft'),
                'altitude_bounds': ((0.0, 38500.0), 'ft'),
                'throttle_enforcement': 'path_constraint', #'path_constraint',
                'time_initial_bounds': ((25.5, 50.5), 'min'), #Check if this makes sense
                'time_duration_bounds': ((25.0, 105.0), 'min'),
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


# phase_info = {
#     'pre_mission': {'include_takeoff': False, 'optimize_mass': True},
#     'climb': {
#         'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
#         'user_options': {
#             'num_segments': 6,
#             'order': 3,
#                 'mach_optimize': True,
#                 'mach_polynomial_order': 3,
#                 'mach_bounds': ((0.18, 0.84), 'unitless'),
#                 'altitude_optimize': True,
#                 'altitude_polynomial_order': 3,
#                 'altitude_bounds': ((0.0, 38000.0), 'ft'),
#                 'throttle_enforcement': 'path_constraint', #'path_constraint',
#                 'time_initial_bounds': ((0.0, 0.0), 'min'),
#                 'time_duration_bounds': ((12.1, 115.0), 'min'),
#                 'no_descent': True,
#         },
#         'initial_guesses': {
#             'time': ([0, 60.0], 'min'),
#             'altitude': ([35, 38000.0], 'ft'),
#             'mach': ([0.2, 0.82], 'unitless'),
#         },
#     },
#     'cruise': {
#         'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
#         'user_options': {
#             'num_segments': 1,
#             'order': 3,
#                 'mach_optimize': False,
#                 'mach_polynomial_order': 1,
#                 'mach_initial': (0.82, 'unitless'),
#                 'mach_bounds': ((0.7, 0.84), 'unitless'),
#                 'altitude_optimize': False,
#                 'altitude_polynomial_order': 1,
#                 'altitude_bounds': ((37000.0, 39000.0), 'ft'),
#                 'throttle_enforcement': 'boundary_constraint',
#                 'time_initial_bounds': ((95.0, 260.0), 'min'), #### Check if this time makes sense
#                 'time_duration_bounds': ((55.5, 410.5), 'min'),
#                 'no_descent': True,
#             },
#         'initial_guesses': {
#             'time': ([70, 193], 'min'),
#             'altitude': ([38000.0, 38000.0], 'ft'),
#             'mach': ([0.82, 0.82], 'unitless'),
#         },
#     },
#     'descent': {
#         'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
#         'user_options': {
#             'num_segments': 5,
#                 'order': 3,
#                 'mach_optimize': True,
#                 'mach_polynomial_order': 3,
#                 'mach_initial': (0.82, 'unitless'),
#                 'mach_final': (0.21, 'unitless'),
#                 'mach_bounds': ((0.19, 0.84), 'unitless'),
#                 'altitude_optimize': True,
#                 'altitude_polynomial_order': 3,
#                 'altitude_initial': (38000.0, 'ft'),
#                 'altitude_final': (0.0, 'ft'),
#                 'altitude_bounds': ((0.0, 38000.0), 'ft'),
#                 'throttle_enforcement': 'path_constraint', #'path_constraint',
#                 'time_initial_bounds': ((25.5, 50.5), 'min'), #Check if this makes sense
#                 'time_duration_bounds': ((25.0, 105.0), 'min'),
#                 'no_climb': True,
#             },
#             # 'initial_guesses': {'time': ([50, 273], 'min')},
#     },
#     'post_mission': {
#         'include_landing': True,
#         'constrain_range': True,
#         'target_range': (mission_distance, 'nmi'),
#     },
# }

# ==== Build and run the problem ====
# Load aircraft and options data from provided sources
prob = av.AviaryProblem()

prob.load_inputs(
    'aviary/models/aircraft/advanced_single_aisle/advanced_single_aisle_FLOPS.csv', phase_info
)

prob.check_and_preprocess_inputs()

prob.build_model()

# optimizer and iteration limit are optional provided here
prob.add_driver('IPOPT', max_iter=100)

prob.add_design_variables()

prob.add_objective()

prob.setup()

prob.run_aviary_problem()

#Print out some variables for quick looking
print("Mission optimization complete.")
ASA_fuel_burn = prob.get_val(av.Mission.Summary.FUEL_BURNED, units='kg')[0]
ASA_wing_aspect_ratio = prob.get_val(av.Aircraft.Wing.ASPECT_RATIO)[0]
# ASA_mission_time = prob.get_val(av.Mission.Summary.MISSION_TIME, units='min')[0]

#printing them out
print('Mission fuel burn, kg:', ASA_fuel_burn)
print('Aspect ratio:', ASA_wing_aspect_ratio)
# print('Mission time, min:', ASA_mission_time)