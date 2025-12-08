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
m_optimized_mach = [0.76] #[0.76, 0.76]
m_optimized_altitude = [40_000] #[37_000, 38_000]
m_optimized_mission_time = [453.05] #[452.78, 452.73,] #in minutes
m_optimized_fuel_burn = [19_565.58] #[19_834.82, 19_687.61] #in lbm

#Optimized with aspect ratio, length, and span
ARSL_optimized_mach =[0.76]
ARSL_optimized_altitude = [40_000]
ARSL_optimized_misison_time = [467.65] #in minutes
ARSL_optimized_fuel_burn = [16_928.89] #in lbm



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
    x=m_optimized_mach,
    y=m_optimized_altitude,
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
                  '<b>Mission Time:</b> ' + f'{m_optimized_mission_time[0]:.2f} min<br>' +
                  '<b>Fuel Burn:</b> ' + f'{m_optimized_fuel_burn[0]:,.2f} lbm<br>' +
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




#==== End of carpet plot generation ====


#==== Plotting carpet plot similar to above but for aspect ratio ====

AR_fuel_burn_data = [[20738.33, 21060.78, 21523.63, 22271.98],
                     [19640.44, 19904.37, 20283.37, 20992.91],
                     [18929.88, 19163.33, 19508.63, 20283.92],
                     [18241.93, 18458.14, 18819.44, 19692.02],
                     [20311.65, 20610.74, 21157.04, 21674.37],
                     [19440.62, 19702.75, 20053.87, 20740.19],
                     [18852.56, 19099.73, 19442.74, 20203.51],
                     [18238.36, 18489.21, 18901.7, 19735.62],
                     [20124.19, 20415.52, 20746.77, 21368.2],
                     [19389.69, 19659.48, 19992.01, 20680.95],
                     [0, 19142.5, 19521.42, 0],
                     [18341.79, 18612.48, 19071.67, 19870.9],
                     [20089.7, 20379.34, 20726.27, 21377.4],
                     [19459.06, 0, 20116.01, 20813.92],
                     [19007.93, 19288.04, 19718.79, 20455.93],
                     [18530.4, 18826.26, 19324.69, 20119.92]
                     ]

AR_aspect_ratio = [[11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87],
                   [11.5, 12.5, 13.5, 14.87]]

AR_altitude = [[40000, 40000, 40000, 40000],
                [40000, 40000, 40000, 40000],
                [40000, 40000, 40000, 40000],
                [40000, 40000, 40000, 40000],
                [39000, 39000, 39000, 39000],
                [39000, 39000, 39000, 39000],
                [39000, 39000, 39000, 39000],
                [39000, 39000, 39000, 39000],
                [38000, 38000, 38000, 38000],
                [38000, 38000, 38000, 38000],
                [38000, 38000, 38000, 38000],
                [38000, 38000, 38000, 38000],
                [37000, 37000, 37000, 37000],
                [37000, 37000, 37000, 37000],
                [37000, 37000, 37000, 37000],
                [37000, 37000, 37000, 37000]]

AR_mach = [[0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82],
           [0.76, 0.78, 0.80, 0.82]]


#Optimized points 
# #optimized mission profile data
# m_optimized_mach = [0.76] #[0.76, 0.76]
# m_optimized_altitude = [40_000] #[37_000, 38_000]
# m_optimized_mission_time = [453.05] #[452.78, 452.73,] #in minutes
# m_optimized_fuel_burn = [19_565.58] #[19_834.82, 19_687.61] #in lbm

# #Optimized with aspect ratio, length, and span
# ARSL_optimized_mach =[0.76]
# ARSL_optimized_altitude = [40_000]
# ARSL_optimized_misison_time = [467.65] #in minutes
# ARSL_optimized_fuel_burn = [16_928.89] #in lbm


# Your data here - please provide:
# - altitude values
# - mach number values  
# - fuel burn data
# - aspect ratio data
# - m_optimized point (altitude, mach, fuel_burn, aspect_ratio)
# - ARSL_optimized point (altitude, mach, fuel_burn, aspect_ratio)

# Example structure (replace with your actual data):
altitudes = [36_000, 37_000, 38_000, 39_000]
mach_numbers = [0.76, 0.78, 0.80, 0.82]

# Fuel burn data (2D array)
fuel_burn_data = [[20_205.43, 20_762.39, 21_852.11, 24_112.98],
                  [21_668.07, 20_594.73, 21_753.51, 20_500],
                  [20_107.03, 20_549.67, 21_847.99, 21_000],
                  [20_354.30, 20_747.47, 22_000, 22_500]]

# Aspect ratio data (2D array)
aspect_ratio_data = [[10.5, 10.8, 11.0, 11.2],
                     [10.3, 10.6, 10.9, 11.1],
                     [10.1, 10.4, 10.7, 11.0],
                     [9.9, 10.2, 10.5, 10.8]]

