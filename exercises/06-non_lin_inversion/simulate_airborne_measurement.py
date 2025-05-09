#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulate airborne radiometric measurements from a HALO-like airplane.

This script simulates radiometric measurements of atmospheric radiation in three frequency bands:
- H2O (22 GHz)
- O2_low (50 GHz)  
- O2_high (118 GHz)

The simulation assumes:
- Aircraft altitude of 15 km
- Nadir-looking geometry (180 degree line of sight)
- Known constant surface reflectivity of 0.4
- Known constant surface temperature of 300K

The script:
1. Loads atmospheric data and auxiliary information
2. Simulates clean measurements for each frequency band
3. Adds random measurement noise based on specified NeDT
4. Saves results as XML files
5. Generates plots of simulated measurements vs latitude

Files:
    Input:
        - atmosphere/atmospheres_true.xml: Atmospheric profiles
        - atmosphere/aux1d_true.xml: Auxiliary data including latitudes
    
    Output:
        - observation/y_obs_*.xml: Simulated noisy measurements
        - observation/f_grid_*.xml: Frequency grids
        - observation/lat.xml: Latitude points
        - check_plots/airborne_measurement.pdf: Visualization of results

Dependencies:
    - numpy: For numerical operations
    - matplotlib: For plotting
    - pyarts: For XML handling
    - nonlin_oem: Custom module for radiative transfer calculations

Created on Sat Jan  4 00:42:52 2025
@author: Manfred Brath
"""

import numpy as np
import matplotlib.pyplot as plt
from pyarts import xml

import nonlin_oem as nlo


# =============================================================================
# %% paths and constants
# =============================================================================


# atmospheric data
atms = xml.load("atmosphere/atmospheres_true.xml")
auxs = xml.load("atmosphere/aux1d_true.xml")

# surface reflectivity
# It is assumed that the surface reflectivity is known and constant
surface_reflectivity = 0.4

# surface temperature
# It is assumed that the surface temperature is known and constant
surface_temperature = 300.0  # K

# define sensor positions and line of sight
# we assume a HALO like airplane with a sensor at 15 km altitude and a line of sight of 180 degrees
sensor_altitude = 15000.
sensor_los = 180.

# set the random number generator
rng = np.random.default_rng(12345)


# latitude
lat = np.array([auxs[i].data[0] for i in range(len(auxs))])

# =============================================================================
# %% simulate the observation


bands = ["K", "V", "F"]
suffixes = ["22GHz", "50GHz", "118GHz"]


results = {}
for band, suffix in zip(bands, suffixes):

    print(f"\n{band}\n")

    # set the "channels" (freqquency grid) for the simulation
    sensor_description_fine, NeDT, Accuracy, FWHM_Antenna=nlo.Hamp_channels([band], rel_mandatory_grid_spacing=1./1.)

    # # setup the basics
    # ws = nlo.basic_setup(f_grid)

    y = np.zeros((len(atms), np.size(sensor_description_fine,0)))

    for i in range(len(atms)):
        if i % 10 == 0:
            print(f"Simulating measurement for atm {i}")

        atm = atms[i]
        y[i, :], _ = nlo.Forward_model(
            [],
            atm,
            surface_reflectivity,
            surface_temperature,
            sensor_altitude,
            sensor_los,            
            sensor_description=sensor_description_fine
        )
    

    y_obs = y + rng.normal(0, NeDT, y.shape)


    results[("y_" + band)] = y
    results[("y_obs_" + band)] = y_obs
    results[("f_grid_" + band)] = sensor_description_fine[:,0]+sensor_description_fine[:,1]+sensor_description_fine[:,2]
    results[('NeDT_'+band)]=NeDT
    results[(band + "_suffix")] = suffix
    results[('sensor_description_' + band)] = sensor_description_fine

    Y = nlo.pa.arts.Matrix(y)
    Y_obs = nlo.pa.arts.Matrix(y_obs)
    SensorCharacteristics = nlo.pa.arts.Matrix(sensor_description_fine)

    Y_obs.savexml(f"observation/y_obs_{suffix}.xml")
    SensorCharacteristics.savexml(
        f"observation/SensorCharacteristics_{suffix}.xml"
    )

    print("ddd")


Lat = nlo.pa.arts.Vector(lat)
Lat.savexml("observation/lat.xml")


# %% plot results

cmap = np.array(
    [
        [0, 0.44701, 0.74101, 1],
        [0.85001, 0.32501, 0.09801, 1],
        [0.92901, 0.69401, 0.12501, 1],
        [0.49401, 0.18401, 0.55601, 1],
        [0.46601, 0.67401, 0.18801, 1],
        [0.30101, 0.74501, 0.93301, 1],
        [0.63501, 0.07801, 0.18401, 1],
    ]
)


fig, ax = plt.subplots(3, 1, figsize=(16, 10))

for i, band in enumerate(bands):

    ax[i].set_prop_cycle(color=cmap)
    sen_desc=results[f"sensor_description_{band}"]

    for j in range(np.size(sen_desc,0)):
        if sen_desc[j,1]+sen_desc[j,2]>0:
            label=f"{sen_desc[j,0]/1e9:0.2f}"+" $\pm$ "+f"{(sen_desc[j,1]+sen_desc[j,2])/1e9:0.2f} GHz"
        else:
            label=f"{sen_desc[j,0]/1e9:0.2f}"
                      
        ax[i].plot(lat, results[(f"y_{band}")][:, j], label=label)   

    ax[i].set_prop_cycle(color=cmap)
    for j in range(np.size(sen_desc,0)):
        if sen_desc[j,1]+sen_desc[j,2]>0:
            label=f"{sen_desc[j,0]/1e9:0.2f}"+" $\pm$ "+f"{(sen_desc[j,1]+sen_desc[j,2])/1e9:0.2f} GHz"
        else:
            label=f"{sen_desc[j,0]/1e9:0.2f}"
        ax[i].plot(
            lat, results[(f"y_obs_{band}")][:, j], "--", label=f"{label} (obs)"
        )

    ax[i].set_title(band)
    ax[i].legend()
    ax[i].set_xlabel("Latitude")
    ax[i].set_ylabel("Brightness temperature [K]")
    ax[i].grid()


fig.tight_layout()
fig.savefig("check_plots/airborne_measurement.pdf")
