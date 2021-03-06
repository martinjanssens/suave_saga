# Optimize.py
# Created:  Feb 2016, M. Vegh
# Modified: 

# ----------------------------------------------------------------------        
#   Imports
# ----------------------------------------------------------------------    

import SUAVE
from SUAVE.Core import Units, Data
import numpy as np
import Vehicles
import Analyses
import Mission_backwards2
import Procedure
import Plot_Mission
import matplotlib.pyplot as plt
from SUAVE.Optimization import Nexus, carpet_plot
import SUAVE.Optimization.Package_Setups.scipy_setup as scipy_setup
import SUAVE.Optimization.Package_Setups.pyopt_setup as pyopt_setup


# ----------------------------------------------------------------------        
#   Run the whole thing
# ----------------------------------------------------------------------


# give proper output to backwork it
# newest config:
# S:700, vc:700, ret_h: 19.2, ret_vc = 750, A=15
# MTOW: 170T, thrust: 115kN
#  fuel burn:  [ 41769.08023241]

#AVL Analysis on or off
AVL_analysis = False

def main():
    print "SUAVE initialized...\n"
    problem = setup()  # "problem" is a nexus

    output = problem.objective()  # uncomment this line when using the default inputs
    # variable_sweep(problem)  # uncomment this to view some contours of the problem
    # output = scipy_setup.SciPy_Solve(problem, solver='SLSQP') # uncomment this to optimize the values
    # output = pyopt_setup.Pyopt_Solve(problem,solver='SNOPT') #,FD='single', nonderivative_line_search=False)

    print 'constraints=', problem.all_constraints()

    Plot_Mission.plot_mission(problem.results, show=False)

    return


# ----------------------------------------------------------------------
#   Inputs, Objective, & Constraints
# ----------------------------------------------------------------------  

