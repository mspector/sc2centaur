import csv
import spawningtool
import sc2reader
import sys
import os
import numpy as np
import plugins
import cv2
#import ipdb
from sc2helper import *
from spawningtool.parser import GameTimeline


dir = os.path.dirname(__file__)

def extract_replays(replay_file,player_number,label,feature_dictionary):
    '''
    The '' function takes (1) a replay file and (2) a player number and
    returns the observation vector for that game and that player.

    '''

    sc2reader_replay = sc2reader.load_replay(replay_file)

    plugins.EngagementTracker()(sc2reader_replay)

    engagements = sc2reader_replay.eblob

    unit_data = plugins.unit_data['HotS']

    #ipdb.set_trace()

    # Extract build order data from spawningtool
    replay_data = spawningtool.parser.parse_replay(replay_file)

    buildOrder  = replay_data['players'][player_number]['buildOrder']
    race = replay_data['players'][player_number]['race']
    
    # Initialize the interval observation array. This is the observation vector
    # for a single slice in starcraft time
    observation = [0]*len(feature_dictionary)

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
            current_unit = feature_dictionary[current_unit_str];
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
    


    return [total_observations,race]


def align_replays(total_observations):
    
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

def process_replays(replay_directory,feature_dictionary):
    
    #ipdb.set_trace()
    training_data={'Protoss':[], 'Zerg':[], 'Terran':[]}
    data_directory = os.path.join(dir,'..\\data\\training_data')

    for dirpath,_,filenames in os.walk(replay_directory):
        for f in filenames:
            filepath = os.path.abspath(os.path.join(dirpath, f))
            #print(filepath)
            
            #Replays should be in the following format:
            #X-build.SC2Replay
            #Where X is P, Z, or T 
            label = f.split('-')[1]
            fileprefix = f.split('.')[0]

            for player in [1, 2]:
                [data,race] = extract_replays(filepath,player,label,feature_dictionary)
                aligned_data = align_replays(data)
                
                training_data[race].append(aligned_data)

                    
                with open(data_directory+'\\'+race+'\\'+fileprefix+'.csv', 'wb') as csvfile:
                    csvwriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    csvwriter.writerows(data)

    return training_data

def process_templates(template_directory,feature_dictionary):
    template_dictionary={}

    for dirpath,_,filenames in os.walk(template_directory):
        for unit_name in feature_dictionary:
            #print(unit_name)
            im = cv2.imread(template_directory+'\\'+unit_name+'.png',0)
            template_dictionary[unit_name]=im

    return template_dictionary



def main():
    replay_directory = 'C:\\Users\\Michael\\Documents\\projects\\sc2centaur\\data\\training_replays'
    process_replays(replay_directory)

if __name__ == '__main__':
    main()