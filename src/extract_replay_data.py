import csv
import spawningtool
import sc2reader
import sys
import os
import numpy as np
#import ipdb
import plugins
from sc2helper import *
from spawningtool.parser import GameTimeline

unit_dict_protoss = {   'Probe':            [0, [50,0,1]],
                'MothershipCore':   [1, [100,100,2]],
                'Mothership':       [2, [400,400,8]],
                'Zealot':           [3, [100,0,2]],
                'Stalker':          [4, [125,50,2]],
                'Sentry':           [5, [50,100,2]],
                'HighTemplar':      [6, [50,150,2]],
                'DarkTemplar':      [7, [125,125,2]],
                'Archon':           [8, [175,275,4]],
                'Immortal':         [9, [250,100,4]],
                'Colossus':         [10,[300,200,6]],
                'Observer':         [11,[25,75,1]],
                'Warp Prism':       [12,[200,0,2]],
                'Phoenix':          [13,[150,100,2]],
                'Void Ray':         [14,[250,150,4]],
                'Oracle':           [15,[150,150,3]],
                'Carrier':          [16,[350,250,6]],
                'Tempest':          [17,[300,200,4]],
                'PhotonCannon':     [18,[150,0,0]],
                'Nexus':            [19,[0,0,0]],
                'Pylon':            [20,[0,0,0]],
                'Assimilator':      [21,[0,0,0]],
                'Gateway':          [22,[0,0,0]],
                'Forge':            [23,[0,0,0]],
                'CyberneticsCore':  [24,[0,0,0]],
                'RoboticsFacility': [25,[0,0,0]],   
                'Stargate':         [26,[0,0,0]],
                'TwilightCouncil':  [27,[0,0,0]],
                'RoboticsBay':      [28,[0,0,0]],
                'FleetBeacon':      [29,[0,0,0]],
                'TemplarArchives':  [30,[0,0,0]],
                'DarkShrine':       [31,[0,0,0]],
            }

unit_dict_zerg = {   'Extractor':            [0, [0,0,0]],
                'Hatchery':   [1, [0,0,0]],
                'SpawningPool':       [2, [0,0,0]],
                'Drone': [3, [50,0,1]],
                'Zergling': [4, [50,0,1]]

            }

def extract(replay_file,player_number,label):
    '''
    The 'extract' function takes (1) a replay file and (2) a player number and
    returns the observation vector for that game and that player.

    '''

    unit_dict = unit_dict_zerg

    sc2reader_replay=sc2reader.load_replay(replay_file)

    plugins.EngagementTracker()(sc2reader_replay)

    engagements = sc2reader_replay.eblob

    unit_data=plugins.unit_data['HotS']

    #ipdb.set_trace()

    # Extract build order data from spawningtool
    replay_data = spawningtool.parser.parse_replay(replay_file)

    buildOrder = replay_data['players'][player_number]['buildOrder']
    
    # Initialize the interval observation array. This is the observation vector
    # for a single slice in starcraft time
    observation = [0]*len(unit_dict)
    
    # The build index is the index of the build command, 
    # where build index=0 is the 0th action taken in the build order
    build_index = 0

    total_observations = [None]*(len(buildOrder))
    probe_count = 0
    army_value = 0
    for x in range(0,len(buildOrder)):
        #TODO: Add a "loading" bar... figure out how to do this
        time = (buildOrder[build_index]['time'])
        time = time_string_to_decimals(time)

        # Add the current build command to this interval's observation vector
        current_unit_str = str(buildOrder[build_index]['name'])

        # This 'try' statement checks to see if the current_unit_str is a unit/building,
        # or another type (upgrade, etc.), and increments the corresponding bin by +1 if valid
        try:
            current_unit = unit_dict[current_unit_str];
            current_unit_bin = current_unit[0]
            observation[current_unit_bin]+=1
            
            if current_unit_str =='Drone':
                probe_count += 1
            else:
                army_value += (current_unit[1][0] + current_unit[1][1]) #sum the current unit's mineral and gas value to get army value

        except KeyError:
            pass

        total_observations[build_index]=[time,army_value,probe_count,list(observation[0:3]),label]

        # Increment to the next build event (build index)
        build_index+=1      
    


    return total_observations

    ## RETURN STATEMENT ABOVE RENDERS CODE BELOW USELESS


    '''
    # Generate the filename to save as .csv
    filename_withExt = replay_file.split('\\')[-1]
    filename = filename_withExt.split('.')[0]
    filename_withDest = destination+filename

    # Write the .csv file
    with open(filename_withDest+'(P'+str(player_number)+').csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(total_observations)
    '''

def align(total_observations):
    
    aligned_observations = [None]*total_observations[-1][0]
    n=0
    current_observation = total_observations[n]
    next_observation = list(total_observations[n+1])

    #ipdb.set_trace()

    for current_time in range(0,total_observations[-1][0]):
        if current_time >= int(next_observation[0]):
            n+=1
            current_observation = list(next_observation)
            try: 
                next_observation=list(total_observations[n+1])
            except IndexError:
                pass

        #print(list(current_observation[1:]))
        #print(current_observation[3])
        aligned_observations[current_time]=([current_time]+list(current_observation[1:]))
        #print(aligned_observations[current_time])
    return aligned_observations

def main():
    
    """ Protoss stuff
    test_replays=    ['/home/michael/projects/sc2centaur/data/replays/4gate_5.SC2Replay',
                      '/home/michael/projects/sc2centaur/data/replays/pvz-3gate-pressure.SC2Replay']

    if(len(sys.argv)==1):
        training_replays=['/home/michael/projects/sc2centaur/data/replays/4gate_1.SC2Replay',
                          '/home/michael/projects/sc2centaur/data/replays/4gate_2.SC2Replay',
                          '/home/michael/projects/sc2centaur/data/replays/4gate_3.SC2Replay',
                          '/home/michael/projects/sc2centaur/data/replays/4gate_4.SC2Replay',
                          '/home/michael/projects/sc2centaur/data/replays/self-generated/AI_4gate_opposed.SC2Replay',
                          '/home/michael/projects/sc2centaur/data/replays/self-generated/AI_4gate_unopposed.SC2Replay',
                          '/home/michael/projects/sc2centaur/data/replays/self-generated/AI_robo_attack1.SC2Replay']
        destination='/home/michael/projects/sc2centaur/data/training_data/'
    else:
        training_replays = sys.argv[1]
        destination = sys.argv[2]

    for replay_file in training_replays:
        extract(replay_file,destination,1)
        extract(replay_file,destination,2)

    """

    #test_replay='C:\\sc2centaur\\data\\replays\\4gate_1.SC2Replay'
    #extract(test_replay,'C:\\sc2centaur\\data\\training_data\\',1)
    test_replay2='C:\\sc2centaur\\data\\replays\\pvz-3gate-pressure.SC2Replay'
    #destination ='C:\\sc2centaur\\data\\training_data\\'
    extract(test_replay2,1)

if __name__ == '__main__':
    main()