def setup():
    nexus = Nexus()
    problem = Data()
    nexus.optimization_problem = problem

    # -------------------------------------------------------------------
    # Inputs
    # -------------------------------------------------------------------

    # twin = "OFF"
    # thrust_total = 115000 * Units.N  # Newtons 111
    # num_engine = 4  # move to main -> how to guarantee these parameters when not optimized for??? - selected at the top and entered in inputs from there?
    # bypass = 6

    problem.inputs = np.array([
        # Variable inputs
        ['wing_area', 700, (400., 750.), 500., Units.meter ** 2],
        ['MTOW', 203e3, (180000., 230000.), 200000., Units.kg],
        ['alt_outgoing_cruise', 13.14, (8., 20.), 15., Units.km],
        ['design_thrust', 100e3, (85e3, 115e3), 100e3, Units.N],
        ['outgoing_cruise_speed', 191., (150, 220), 200, Units['m/s']],
        ['spray_cruise_speed', 200., (150, 220), 200, Units['m/s']],
        # climb throttle as input?

        # "Set" inputs
        ['AR', 15, (15, 15), 15, Units.less],
        # speeds???
    ])
    # opt results: [700.0000000000755, 180623.48270764505, 13.147354544329831, 93680.83722141015, 193.90945445747235, 200.00000000005906, 15.00000022353205]

    #   [ tag, initial, (lb,ub) , scaling , units ]
    # problem.inputs = np.array([
        # ['wing_area', 700, (400., 600.), 500., Units.meter ** 2],  # was 480 before -> constrained by tip deflection not strength!
        # ['MTOW', 180000., (160000.,160000.), 160000., Units.kg],
        #['cruise_speed', 700., (600., 900.), 500., Units['km/h']],  # 756
        #['return_cruise_alt', 19.2, (8., 20.), 10, Units.km],
        # ['AR',15,(10,15),10,Units.less], # wing area, vs MTOW fuel weight for different
        #['return_cruise_speed', 750., (600., 760.), 500., Units['km/h']],

        # ['cruise_altitude',19,(19,19),19,Units.km],
        # ['wing_sweep', 0, (0,0),5,Units.less],

        # [ 'cruise_altitude'              ,  19.5    , (   19.5   ,    21.   ) ,   10.  , Units.km],
        # [ 'c1_airspeed'              ,  90    , (   50   ,    250.   ) ,   100.  , Units['m/s']],
        # [ 'c1_rate'              ,  15    , (   1   ,    25.   ) ,   10.  , Units['m/s']],
        #
        # [ 'c2_airspeed'              ,  110    , (   50   ,    250.   ) ,   100.  , Units['m/s']],
        # [ 'c2_rate'              ,  11    , (   1   ,    25.   ) ,   10.  , Units['m/s']],
        #
        # [ 'c3_airspeed'              ,  120    , (   50   ,    250.   ) ,   100.  , Units['m/s']],
        # [ 'c3_rate'              ,  8    , (   1   ,    25.   ) ,   10.  , Units['m/s']],
        #
        # [ 'c4_airspeed'              ,  150    , (   50   ,    250.   ) ,   100.  , Units['m/s']],
        # [ 'c4_rate'              ,  6    , (   1   ,    25.   ) ,   10.  , Units['m/s']],
        #
        # [ 'c5_airspeed'              ,  200    , (   50   ,    250.   ) ,   100.  , Units['m/s']],
        # [ 'c5_rate'              ,  4    , (   1   ,    25.   ) ,   10.  , Units['m/s']]

        # segment.altitude_end   = 3 * Units.km
        #     segment.air_speed      = 118.0 * Units['m/s']
        #     segment.climb_rate     = 15. * Units['m/s']

    #])

    # -------------------------------------------------------------------
    # Objective
    # -------------------------------------------------------------------

    # throw an error if the user isn't specific about wildcards
    # [ tag, scaling, units ]
    problem.objective = np.array([
        # [ 'Nothing', 1, Units.kg ]
        # ['max_throttle', .8 ,Units.less],
        ['fuel_burn', 45000., Units.kg]
    ])

    # -------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------

    # stuctural weight below some threshold
    # [ tag, sense, edge, scaling, units ]
    problem.constraints = np.array([

        # ['min_throttle', '>', 0., 1e-2, Units.less],
        ['max_throttle', '<', 1., 1e-2, Units.less],
        ['main_mission_time', '<', 11.1, 1, Units.h],
        ['mission_range', '>', 7000., 100., Units.km],
        # ['aerosol_released', '=', 40000., 50., Units.kg ],
        ['design_range_fuel_margin' , '>', 0.05, 1E-1, Units.less],
        ['take_off_field_length', '<', 2500., 1e-1, Units.m],
        ['landing_field_length', '<', 2500., 1e-1, Units.m],
        ['MTOW_delta', '<', '1' , 4, Units.kg],
        ['MTOW_delta', '>', '-1', 4, Units.kg], # tricky to predict the effects of MTOW constraints


    ])

    # -------------------------------------------------------------------
    #  Aliases
    # -------------------------------------------------------------------

    # [ 'alias' , ['data.path1.name','data.path2.name'] ]

    problem.aliases = [
        ['wing_area', ['vehicle_configurations.*.wings.main_wing.areas.reference',
                       'vehicle_configurations.*.reference_area']],

        ['MTOW', ['vehicle_configurations.*.mass_properties.takeoff',
                  "vehicle_configurations.*.mass_properties.max_takeoff"]],

        ['alt_outgoing_cruise', 'missions.base.segments.climb_4_final_outgoing.altitude_end'],

        ['design_thrust', 'vehicle_configurations.*.propulsors.turbofan.thrust.total_design'],

        ['spray_cruise_speed', ['missions.base.segments.cruise_1.air_speed',
                                'missions.base.segments.cruise_2.air_speed',
                                'missions.base.segments.cruise_final.air_speed']],

        ['outgoing_cruise_speed', 'missions.base.segments.cruise_outgoing.air_speed'],

        # thrust_total
        # 1000.0

        ['AR', 'vehicle_configurations.*.wings.main_wing.aspect_ratio'],


        ['fuel_burn', 'summary.base_mission_fuelburn'],


        ['min_throttle', 'summary.min_throttle'],

        ['max_throttle', 'summary.max_throttle'],

        ['main_mission_time', 'summary.main_mission_time'],

        ['mission_range', 'summary.mission_range'],

        # ['aerosol_released', '=', 40000., 50., Units.kg], #FIXME

        ['design_range_fuel_margin', 'summary.max_zero_fuel_margin'],

        ['take_off_field_length', 'summary.field_length_takeoff'],

        ['landing_field_length', 'summary.field_length_landing'],

        ['MTOW_delta', 'summary.MTOW_delta'],






        ['cruise_speed', 'missions.base.segments.cruise_empty.air_speed'],
         # [
         #    "missions.base.segments.cruise_highlift.air_speed",
         #
         #    "missions.base.segments.cruise_2.air_speed"]],
        ['return_cruise_speed', "missions.base.segments.cruise_final.air_speed"],

        ['oswald', 'vehicle_configurations.*.wings.main_wing.span_efficiency'],
        ['cruise_altitude', "missions.base.segments.climb_8.altitude_end"],


        ['return_cruise_alt', 'missions.base.segments.descent_1.altitude_end'],

        ['bypass', 'vehicle_configurations.*.propulsors.turbofan.bypass_ratio'],
        ['wing_sweep', 'vehicle_configurations.*.wings.main_wing.sweep'],
        ['oew', 'summary.op_empty'],
        ['Nothing', 'summary.nothing'],
        ['c1_airspeed', 'missions.base.segments.climb_1.air_speed'],
        ['c1_rate', 'missions.base.segments.climb_1.climb_rate'],

        ['c2_airspeed', 'missions.base.segments.climb_2.air_speed'],
        ['c2_rate', 'missions.base.segments.climb_2.climb_rate'],

        ['c3_airspeed', 'missions.base.segments.climb_3.air_speed'],
        ['c3_rate', 'missions.base.segments.climb_3.climb_rate'],

        ['c4_airspeed', 'missions.base.segments.climb_4.air_speed'],
        ['c4_rate', 'missions.base.segments.climb_4.climb_rate'],

        ['c5_airspeed', 'missions.base.segments.climb_5.air_speed'],
        ['c5_rate', 'missions.base.segments.climb_5.climb_rate']
    ]

    # -------------------------------------------------------------------
    #  Vehicles
    # -------------------------------------------------------------------
    nexus.vehicle_configurations = Vehicles.setup()

    # -------------------------------------------------------------------
    #  Analyses
    # -------------------------------------------------------------------
    nexus.analyses = Analyses.setup(nexus.vehicle_configurations)

    # -------------------------------------------------------------------
    #  Missions
    # -------------------------------------------------------------------
    nexus.missions = Mission_backwards2.setup(nexus.analyses)

    # -------------------------------------------------------------------
    #  Procedure
    # -------------------------------------------------------------------    
    nexus.procedure = Procedure.setup()

    # -------------------------------------------------------------------
    #  Summary
    # -------------------------------------------------------------------    
    nexus.summary = Data()

    return nexus


