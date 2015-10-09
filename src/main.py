"""

==================================
Starcraft Assistive AI
==================================

The Starcraft Assistive AI encodes Starcraft II knowledge and uses it to generate predictions.

Press the "Print Screen" key while in-game to capture the screen for processing.
Press "Escape" to quit.

**Your instance of Starcraft must be running in full-screen windowed mode!**
=============================================
"""
print(__doc__)

from sc2centaur import *
import keyboardhook
import os
import sys
import data_extractor
import ipdb

feature_dictionary = {  #'Drone':            [0, [50,0,1]],
                        'Extractor':        [0, [0,0,0]],
                        'Hatchery':         [1, [0,0,0]],
                        'SpawningPool':     [2, [0,0,0]]
                        #'Zergling':         [4, [50,0,1]]
                        }   

"""
                        'Probe':            [0, [50,0,1]],
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
"""
                    

dir = os.path.dirname(__file__)

def main(): 
    

    print("Loading... Please wait.")
    
    #### Set data locations
    replay_directory = os.path.join(dir,'..\\data\\training_replays')
    training_directory = os.path.join(dir,'..\\data\\training_data')
    template_directory = os.path.join(dir,'..\\data\\templates')
    numbers_directory  =os.path.join(dir,'..\\data\\numbers')
    
    training_data = data_extractor.process_replays(replay_directory,feature_dictionary)
    template_dictionary = data_extractor.process_templates(template_directory,feature_dictionary)

    #feature_dictionary = {0:"Extractor", 1:"Hatchery", 2:"Spawning Pool"}

    #### Initialize class instances
    sc2c = sc2centaur(training_data, numbers_directory, feature_dictionary, template_dictionary)
    hook = keyboardhook.GlobalInput()
    
    #### Initialize parameters
    feature_vector = [0,0,0]
    unlocked = True
    max_screenshots = 2
    screenshots_taken = 0
    key = None
    
    print("\nWaiting for image. Take a screenshot\n")
    
    #### Until enough screenshots are gathered, listen for the "print screen" key
    while unlocked:
        while key != 'Snapshot':
            key = hook.getKey()
        
        key = None

        #### When "print screen" is pressed, read the HUD to identify buildings, here referred to as "features"
        if len(sys.argv)==1:
            filename = os.path.join(dir,'..\\observations\\observation.bmp')
        elif sys.argv[1]=='--debug':
            obs_name = input('Enter observation name: ')
            filename = os.path.join(dir,'..\\observations\\'+obs_name+'.bmp')

        feature_name, feature_index = sc2c.read_hud(filename)

        if(feature_name == None):
            print("No valid buildings detected.")
            pass
        else:
        #### If there's a valid building in the screenshot, increment that building's corresponding bin in the feature vector   
            feature_vector[feature_index]+=1

        #### Read the time and convert it to seconds
            time = sc2c.read_time(filename)
            seconds = time[0]*60+time[1]*10+time[2]

        #### If a valid building was captured, increment the "lock timer" by one, so that the loop will stop after the desired number of screenshots    
            screenshots_taken+=1
            if screenshots_taken>=max_screenshots:
                unlocked = False

            print(feature_name+" detected ("+str(screenshots_taken)+"/"+str(max_screenshots)+" screenshots)")
            
    #### Using the feature vector generated from the screenshots, compile this information into an "observation," 
    observation = [seconds, None, None, feature_vector, 'in-game observation']
    
    #### ...and use it to classify the observed in-game behavior of your opponent
    label = sc2c.classify(observation,1)
    print("Predicted build: "+label)
    
    #### Then gather statistics about similar builds and provide data about army value over time.
    army_stats, worker_stats = sc2c.get_statistics(label)
    plt = sc2c.plot_statistics(army_stats,worker_stats)

    plt.show()


if __name__ == '__main__':
    main()
