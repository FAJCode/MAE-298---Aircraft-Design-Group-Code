#For generating carpet plots and fuel burn plot with mission profile and mach 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.graph_objects as go
from scipy.interpolate import griddata



# ==== End of general carpet plot ====


#==== Carpet plot data ====

#For the boundary of time and altitude
#Altitudes
altitudes = [36_000, 37_000, 38_000, 39_000, 40_000]  # in feet
mach_numbers = [0.74, 0.76, 0.77, 0.78, 0.79, 0.80, 0.81, 0.82, 0.84]

#fuel burn rate in lbm 
fuel_burn_data = [[20_205.43, 20_762.39, 21_852.11, 24_112.98],
                          [21_668.07, 20_594.73, 21_753.51,0],
                          [20_107.03, 20_549.67, 21_847.99,0],
                          [20_354.30, 20_747.47, 0, 0],
                          [20820.26, 21212.53,0,0]]

#Corresponding mission time in minutes
mission_time_data = [[452.175 ,445.17 ,444.37, 472.524],
                              [457.697, 451.083, 453.979, 0],
                              [465.514, 459.486, 468.112, 0],
                              [477.611, 473.001, 0, 0],
                              [493.27, 491.16, 0, 0]]

#Corresponding mission altitude in feet
altitude_data = [[36_000, 36_000, 36_000, 36_000, 36_000],
                          [37_000, 37_000, 37_000,0],
                          [38_000, 38_000, 38_000,0],
                          [39_000, 39_000, 0, 0],
                          [40_000, 40_000, 0, 0]]

#Corresponding mach numbers
mach_data = [[0.76, 0.78, 0.80, 0.82],
                      [0.76, 0.78, 0.80,0],
                      [0.76, 0.78, 0.80,0],
                      [0.76, 0.78, 0, 0],
                      [0.76, 0.78, 0, 0]]


#Optimized points 
#optimized mission profile data
optimized_mach = [0.76] #[0.76, 0.76]
optimized_altitude = [40_000] #[37_000, 38_000]
optimized_misison_time = [453.05] #[452.78, 452.73,] #in minutes
optimized_fuel_burn = [19_565.58] #[19_834.82, 19_687.61] #in lbm



#End of data for carpet plot

# ==== Generate carpet plot from data ====

# ===========================================
# ------------------------------
# Flatten and filter data for interpolation
mach_flat = []
alt_flat = []
fuel_flat = []
time_flat = []

for i in range(len(fuel_burn_data)):
    for j in range(len(fuel_burn_data[i])):
        if fuel_burn_data[i][j] != 0 and mach_data[i][j] != 0:
            mach_flat.append(mach_data[i][j])
            alt_flat.append(altitude_data[i][j])
            fuel_flat.append(fuel_burn_data[i][j])
            time_flat.append(mission_time_data[i][j])

# Create grid for interpolation
mach_grid = np.linspace(min(mach_flat), max(mach_flat), 100)
alt_grid = np.linspace(min(alt_flat), max(alt_flat), 100)
mach_mesh, alt_mesh = np.meshgrid(mach_grid, alt_grid)

# Interpolate fuel burn data
fuel_mesh = griddata((mach_flat, alt_flat), fuel_flat, (mach_mesh, alt_mesh), method='cubic')

# Interpolate mission time data
time_mesh = griddata((mach_flat, alt_flat), time_flat, (mach_mesh, alt_mesh), method='cubic')

# Create the figure
fig = go.Figure()

# Add contour plot for fuel burn
fig.add_trace(go.Contour(
    x=mach_grid,
    y=alt_grid,
    z=fuel_mesh,
    colorscale='Viridis',
    contours=dict(
        showlabels=True,
        labelfont=dict(size=10, color='white')
    ),
    colorbar=dict(
        title='Fuel Burn<br>(lbm)',
        tickfont=dict(size=12)
    ),
    hovertemplate='<b>Mach:</b> %{x:.2f}<br>' +
                  '<b>Altitude:</b> %{y:,.0f} ft<br>' +
                  '<b>Fuel Burn:</b> %{z:,.2f} lbm<br>' +
                  '<extra></extra>',
    name='Fuel Burn'
))

# Add contour lines for mission time
fig.add_trace(go.Contour(
    x=mach_grid,
    y=alt_grid,
    z=time_mesh,
    showscale=False,
    contours=dict(
        showlabels=True,
        labelfont=dict(size=9, color='black'),
        coloring='none'
    ),
    line=dict(
        color='black',
        width=2,
        dash='dash'
    ),
    hovertemplate='<b>Mach:</b> %{x:.2f}<br>' +
                  '<b>Altitude:</b> %{y:,.0f} ft<br>' +
                  '<b>Mission Time:</b> %{z:.1f} min<br>' +
                  '<extra></extra>',
    name='Mission Time (min)'
))

# Add scatter points for actual data
fig.add_trace(go.Scatter(
    x=mach_flat,
    y=alt_flat,
    mode='markers',
    marker=dict(
        size=10,
        color='white',
        line=dict(color='black', width=2)
    ),
    name='Data Points',
    hovertemplate='<b>Mach:</b> %{x:.2f}<br>' +
                  '<b>Altitude:</b> %{y:,.0f} ft<br>' +
                  '<extra></extra>'
))

# Add optimized point
fig.add_trace(go.Scatter(
    x=optimized_mach,
    y=optimized_altitude,
    mode='markers',
    marker=dict(
        size=15,
        color='lightblue',
        line=dict(color='darkblue', width=3),
        symbol='star'
    ),
    name='Optimized Point',
    hovertemplate='<b>Optimized Point</b><br>' +
                  '<b>Mach:</b> %{x:.2f}<br>' +
                  '<b>Altitude:</b> %{y:,.0f} ft<br>' +
                  '<b>Mission Time:</b> ' + f'{optimized_misison_time[0]:.2f} min<br>' +
                  '<b>Fuel Burn:</b> ' + f'{optimized_fuel_burn[0]:,.2f} lbm<br>' +
                  '<extra></extra>'
))



# Update layout
fig.update_layout(
    title={
        'text': 'Carpet Plot: Fuel Burn vs Mach Number and Altitude',
        'font': {'size': 18, 'color': '#2c3e50'},
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title=dict(text='Mach Number', font=dict(size=14, color='#2c3e50')),
        gridcolor='lightgray',
        showgrid=True
    ),
    yaxis=dict(
        title=dict(text='Altitude (ft)', font=dict(size=14, color='#2c3e50')),
        gridcolor='lightgray',
        showgrid=True,
        separatethousands=True
    ),
    legend=dict(
        x=1.2,
        y=0.98,
        font=dict(size=12),
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='gray',
        borderwidth=1
    ),
    hovermode='closest',
    plot_bgcolor='white',
    width=1100,
    height=700,
    margin=dict(l=80, r=150, t=80, b=80)
)

fig.show()
# fig.write_html('../plots/carpet_plot_fuel_burn_mach_altitude.html')
