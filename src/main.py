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
import sc2helper
import keyboardhook
import os
import sys
#import ipdb



                    
feature_dict = sc2helper.get_feature_dict()
dir = os.path.dirname(__file__)

def main(): 
    print("Loading... Please wait.")
    


    #The output_dir is where training data will be saved (in .csv format) so that it can be read manually
    #   for debugging purposes, or read by other components.
    output_dir = os.path.join(dir,'..\\data\\training_data')
    
    #Initialize class instances
    #   sc2c is the "agent" that processes the screen, processes the game data, and generates predictions.
    #   hook is used for listening to keyboard input.
    sc2c = sc2centaur(feature_dict)
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
    #TODO: Is "observation" really even necessary?
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
