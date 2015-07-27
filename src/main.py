"""
=============================================
~~Starcraft Assistive AI~~

The Starcraft Assistive AI encodes Starcraft II knowledge and uses it to generate predictions.

Press the "Print Screen" key while in-game to capture the screen for processing.
Press "Escape" to quit.

**You must be in full-screen windowed mode!**
=============================================
"""
print(__doc__)

from sc2centaur import *
import keyboardhook
#import ipdb
def main(): 
    
    print("Loading... Please wait.")
    
    #### Set data locations
    training_directory ="C:\\sc2centaur\\data\\training_replays"
    templates_directory="C:\\sc2centaur\\data\\templates"
    numbers_directory  ="C:\\sc2centaur\\data\\numbers"
    
    #### Initialize class instances
    sc2c = SC2C(training_directory,templates_directory,numbers_directory)
    hook = keyboardhook.GlobalInput()
    
    #### Initialize parameters
    feature_vector = [0,0,0]
    unlocked = True
    max_screenshots = 2
    lock_timer = 0
    key = None
    
    print("\nWaiting for image. Take a screenshot\n")
    
    #### Until enough screenshots are gathered, listen for the "print screen" key
    while unlocked:
        while key != 'Snapshot':
            key = hook.getKey()
        
        key = None

        #TODO: Figure out a more elegant way to handle passing the feature dictionary between this location and "extract_replay_data.py"
        feature_dictionary = {0:"Extractor", 1:"Hatchery", 2:"Spawning Pool"}

        #### When "print screen" is pressed, read the HUD to identify buildings, here referred to as "features"
        feature_name, feature_index = sc2c.read_hud('C:\\sc2centaur\\observations\\observation.bmp',feature_dictionary)
        
        if(feature_name == None):
            print("No valid buildings detected.")
            pass
        else:
        #### If there's a valid building in the screenshot, increment that building's corresponding bin in the feature vector   
            feature_vector[feature_index]+=1

        #### ...then read the time and convert it to seconds
            time = sc2c.read_time('C:\\sc2centaur\\observations\\observation.bmp')
            seconds = time[0]*60+time[1]*10+time[2]

        #### If a valid building was captured, increment the "lock timer" by one, so that the loop will stop after the desired number of screenshots    
            lock_timer+=1
            if lock_timer>=max_screenshots:
                unlocked = False

            print(feature_name+" detected ("+str(lock_timer)+"/"+str(max_screenshots)+" screenshots)")
            
    #### Using the feature vector generated from the screenshots, compile this information into an "observation," 
    #### and use it to classify the observed in-game behavior of your opponent
    observation = [seconds, None, None, feature_vector, 'in-game observation']
    label = sc2c.classify(observation,1)
    print("Predicted build: "+label)
    
    #### Then gather statistics about similar builds and provide data about army value over time.
    army_stats, worker_stats = sc2c.get_statistics(label)
    plt = sc2c.plot_statistics(army_stats,worker_stats)

    plt.show()


if __name__ == '__main__':
    main()