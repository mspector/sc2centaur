#from IPython import embed

import json
import spawningtool
import sys
import os
import numpy as np
from spawningtool.parser import GameTimeline

#Argument 1: replay directory (source)
#Argument 2: json directory (target)



#unit_dict should eventually be made into a global variable across the whole project
unit_dict = {   'Probe':            0,
                'MothershipCore':   1,
                'Mothership':       2, 
                'Zealot':           3,
                'Stalker':          4,
                'Sentry':           5,
                'HighTemplar':      6,
                'DarkTemplar':      7,
                'Archon':           8,
                'Immortal':         9,
                'Colossus':         10,
                'Observer':         11,
                'Warp Prism':       12,
                'Phoenix':          13,
                'Void Ray':         14,
                'Oracle':           15,
                'Carrier':          16,
                'Tempest':          17,
                'Nexus':            18,
                'Pylon':            19,
                'Assimilator':      20,
                'Gateway':          21,
                'Forge':            22,
                'CyberneticsCore':  23,
                'PhotonCannon':     24,
                'RoboticsFacility': 25,    
                'Stargate':         26,
                'TwilightCouncil':  27,
                'RoboticsBay':      28,
                'FleetBeacon':      29,
                'TemplarArchives':  30,
                'DarkShrine':       31,
            }


def time_string_to_decimals(time_string):
    fields = time_string.split(":")
    hours = fields[0] if len(fields) > 0 else 0.0
    minutes = fields[1] if len(fields) > 1 else 0.0
    seconds = fields[2] if len(fields) > 2 else 0.0

    return (float(hours) + (float(minutes) / 60.0) + (float(seconds) / pow(60.0, 2)))


def extract(replay_file,player_number):
    '''
    The 'extract' function takes (1) a replay file and (2) a player number and
    returns the observation vector for that game and that player.

    '''
    replay_data=spawningtool.parser.parse_replay(replay_file)

    player1_buildOrder = replay_data['players'][player_number]['buildOrder']

    intervals = np.arange(.5,10.5,0.5)
                            # The 'intervals' array gives the starting/stopping times for each 
                            #   interval (in decimal: e.g. 3:30 = 3.50). The 'while' loop below
                            #   uses this array to check which interval the current game time is assigned to.
    
    interval_observation = np.zeros([1,len(unit_dict)],dtype=int)
                            # Initialize the interval observation array. This is the observation vector
                            #   for an individual 30-second interval. It will be re-initialized in the
                            #   while loop

    total_observations = np.zeros([len(intervals),len(unit_dict)],dtype=int)

    time = 0
    
    build_index = 0         # The build index is the index of the build command, 
                            #   where build index=0 is the 0th action taken in the build order

    interval_index = 0      # The interval index is the index of the current 30 second interval.
                            #   if interval index=0, the current build command is happening between 
                            #   0 and 30 seconds in the game. Corresponds to 'intervals' array.

    while(time<10.00):

        time = time_string_to_decimals(player1_buildOrder[build_index]['time'])

        if( time > intervals[interval_index] ):
            total_observations[interval_index,:]=interval_observation
                            # Add the previous interval's observation vector to 'total_observations'

            interval_index+=1
                            # Increment 'interval_index' when the interval changes

            interval_observation = np.zeros([1,len(unit_dict)],dtype=int) 
                            # Re-initialize the interval observation array when the interval changes
            
        current_unit_str = str(player1_buildOrder[build_index]['name'])
                            # Add the current build command to this interval's observation vector

        try:
            current_unit_bin = unit_dict[current_unit_str]
            interval_observation[0,current_unit_bin]=1 #set to 1 to indicate the unit was built vs not built
        except KeyError:
            pass
                            # This 'try' statement checks to see if the current_unit_str is a unit/building,
                            # or another type (upgrade, etc.)

        build_index+=1      # Increment to the next build event (build index)

    return total_observations


def main():
    
    replay_dir = sys.argv[1]
    json_dir = sys.argv[2]


    for subdir, dirs, files in os.walk(replay_dir):
        for file in files:
            
            replay_file = os.path.join(subdir, file)

            #player1_observations = extract(replay_file,1)
            player2_observations = extract(replay_file,2)

            print(player2_observations)

if __name__ == '__main__':
    main()