# Optimized points
m_optimized = {
    'altitude': 38_000,
    'mach': 0.78,
    'fuel_burn': 19_500,
    'aspect_ratio': 10.5
}

ARSL_optimized = {
    'altitude': 37_000,
    'mach': 0.80,
    'fuel_burn': 19_800,
    'aspect_ratio': 10.8
}

# Flatten data for interpolation
alt_flat = []
mach_flat = []
fuel_flat = []
ar_flat = []

for i, alt in enumerate(altitudes):
    for j, mach in enumerate(mach_numbers):
        if i < len(fuel_burn_data) and j < len(fuel_burn_data[i]):
            alt_flat.append(alt)
            mach_flat.append(mach)
            fuel_flat.append(fuel_burn_data[i][j])
            ar_flat.append(aspect_ratio_data[i][j])

# Create grid for interpolation
mach_grid = np.linspace(min(mach_flat), max(mach_flat), 100)
alt_grid = np.linspace(min(alt_flat), max(alt_flat), 100)
mach_mesh, alt_mesh = np.meshgrid(mach_grid, alt_grid)

# Interpolate fuel burn and aspect ratio data
fuel_mesh = griddata((mach_flat, alt_flat), fuel_flat, (mach_mesh, alt_mesh), method='cubic')
ar_mesh = griddata((mach_flat, alt_flat), ar_flat, (mach_mesh, alt_mesh), method='cubic')

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
        tickfont=dict(size=12),
        len=0.7,
        y=0.5
    ),
    hovertemplate='<b>Mach:</b> %{x:.2f}<br>' +
                  '<b>Altitude:</b> %{y:,.0f} ft<br>' +
                  '<b>Fuel Burn:</b> %{z:,.2f} lbm<br>' +
                  '<extra></extra>',
    name='Fuel Burn'
))

# Add contour lines for aspect ratio (white lines)
fig.add_trace(go.Contour(
    x=mach_grid,
    y=alt_grid,
    z=ar_mesh,
    showscale=False,
    contours=dict(
        showlabels=True,
        labelfont=dict(size=9, color='black'),
        coloring='none'
    ),
    line=dict(
        color='white',
        width=2
    ),
    hovertemplate='<b>Mach:</b> %{x:.2f}<br>' +
                  '<b>Altitude:</b> %{y:,.0f} ft<br>' +
                  '<b>Aspect Ratio:</b> %{z:.2f}<br>' +
                  '<extra></extra>',
    name='Aspect Ratio'
))

# Add scatter points for actual data
fig.add_trace(go.Scatter(
    x=mach_flat,
    y=alt_flat,
    mode='markers',
    marker=dict(
        size=8,
        color='lightgray',
        line=dict(color='black', width=1)
    ),
    name='Data Points',
    hovertemplate='<b>Mach:</b> %{x:.2f}<br>' +
                  '<b>Altitude:</b> %{y:,.0f} ft<br>' +
                  '<extra></extra>'
))

# Add m_optimized point
fig.add_trace(go.Scatter(
    x=[m_optimized['mach']],
    y=[m_optimized['altitude']],
    mode='markers',
    marker=dict(
        size=15,
        color='lightblue',
        line=dict(color='pink', width=3),
        symbol='star'
    ),
    name='m_optimized',
    hovertemplate='<b>m_optimized</b><br>' +
                  '<b>Mach:</b> %{x:.2f}<br>' +
                  '<b>Altitude:</b> %{y:,.0f} ft<br>' +
                  f'<b>Fuel Burn:</b> {m_optimized["fuel_burn"]:,.2f} lbm<br>' +
                  f'<b>Aspect Ratio:</b> {m_optimized["aspect_ratio"]:.2f}<br>' +
                  '<extra></extra>'
))

# Add ARSL_optimized point
fig.add_trace(go.Scatter(
    x=[ARSL_optimized['mach']],
    y=[ARSL_optimized['altitude']],
    mode='markers',
    marker=dict(
        size=15,
        color='cyan',
        line=dict(color='blue', width=3),
        symbol='star'
    ),
    name='ARSL_optimized',
    hovertemplate='<b>ARSL_optimized</b><br>' +
                  '<b>Mach:</b> %{x:.2f}<br>' +
                  '<b>Altitude:</b> %{y:,.0f} ft<br>' +
                  f'<b>Fuel Burn:</b> {ARSL_optimized["fuel_burn"]:,.2f} lbm<br>' +
                  f'<b>Aspect Ratio:</b> {ARSL_optimized["aspect_ratio"]:.2f}<br>' +
                  '<extra></extra>'
))

# Update layout
fig.update_layout(
    title={
        'text': 'Carpet Plot: Fuel Burn and Aspect Ratio vs Mach Number and Altitude',
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
        font=dict(size=11),
        bgcolor='rgba(255,255,255,0.9)',
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




