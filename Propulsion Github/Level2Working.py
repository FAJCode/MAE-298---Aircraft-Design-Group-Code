import numpy as np
import matplotlib.pyplot as plt
import aviary.api as av

# ==========================================
# CONFIGURATION
# ==========================================
# Make sure your CSV file is in the same folder!
input_file = 'advanced_single_aisle_FLOPS_copy.csv' 

# Ranges for the sweeps
loc_sweep_values = np.linspace(0.2, 0.4, 10)   # Sweep Location from 0.2 to 0.4
scale_sweep_values = np.linspace(0.9, 1.3, 10) # Sweep Scale from 0.9 to 1.3

# Storage for results
res_loc_sweep = {'x': [], 'fuel': [], 'opt_scale': []}
res_scale_sweep = {'x': [], 'fuel': [], 'opt_loc': []}

# Define the Mission (Reusable Function)
def get_phase_info():
    mission_distance = 3000.0
    return {
        'pre_mission': {'include_takeoff': False, 'optimize_mass': True},
        'climb': {
            'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
            'user_options': {
                'num_segments': 10, 'order': 3, 'mach_optimize': True, 'mach_polynomial_order': 1,
                'mach_initial': (0.21, 'unitless'), 'mach_bounds': ((0.20, 0.88), 'unitless'),
                'altitude_optimize': True, 'altitude_polynomial_order': 1,
                'altitude_initial': (0.0, 'ft'), 'altitude_bounds': ((0.0, 40000.0), 'ft'),
                'throttle_enforcement': 'path_constraint', 'time_initial_bounds': ((0.0, 0.0), 'min'),
                'time_duration_bounds': ((12.1, 180.0), 'min'), 'no_descent': True,
            },
            'initial_guesses': {'time': ([0, 60.0], 'min')},
        },
        'cruise': {
            'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
            'user_options': {
                'num_segments': 5, 'order': 3, 'mach_optimize': True, 'mach_polynomial_order': 1,
                'mach_bounds': ((0.76, 0.88), 'unitless'), 'altitude_optimize': True,
                'altitude_polynomial_order': 1, 'altitude_bounds': ((36000.0, 40000.0), 'ft'),
                'throttle_enforcement': 'boundary_constraint', 'time_initial_bounds': ((95.0, 260.0), 'min'),
                'time_duration_bounds': ((55.5, 410.5), 'min'), 'no_descent': True,
            },
            'initial_guesses': {'time': ([70, 193], 'min')},
        },
        'descent': {
            'subsystem_options': {'core_aerodynamics': {'method': 'computed'}},
            'user_options': {
                'num_segments': 10, 'order': 3, 'mach_optimize': True, 'mach_polynomial_order': 1,
                'mach_final': (0.21, 'unitless'), 'mach_bounds': ((0.20, 0.88), 'unitless'),
                'altitude_optimize': True, 'altitude_polynomial_order': 1,
                'altitude_final': (0.0, 'ft'), 'altitude_bounds': ((0.0, 40000.0), 'ft'),
                'throttle_enforcement': 'path_constraint', 'time_initial_bounds': ((20.5, 50.5), 'min'),
                'time_duration_bounds': ((20.0, 80.0), 'min'), 'no_climb': True,
            },
        },
        'post_mission': {
            'include_landing': True, 'constrain_range': True, 'target_range': (mission_distance, 'nmi'),
        },
    }

# ==========================================
# EXPERIMENT 1: VARY LOCATION (Fixed), OPTIMIZE SCALE
# ==========================================
print(f"\nRunning Experiment 1: Sweeping Location...")
print(f"{'Location':<10} | {'Fuel Burn':<10} | {'Opt Scale'}")
print("-" * 35)