def variable_sweep(problem, color_label, bar_label, xlabel, ylabel, title):
    number_of_points = 5
    outputs = carpet_plot(problem, number_of_points, 0, 0)  # run carpet plot, suppressing default plots
    inputs = outputs.inputs
    objective = outputs.objective
    constraints = outputs.constraint_val
    plt.figure(0)
    CS = plt.contourf(inputs[0, :], inputs[1, :], objective, 20, linewidths=2)
    cbar = plt.colorbar(CS)
    cbar.ax.set_ylabel(color_label)
    # cbar.ax.set_ylabel('fuel burn (kg)')

    if bar_label != "unknown":
        CS_const = plt.contour(inputs[0, :], inputs[1, :], constraints[0, :, :])
        plt.clabel(CS_const, inline=1, fontsize=10)
        cbar = plt.colorbar(CS_const)
        # cbar.ax.set_ylabel('fuel margin')
        cbar.ax.set_ylabel(bar_label)

    # plt.xlabel('wing area (m^2)')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.ylabel('cruise_speed (km)')

    '''
    #now plot optimization path (note that these data points were post-processed into a plottable format)
    wing_1  = [95          ,	95.00000149 ,	95          ,	95          ,	95.00000149 ,	95          ,	95          ,	95.00000149 ,	95          ,	106.674165  ,	106.6741665 ,	106.674165  ,	106.674165  ,	106.6741665 ,	106.674165  ,	106.674165  ,	106.6741665 ,	106.674165  ,	105.6274294 ,	105.6274309 ,	105.6274294 ,	105.6274294 ,	105.6274309 ,	105.6274294 ,	105.6274294 ,	105.6274309 ,	105.6274294 ,	106.9084316 ,	106.9084331 ,	106.9084316 ,	106.9084316 ,	106.9084331 ,	106.9084316 ,	106.9084316 ,	106.9084331 ,	106.9084316 ,	110.520489  ,	110.5204905 ,	110.520489  ,	110.520489  ,	110.5204905 ,	110.520489  ,	110.520489  ,	110.5204905 ,	110.520489  ,	113.2166831 ,	113.2166845 ,	113.2166831 ,	113.2166831 ,	113.2166845 ,	113.2166831 ,	113.2166831 ,	113.2166845 ,	113.2166831 ,	114.1649262 ,	114.1649277 ,	114.1649262 ,	114.1649262 ,	114.1649277 ,	114.1649262 ,	114.1649262 ,	114.1649277 ,	114.1649262 ,	114.2149828]
    alt_1   = [11.0              ,	11.0              ,	11.000000149011612,	11.0              ,	11.0              ,	11.000000149011612,	11.0              ,	11.0              ,	11.000000149011612,	9.540665954351425 ,	9.540665954351425 ,	9.540666103363037 ,	9.540665954351425 ,	9.540665954351425 ,	9.540666103363037 ,	9.540665954351425 ,	9.540665954351425 ,	9.540666103363037 ,	10.023015652305284,	10.023015652305284,	10.023015801316896,	10.023015652305284,	10.023015652305284,	10.023015801316896,	10.023015652305284,	10.023015652305284,	10.023015801316896,	10.190994033521863,	10.190994033521863,	10.190994182533474,	10.190994033521863,	10.190994033521863,	10.190994182533474,	10.190994033521863,	10.190994033521863,	10.190994182533474,	10.440582829327589,	10.440582829327589,	10.4405829783392  ,	10.440582829327589,	10.440582829327589,	10.4405829783392  ,	10.440582829327589,	10.440582829327589,	10.4405829783392  ,	10.536514606250261,	10.536514606250261,	10.536514755261873,	10.536514606250261,	10.536514606250261,	10.536514755261873,	10.536514606250261,	10.536514606250261,	10.536514755261873,	10.535957839878783,	10.535957839878783,	10.535957988890395,	10.535957839878783,	10.535957839878783,	10.535957988890395,	10.535957839878783,	10.535957839878783,	10.535957988890395,	10.52829047]
    wing_2  = [128        ,	128.0000015,	128        ,	128        ,	128.0000015,	128        ,	128        ,	128.0000015,	128        ,	130        ,	130.0000015,	130        ,	130        ,	130.0000015,	130        ,	130        ,	130.0000015,	130        ,	122.9564124,	122.9564139,	122.9564124,	122.9564124,	122.9564139,	122.9564124,	122.9564124,	122.9564139,	122.9564124,	116.5744347,	116.5744362,	116.5744347,	116.5744347,	116.5744362,	116.5744347,	116.5744347,	116.5744362,	116.5744347,	116.3530891,	116.3530906,	116.3530891,	116.3530891,	116.3530906,	116.3530891,	116.3530891,	116.3530906,	116.3530891]
    alt_2   = [13.8,	13.799999999999999,	13.80000014901161,	13.799999999999999,	13.799999999999999,	13.80000014901161,	13.799999999999999,	13.799999999999999,	13.80000014901161,	11.302562430674953,	11.302562430674953,	11.302562579686565,	11.302562430674953,	11.302562430674953,	11.302562579686565,	11.302562430674953,	11.302562430674953,	11.302562579686565,	11.158808932491421,	11.158808932491421,	11.158809081503033,	11.158808932491421,	11.158808932491421,	11.158809081503033,	11.158808932491421,	11.158808932491421,	11.158809081503033,	11.412913394878741,	11.412913394878741,	11.412913543890353,	11.412913394878741,	11.412913394878741,	11.412913543890353,	11.412913394878741,	11.412913394878741,	11.412913543890353,	11.402627869388722,	11.402627869388722,	11.402628018400334,	11.402627869388722,	11.402627869388722,	11.402628018400334,	11.402627869388722,	11.402627869388722,	11.402628018400334]

    
    opt_1   = plt.plot(wing_1, alt_1, label='optimization path 1')
    init_1  = plt.plot(wing_1[0], alt_1[0], 'ko')
    final_1 = plt.plot(wing_1[-1], alt_1[-1], 'kx')
    
    opt_2   = plt.plot(wing_2, alt_2, 'k--', label='optimization path 2')
    init_2  = plt.plot(wing_2[0], alt_2[0], 'ko', label= 'initial points')
    final_2 = plt.plot(wing_2[-1], alt_2[-1], 'kx', label= 'final points')
    '''
    plt.legend(loc='upper left')
    plt.savefig(title + ".eps")
    plt.show()

    return


if __name__ == '__main__':
    main()
