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

def main(): 
    training_directory ="C:\\sc2centaur\\data\\training_data"
    templates_directory="C:\\sc2centaur\\data\\templates"
    numbers_directory  ="C:\\sc2centaur\\data\\numbers"
    observation = ['6:58', '[13, 0, 0, 4, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 1, 4, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]']
    key = None

    hook = keyboardhook.GlobalInput()
    sc2c = SC2C(training_directory,templates_directory,numbers_directory)

    while key != 'Snapshot':
        key = hook.getKey()

    print('success')
    nexus_identified = sc2c.find_buildings('observations\\observation.bmp')
    #time = sc2c.get_game_time()
    time = "<insert time here>"
    if nexus_identified:
        print("Enemy expansion identified at T="+time)
    else:
        print("No expansion detected.")
    #test_replay = '/home/michael/projects/sc2centaur/data/replays/4gate_1.SC2Replay'
    #sc2c.test_plugins(test_replay)

if __name__ == '__main__':
    main()