for loc in loc_sweep_values:
    prob = av.AviaryProblem(verbosity=0)
    prob.load_inputs(input_file, get_phase_info())
    prob.check_and_preprocess_inputs()
    prob.add_pre_mission_systems()
    prob.add_phases()
    prob.add_post_mission_systems()
    prob.link_phases()
    prob.add_driver('IPOPT', max_iter=50)
    prob.add_design_variables()
    
    # --- SETUP VARIABLES FOR EXP 1 ---
    # Design Variable: SCALE IS FREE
    prob.model.add_design_var(av.Aircraft.Engine.SCALE_FACTOR, lower=0.9, upper=1.4, ref=1)
    # LOCATION IS NOT A DESIGN VAR (We will force it)
    
    prob.add_objective('fuel_burned')
    prob.model.add_constraint(av.Aircraft.Propulsion.TOTAL_SCALED_SLS_THRUST, lower=40000, upper=58000)
    prob.model.add_constraint(av.Aircraft.Engine.MASS, lower=6500, upper=8000.0)
    
    prob.setup()
    
    # Force Location Value
    prob.set_val(av.Aircraft.Engine.WING_LOCATIONS, loc)
    prob.set_val('target_range', 3000.0, units='nmi')

    try:
        prob.run_aviary_problem()
        fb = prob.get_val(av.Mission.Summary.FUEL_BURNED, units='lbm')[0]
        opt_s = prob.get_val(av.Aircraft.Engine.SCALE_FACTOR)[0]
        res_loc_sweep['x'].append(loc)
        res_loc_sweep['fuel'].append(fb)
        res_loc_sweep['opt_scale'].append(opt_s)
        print(f"{loc:<10.2f} | {fb:<10.0f} | {opt_s:.4f}")
    except:
        print(f"{loc:<10.2f} | FAILED")

# ==========================================
# EXPERIMENT 2: VARY SCALE (Fixed), OPTIMIZE LOCATION
# ==========================================
print(f"\nRunning Experiment 2: Sweeping Scale Factor...")
print(f"{'Scale':<10} | {'Fuel Burn':<10} | {'Opt Location'}")
print("-" * 35)

for scale in scale_sweep_values:
    prob = av.AviaryProblem(verbosity=0)
    prob.load_inputs(input_file, get_phase_info())
    prob.check_and_preprocess_inputs()
    prob.add_pre_mission_systems()
    prob.add_phases()
    prob.add_post_mission_systems()
    prob.link_phases()
    prob.add_driver('IPOPT', max_iter=50)
    prob.add_design_variables()
    
    # --- SETUP VARIABLES FOR EXP 2 ---
    # Design Variable: LOCATION IS FREE
    prob.model.add_design_var(av.Aircraft.Engine.WING_LOCATIONS, lower=0.2, upper=0.4, ref=0.27)
    # SCALE IS NOT A DESIGN VAR (We will force it)
    
    prob.add_objective('fuel_burned')
    prob.model.add_constraint(av.Aircraft.Propulsion.TOTAL_SCALED_SLS_THRUST, lower=40000, upper=58000)
    prob.model.add_constraint(av.Aircraft.Engine.MASS, lower=6500, upper=8000.0)

    prob.setup()
    
    # Force Scale Value
    prob.set_val(av.Aircraft.Engine.SCALE_FACTOR, scale)
    prob.set_val('target_range', 3000.0, units='nmi')

    try:
        prob.run_aviary_problem()
        fb = prob.get_val(av.Mission.Summary.FUEL_BURNED, units='lbm')[0]
        opt_l = prob.get_val(av.Aircraft.Engine.WING_LOCATIONS)[0]
        res_scale_sweep['x'].append(scale)
        res_scale_sweep['fuel'].append(fb)
        res_scale_sweep['opt_loc'].append(opt_l)
        print(f"{scale:<10.2f} | {fb:<10.0f} | {opt_l:.4f}")
    except:
        print(f"{scale:<10.2f} | FAILED")

# ==========================================
# PLOTTING
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Fuel vs Location
if len(res_loc_sweep['x']) > 0:
    ax1.plot(res_loc_sweep['x'], res_loc_sweep['fuel'], 'bo-', label='Fuel Burn')
    ax1.set_xlabel('Engine Spanwise Location')
    ax1.set_ylabel('Fuel Burn (lbm)')
    ax1.set_title('Sensitivity: Fuel vs Location\n(Scale Optimized)')
    ax1.grid(True)

# Plot 2: Fuel vs Scale
if len(res_scale_sweep['x']) > 0:
    ax2.plot(res_scale_sweep['x'], res_scale_sweep['fuel'], 'ro-', label='Fuel Burn')
    ax2.set_xlabel('Engine Scale Factor')
    ax2.set_ylabel('Fuel Burn (lbm)')
    ax2.set_title('Sensitivity: Fuel vs Scale Factor\n(Location Optimized)')
    ax2.grid(True)

plt.tight_layout()
plt.show()