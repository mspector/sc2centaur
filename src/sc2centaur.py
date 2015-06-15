"""
SC2Centaur class

"""
import ipdb
import numpy as np
import cv2
import os
import sc2helper
import sc2reader
import plugins
from os import path

class SC2C(object):

    def __init__(self,training_file_directory):
        "SC2C object initialized..."
        files=[]
        for dirpath,_,filenames in os.walk(training_file_directory):
            for f in filenames:
                files.append(os.path.abspath(os.path.join(dirpath, f)))

        self.training_data = sc2helper.csv_read(files)
        self.n_games = len(self.training_data)
        self.time = None

    def get_time_slice(time):
        # For each game in self.training_data:
        #   Find the latest game state vector
        print("get time slice")


    def classify(self,observation):
        print('Classifying observation...')
        time = observation[0]
        state_vector = observation[1]

    def test_plugins(self,path_to_replay):
        replay=sc2reader.load_replay(path_to_replay)

        army_reader = plugins.ArmyTracker()
        engagement_reader = plugins.EngagementTracker()

        engagement_reader(replay)
        army_reader(replay)

        ipdb.set_trace()




    def vision(image_source):
        img = cv2.imread(image_source)
        h=img.shape[0];
        w=img.shape[1];
        print(img.shape)
        #Assumes 1080x1920 resolution
        img2 = cv2.resize(img,(w/2,h/2))
        info_panel = img[884:1070,370:1365]
        name = info_panel[0:35,400:750]

        nexus_template = cv2.imread('/home/michael/projects/sc2centaur/data/unit_templates/nexus_template.png')

        res = cv2.matchTemplate(info_panel,nexus_template,eval('cv2.TM_CCOEFF'))
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        cv2.imshow('info panel',info_panel)
        cv2.imshow('screenshot',img2)
        cv2.imshow('name',name)

        cv2.waitKey(0)
        cv2.destroyAllWindows()


