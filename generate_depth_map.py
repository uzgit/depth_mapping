#!/usr/bin/python3

import sys
import numpy as np
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt

# Set some values for the aesthetic of the depth map
num_longitude_interpolation_points = 100
num_latitude_interpolation_points  = 100
number_of_latitude_longitude_ticks = 10
line_ticks        = 7
color_ticks       = 30
color_label_ticks = 30

depth_sanity_constraint = 1000;                 #The Intelliducer outputs 1000000 when in an error state


# for calling via terminal
if len(sys.argv) != 2:
    print("Usage: ./generate_depth_map.py <.csv file>")


messages = np.genfromtxt(sys.argv[1], delimiter=',')
messages = messages[1:]

######################################################################
# If using a .csv generated from mysql

latitudes_raw  = messages[:,[1]]    # extract latitudes from column 1 (0-based indices)
longitudes_raw = messages[:,[2]]    # extract longitudes from column 2
depths_raw     = messages[:,[3]]    # extract depths from column 3

######################################################################
# Remove erroneous samples. These are samples which would have been taken by the
# Intelliducer when the boat was out of the water.

latitudes_raw  = latitudes_raw.reshape(len(latitudes_raw),)
longitudes_raw = longitudes_raw.reshape(len(longitudes_raw),)
depths_raw     = depths_raw.reshape(len(depths_raw),)

latitudes  = []
longitudes = []
depths     = []
for i in range(len(depths_raw)):

    if(abs(depths_raw[i]) < depth_sanity_constraint):   # collect all geotagged depths that don't represent error states

        latitudes.append(latitudes_raw[i])
        longitudes.append(longitudes_raw[i])
        depths.append(depths_raw[i])

######################################################################
# Create a bounding box, inside which to generate the map.
minimum_latitude  = min(latitudes)
maximum_latitude  = max(latitudes)
minimum_longitude = min(longitudes)
maximum_longitude = max(longitudes)

######################################################################
# Create an evenly spaced grid inside the bounding box.
interpolation_longitudes = np.linspace(minimum_longitude, maximum_longitude, num_longitude_interpolation_points)
interpolation_latitudes  = np.linspace(minimum_latitude,  maximum_latitude,  num_latitude_interpolation_points)

############################################################################################################################
# Using linear interpolation, calculate the depth at each point on the evenly spaced grid.
interpolated_depths = griddata(longitudes, latitudes, depths, interpolation_longitudes, interpolation_latitudes, interp='linear')

# Visualizing the data
######################################################################

# Generate longitude labels.
longitude_ticks        = []
longitude_ticks_labels = []
for i in np.linspace(minimum_longitude, maximum_longitude, number_of_latitude_longitude_ticks):
    longitude_ticks.append(i)
    longitude_ticks_labels.append("%.6f" % i)

# Generate latitude labels.
latitude_ticks        = []
latitude_ticks_labels = []
for i in np.linspace(minimum_latitude, maximum_latitude, number_of_latitude_longitude_ticks):
    latitude_ticks.append(i)
    latitude_ticks_labels.append("%.6f" % i)

# Create contour lines.
contour  = plt.contour (interpolation_longitudes, interpolation_latitudes, -interpolated_depths, line_ticks, linewidths=0.5, colors='k')

# Colorize areas bounded by the contour lines.
contourf = plt.contourf(interpolation_longitudes, interpolation_latitudes, interpolated_depths, color_ticks, cmap='Blues', vmin=-abs(interpolated_depths).max(), vmax=abs(interpolated_depths).max())

# Add a legend.
colorbar = plt.colorbar(ticks=np.linspace(abs(interpolated_depths).max(), -abs(interpolated_depths).max(), color_label_ticks), label="Depth (m)")

# Plot the locations where the boat actually collected the data that is being used to create the depth map.
plt.scatter(longitudes, latitudes, marker='o', c='black', s=5, zorder=10)

# Set labels and limits on the x and y axes.
plt.xticks(longitude_ticks, longitude_ticks_labels, rotation='vertical')
plt.yticks(latitude_ticks, latitude_ticks_labels)
plt.xlim(minimum_longitude, maximum_longitude)
plt.ylim(minimum_latitude,  maximum_latitude)

plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()