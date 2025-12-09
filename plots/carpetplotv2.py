import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma

# ==========================
# Your Data
# ==========================
aspect_ratio = np.array([10, 15, 20, 25, 30, 35])
sweep = np.array([15, 17, 19, 21, 23, 25])

fuel_burn_data = np.array([[9311.8,	9116.68,	8991.85,	11705.19,	11697.82,	0],
                          [8982.68,	8878.65,	8770.58,	9048.09,	11271.5,	0],
                          [8747.22,	8581.3,	8493.31,	8724.47,	0,	0],
                          [8619.84,	8364.65,	8197,	8433.5,	0,	0],
                          [8564.66,	8252.98,	8051.45,	8165.68,	0,	0],
                          [8594.26,	8234.74,	7978.57,	7965.61,	0,	0]])

#lift_data = [[0.71,	0.76,	0.8,	0.84,	0.88,	0],
#                              [0.7,	0.74,	0.78,	0.82,	0.86,	0],
#                              [0.68,	0.72,	0.76,	0.8,	0,	0],
#                              [0.65,	0.7,	0.74,	0.77,	0,	0],
#                              [0.63,	0.67,	0.7,	0.74,	0,	0],
#                              [0.59,	0.63,	0.66,	0.7,	0,	0]]

# Mask zeros (treat as missing)
Z = ma.masked_where(fuel_burn_data == 0, fuel_burn_data)

# Create 2D mesh for plotting
X, Y = np.meshgrid(aspect_ratio, sweep)

# ==========================
# Plotting
# ==========================
fig, ax = plt.subplots(figsize=(9, 7))

# Filled contour of fuel burn
cont = ax.contourf(X, Y, Z, levels=20, cmap="inferno")

# Contour lines of Z
ax.contour(X, Y, Z, colors="black", linewidths=0.7)

# Carpet lines for X (iso-AR)
ax.contour(X, Y, X, colors='red', linestyles='--', linewidths=0.7)

# Carpet lines for Y (iso-sweep)
ax.contour(X, Y, Y, colors='blue', linestyles='--', linewidths=0.7)

# Labels & colorbar
fig.colorbar(cont, label="Lift Coefficient")
ax.set_xlabel("Aspect Ratio")
ax.set_ylabel("Sweep Angle (deg)")
ax.set_title("Lift Coefficient vs AR & Sweep")

plt.tight_layout()
plt.show()


# ==========================
# Lift vs AR & Sweep Carpet Plot
# ==========================

