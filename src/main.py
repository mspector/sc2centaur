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
#import ipdb


#The feature_dict contains information about each Starcraft 2 unit.
#   E.g., a 'Drone' has a unit index of 0, and costs 50 minerals, 0 gas, and 1 supply.
#   Unit Name: [index],[mineral-cost, gas-cost, supply-cost]]
feature_dict = {  'Drone':            [0, [50,0,1]],
                        'Extractor':        [1, [0,0,0]],
                        'Hatchery':         [2, [0,0,0]],
                        'SpawningPool':     [3, [0,0,0]],
                        'Zergling':         [4, [50,0,1]]
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
    
    #Set data locations
    #   replay_dir contains the replays that are used as training data.
    #   template_dir contains the template images of the units and buildings on the screen.
    #   numbers_dir contains the template images of numbers used for reading the game time.
    replay_dir   = os.path.join(dir,'..\\data\\training_replays')
    template_dir = os.path.join(dir,'..\\data\\templates')
    numbers_dir  = os.path.join(dir,'..\\data\\numbers')

    #The output_dir is where training data will be saved (in .csv format) so that it can be read manually
    #   for debugging purposes, or read by other components.
    output_dir = os.path.join(dir,'..\\data\\training_data')
    
    template_dict = data_extractor.process_templates(template_dir,feature_dict)
    training_data = data_extractor.process_replays(replay_dir,feature_dict,output_dir)

    #Initialize class instances
    #   sc2c is the "agent" that processes the screen, processes the game data, and generates predictions.
    #   hook is used for listening to keyboard input.
    sc2c = sc2centaur(training_data, numbers_dir, feature_dict, template_dict)
    hook = keyboardhook.GlobalInput()
    
    #Initialize the feature_vector.
    #   It will store the features detected from screenshots of the current game.
    feature_vector = [0]*len(feature_dict)
    
    #Initialize flow control variables
    loop_unlocked = True
    max_screenshots = 2
    screenshots_taken = 0
    key = None
    

    #The main loop listens for the "print screen" key, until a set number of units or buildings are screen captured.
    while loop_unlocked:
    
        if screenshots_taken == 0:
            print("\nPlease take screenshots of "+str(max_screenshots)+" enemy units and/or buildings.") 
        print("\nWaiting for image. Press PrintScreen...\n")

        #Listen for the "print screen" key
        while key != 'Snapshot':
            key = hook.getKey()
        
        key = None

        #(This block of code enables the "--debug" flag. This bypasses the part of the code that captures the current screen image.
        #Instead, it replaces the image with the image of the user's choosing.)
        if len(sys.argv)==1:
            filename = os.path.join(dir,'..\\observations\\observation.bmp')
        elif sys.argv[1]=='--debug':
            obs_name = input('Enter observation name: ')
            filename = os.path.join(dir,'..\\observations\\'+obs_name+'.bmp')

        #When "print screen" is pressed, read the HUD to identify buildings, here referred to as "features"
        feature_name, feature_index = sc2c.read_hud(filename)

        #If no valid buildings were detected in the screenshot, exit the loop and wait for a new screenshot. 
        #Otherwise, increment that building's corresponding bin in the feature vector.
        if(feature_name == None):
            print("No valid buildings detected.")
            pass
        else:
            feature_vector[feature_index]+=1

            #Read the time and convert it to a game time (measured in seconds)
            time = sc2c.read_time(filename)
            game_time = time[0]*60+time[1]*10+time[2]

            #If a valid building was captured, increment the "lock timer" by one, so that the loop will stop after the desired number of screenshots    
            screenshots_taken+=1
            #If the maximum number of screenshots is reached, lock the loop by setting "loop_unlocked" to False
            if screenshots_taken>=max_screenshots:
                loop_unlocked = False

            print(feature_name+" detected ("+str(screenshots_taken)+"/"+str(max_screenshots)+" screenshots)")
            
    #Using the feature vector generated from the screenshots, compile this information into an "observation."
    observation = [game_time, None, None, feature_vector, 'in-game observation']
    
    #Use the observation to classify the observed in-game behavior of the opponent.
    label = sc2c.classify(observation,1)
    print("Predicted build: "+label)
    
    #### Then gather statistics about similar builds and provide data about army value over time.
    army_stats, worker_stats = sc2c.get_statistics(label)
    plt = sc2c.plot_statistics(army_stats,worker_stats)

    plt.show()


if __name__ == '__main__':
    main()
