import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter
import os
import random
from mpl_toolkits.mplot3d import Axes3D  # For 3D plots

# ========== USER INPUT ========== #
area_cm2 = float(input("📏 Enter room area in cm²: "))

# ========== ROOM GRID SETUP ========== #
room_side = np.sqrt(area_cm2)  # Assume square room
main_divs = 5
sub_divs_per_main = 10

total_rows = main_divs
total_cols = sub_divs_per_main

main_box_size = room_side / main_divs
sub_box_size = main_box_size / sub_divs_per_main

print(f"\n🧱 Room divided into {total_rows} rows × {total_cols} columns.")
print(f"Each grid cell ≈ {sub_box_size:.2f} cm × {sub_box_size:.2f} cm\n")

# ========== KALMAN FILTER SETUP ========== #
def create_kf():
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.x = np.array([[0.], [0.]])
    kf.F = np.array([[1., 1.], [0., 1.]])
    kf.H = np.array([[1., 0.]])
    kf.P *= 1000.
    kf.R = 5
    kf.Q = np.array([[1., 0.], [0., 1.]]) * 0.01
    return kf

# ========== DATA SIMULATION ========== #
raw_grid = np.zeros((total_rows, total_cols))
filtered_grid = np.zeros((total_rows, total_cols))

for i in range(total_rows):
    for j in range(total_cols):
        kf = create_kf()
        readings = []
        for _ in range(20):  # simulate 20 time steps
            raw = -70 + random.uniform(-10, 10)  # Simulated RSSI
            kf.predict()
            kf.update(np.array([[raw]]))
            readings.append((raw, kf.x[0][0]))
        raw_avg = np.mean([r[0] for r in readings])
        filtered_avg = np.mean([r[1] for r in readings])
        raw_grid[i][j] = raw_avg
        filtered_grid[i][j] = filtered_avg

# ========== SAVE TO CSV ========== #
os.makedirs("output", exist_ok=True)
pd.DataFrame(raw_grid).to_csv("output/simulated_raw.csv", index=False)
pd.DataFrame(filtered_grid).to_csv("output/simulated_filtered.csv", index=False)

# ========== VISUALIZATIONS ========== #

# 1. Heatmap
plt.figure(figsize=(10, 6))
plt.title("📶 Simulated WiFi Signal Heatmap (Filtered)")
plt.xlabel("Sub-Box Columns")
plt.ylabel("Main Box Rows")
heatmap = plt.imshow(filtered_grid, cmap='plasma', interpolation='nearest')
plt.colorbar(heatmap, label='Signal Strength (dBm)')
plt.savefig("output/simulated_heatmap.png")
plt.show()

# 2. Gradient
plt.figure(figsize=(10, 6))
plt.title("🎨 WiFi Gradient View")
gradient = plt.imshow(filtered_grid, cmap='coolwarm', interpolation='bicubic')
plt.colorbar(gradient, label='Signal Strength (dBm)')
plt.savefig("output/simulated_gradient.png")
plt.show()

# 3. Line Graph (Row-wise)
plt.figure(figsize=(10, 5))
plt.title("📈 Row-wise Signal Strength (Filtered)")
for i in range(total_rows):
    plt.plot(filtered_grid[i], label=f"Row {i+1}")
plt.xlabel("Sub-Box Columns")
plt.ylabel("Signal Strength (dBm)")
plt.legend()
plt.grid(True)
plt.savefig("output/row_line_plot.png")
plt.show()

# 4. Line Graph (Column-wise)
plt.figure(figsize=(10, 5))
plt.title("📈 Column-wise Signal Strength (Filtered)")
for j in range(total_cols):
    col_vals = filtered_grid[:, j]
    plt.plot(col_vals, label=f"Col {j+1}")
plt.xlabel("Main Box Rows")
plt.ylabel("Signal Strength (dBm)")
plt.legend()
plt.grid(True)
plt.savefig("output/col_line_plot.png")
plt.show()

# 5. 3D Surface Plot
X = np.arange(0, total_cols)
Y = np.arange(0, total_rows)
X, Y = np.meshgrid(X, Y)
Z = filtered_grid

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='k')
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Signal Strength (dBm)')
ax.set_title("🗻 3D WiFi Signal Surface")
ax.set_xlabel("Columns")
ax.set_ylabel("Rows")
ax.set_zlabel("Signal (dBm)")
plt.savefig("output/3d_surface_plot.png")
plt.show()

# 6. Contour Plot
plt.figure(figsize=(10, 6))
cp = plt.contourf(X, Y, Z, cmap='inferno', levels=20)
plt.colorbar(cp, label="Signal Strength (dBm)")
plt.title("🌍 Contour Plot of WiFi Signal")
plt.xlabel("Columns")
plt.ylabel("Rows")
plt.savefig("output/contour_plot.png")
plt.show()

print("✅ Done! All visualizations and CSV files saved in ./output/")
