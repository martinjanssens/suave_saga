# Analyses.py
# 
# Created:  Mar. 2016, M. Vegh
# Modified: 

# ----------------------------------------------------------------------        
#   Imports
# ----------------------------------------------------------------------    

import SUAVE
import numpy as np
from SUAVE.Core import Units
from empty_saga import empty
from Optimize import AVL_analysis


# ----------------------------------------------------------------------
#   Setup Analyses
# ----------------------------------------------------------------------  

def setup(configs):
    analyses = SUAVE.Analyses.Analysis.Container()

    # build a base analysis for each config
    for tag, config in configs.items():
        analysis = base(config)
        analyses[tag] = analysis

    # adjust analyses for configs

    # takeoff_analysis
    analyses.takeoff.aerodynamics.settings.drag_coefficient_increment = 0.0000

    # landing analysis
    aerodynamics = analyses.landing.aerodynamics

    return analyses


# ----------------------------------------------------------------------
#   Define Base Analysis
# ----------------------------------------------------------------------  

def base(vehicle):
    # ------------------------------------------------------------------
    #   Initialize the Analyses
    # ------------------------------------------------------------------     
    analyses = SUAVE.Analyses.Vehicle()

    # ------------------------------------------------------------------
    #  Basic Geometry Relations
    sizing = SUAVE.Analyses.Sizing.Sizing()
    sizing.features.vehicle = vehicle
    analyses.append(sizing)

    # ------------------------------------------------------------------
    #  Weights
    weights = SUAVE.Analyses.Weights.Weights()
    weights.settings.empty_weight_method = empty
    weights.vehicle = vehicle
    analyses.append(weights)

    # ------------------------------------------------------------------
    #  Aerodynamics Analysis
    if AVL_analysis == False: #Run zero-fidelity method
        aerodynamics = SUAVE.Analyses.Aerodynamics.Fidelity_Zero()
        aerodynamics.geometry = vehicle

        aerodynamics.settings.drag_coefficient_increment = 0.0000
        analyses.append(aerodynamics)

    #  AVL-based analysis
    else:
        #aerodynamics_avl = SUAVE.Analyses.Aerodynamics.Surrogates.AVL()
        #aerodynamics_avl.training.angle_of_attack = np.array([-5.,0.,15.]) * Units.deg
        aerodynamics_avl = SUAVE.Analyses.Aerodynamics.AVL()
        aerodynamics_avl.features = vehicle
        aerodynamics_avl.geometry = vehicle

        #aerodynamics_avl.lift.total
        analyses.append(aerodynamics_avl)
        # aerodynamics_avl.finalized = False
        # print aerodynamics_avl

    # ------------------------------------------------------------------
    #  Stability Analysis
    stability = SUAVE.Analyses.Stability.Fidelity_Zero()
    stability.geometry = vehicle
    analyses.append(stability)

    #  Noise Analysis
    noise = SUAVE.Analyses.Noise.Fidelity_One()
    noise.geometry = vehicle
    analyses.append(noise)

    # ------------------------------------------------------------------
    #  Energy
    energy = SUAVE.Analyses.Energy.Energy()
    energy.network = vehicle.propulsors  # what is called throughout the mission (at every time step))
    analyses.append(energy)
    #

    # ------------------------------------------------------------------
    #  Planet Analysis
    planet = SUAVE.Analyses.Planets.Planet()
    analyses.append(planet)

    # ------------------------------------------------------------------
    #  Atmosphere Analysis
    atmosphere = SUAVE.Analyses.Atmospheric.US_Standard_1976()
    atmosphere.features.planet = planet.features
    analyses.append(atmosphere)

    # done!
    return analyses