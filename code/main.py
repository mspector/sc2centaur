"""
==================================
Starcraft Assistive AI
==================================
"""
print(__doc__)

from sc2centaur import *

def main():	
	
	observation = ['6:58', '[13, 0, 0, 4, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 1, 4, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]']
	training_directory="/home/michael/projects/sc2centaur/data/training_data/"

	sc2c = SC2C(training_directory)

	sc2c.classify(observation)

	test_replay = '/home/michael/projects/sc2centaur/data/replays/4gate_1.SC2Replay'
	sc2c.test_plugins(test_replay)

if __name__ == '__main__':
    main()