"""
==================================
Starcraft Assistive AI: sc2centaur class
==================================

"""
import ipdb
import numpy as np
import cv2
import os
import sc2helper
import sc2reader
import plugins
from os import path
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from custom_drawMatches import drawMatches


#The sc2centaur class represents an agent that is responsible for reading the player's screen, 
#   classifying the opponent's behavior, and generating predictions. It is intended as an intelligent
#   assistant that has "expert knowledge" of Starcraft II player behavior, and therefore contains the 
#   training data for the classification. 


#Set data locations
#   replay_dir contains the replays that are used as training data.
#   template_dir contains the template images of the units and buildings on the screen.
#   numbers_dir contains the template images of numbers used for reading the game time.
dir = os.path.dirname(__file__)
replay_dir   = os.path.join(dir,'..','data','training_replays')
template_dir = os.path.join(dir,'..','data','templates')
numbers_dir  = os.path.join(dir,'..','data','numbers')
training_data_dir = os.path.join(dir,'..','data','training_data')

class sc2centaur(object):


    def __init__(self, feature_dict):
        

        #TODO: 
        #The SC2Centaur should read data from the csv files. 
        #Remove the line below and replace it with a .csv reading function.
        #pca.py will hold the function that writes the replays to .csv format.
        self.feature_dict=feature_dict
        
        self.training_data={'Protoss': [], 'Terran': [], 'Zerg': []}
        for race in ['Protoss','Terran','Zerg']:
            race_dir = os.path.join(training_data_dir,race)
            for dirpath,_,filenames in os.walk(race_dir):
                for f in filenames:
                    replay_data = sc2helper.csv_read(os.path.join(race_dir,f))
                    self.training_data[race].append(replay_data)

        self.n_games = len(self.training_data)

        self.numbers=[]
        for dirpath,_,filenames in os.walk(numbers_dir):
            for f in filenames:
                im = cv2.imread(os.path.abspath(os.path.join(dirpath, f)),0)
                self.numbers.append(im)

        self.template_dict={}
        for dirpath,_,filenames in os.walk(template_dir):
            for unit_name in feature_dict:
                #print(unit_name)
                im = cv2.imread(os.path.join(template_dir,unit_name+'.png'), 0)
                self.template_dict[unit_name]=im

        self.time = None
    
    def read_hud(self,path):
        img = cv2.imread(path,0) # total image
        x_min = 2740
        x_max = 2980
        y_min = 898
        y_max = 917

        hud_img = img[y_min:y_max,x_min:x_max]

        #cv2.imshow("hud",hud_img)
        hud_globalMax = 0
        feature_id = None
        for unit_name in self.feature_dict.keys():

            template = self.template_dict[unit_name]
            hud_result  = cv2.matchTemplate(hud_img,template,cv2.TM_CCOEFF_NORMED)
            _, hud_max_val, _, _ = cv2.minMaxLoc(hud_result)
            
            if hud_max_val > hud_globalMax:
                hud_globalMax=hud_max_val
                feature_id = unit_name
                #print('CURRENT BEST MATCH: '+unit_name)
                #print('SCORE: '+str(hud_globalMax))
        try:        
            feature_index = self.feature_dict[unit_name][0]
        except KeyError:
            feature_id = None
            feature_index = None

        return feature_id,feature_index


    def read_time(self,path):

        img = cv2.imread(path,0) # total image

        x_min = 2195
        x_max = 2208
        y_min = 783
        y_max = 794
        minute_img = img[y_min:y_max,x_min:x_max]
        
        x_min = 2216
        x_max = 2229
        second1_img= img[y_min:y_max,x_min:x_max]

        x_min = 2232
        x_max = 2245
        second2_img= img[y_min:y_max,x_min:x_max]

        minute  = None
        second1 = None
        second2 = None

        minute_globalMax  = 0
        second1_globalMax = 0
        second2_globalMax = 0

        for i in range(0,10):
            minute_result  = cv2.matchTemplate(minute_img,self.numbers[i],cv2.TM_CCOEFF_NORMED)
            second1_result = cv2.matchTemplate(second1_img,self.numbers[i],cv2.TM_CCOEFF_NORMED)
            second2_result = cv2.matchTemplate(second2_img,self.numbers[i],cv2.TM_CCOEFF_NORMED)

            minute_min_val, minute_max_val, a, b = cv2.minMaxLoc(minute_result)
            second1_min_val, second1_max_val, a, b = cv2.minMaxLoc(second1_result)
            second2_min_val, second2_max_val, a, b = cv2.minMaxLoc(second2_result)

            if minute_max_val > minute_globalMax:
                minute_globalMax = minute_max_val
                minute = i

            if second1_max_val > second1_globalMax:
                second1_globalMax = second1_max_val
                second1 = i

            if second2_max_val > second2_globalMax:
                second2_globalMax = second2_max_val
                second2 = i

        #print("Time---> "+str(minute)+":"+str(second1)+str(second2))

        return [minute,second1,second2]

    #classify needs some work.
    #should it ingest an 'observation', or a bunch of variables that make up an observation? that might make it clearer what's happening inside
    #The classification algorithm may be flawed. Right now it does K-nearest neighbors on a training set consisting exclusively of feature 
    #vectors that happen at the exact same game time.
    def classify(self,observation,k):
        ipdb.set_trace()
        time = observation[0]
        test_feature_vector = [time]+observation[3]#observation[3] is the feature vector
        training_set = []
        
        #This shouldn't be hardcoded in the future
        race='Zerg'
        for games in self.training_data[race]:
            for g in games:
                training_feature_vector = [time]+g[time][3]+[g[time][4]]
                training_set.append(training_feature_vector)
        

        #ipdb.set_trace()
        
        k_nearest_neighbors = sc2helper.getNeighbors(training_set,test_feature_vector, k)    
        label = sc2helper.getResponse(k_nearest_neighbors)
        return label

    def get_statistics(self,observation_label):
        """
        Input:  a label of a build (e.g., "speedling rush")
        Output: two arrays: one with the army values over time, and the other 
                with the worker count over time for that build
        """
        total_army_stats = []
        total_worker_stats = []

        #This shouldn't be hardcoded in the future
        race = 'Zerg'

        
        for game_idx in range(0,len(self.training_data[race])):
            game_label = self.training_data[race][game_idx][0][-1]
            army_stats = []
            worker_stats = []
            if game_label == observation_label:
                for observation in self.training_data[race][game_idx]:
                    army_stats.append(observation[1])
                    worker_stats.append(observation[2])
            total_army_stats.append(army_stats)
            total_worker_stats.append(worker_stats)
        return total_army_stats,total_worker_stats

    def plot_statistics(self,army_stats,worker_stats):
        '''
        Plots stats. Right now only plots army value over time.
        '''  
             
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        for game_idx in range(0,len(army_stats)):
            ax.scatter(range(0,len(army_stats[game_idx])), army_stats[game_idx])

        ax.set_xlabel('Game Time (sec)')
        ax.set_ylabel('Army Value (minerals + gas)')

        return plt



    '''
    I'm not sure which of these classes below are actually used anymore


    def test_plugins(self,path_to_replay):
        replay=sc2reader.load_replay(path_to_replay)

        army_reader = plugins.ArmyTracker()
        engagement_reader = plugins.EngagementTracker()

        engagement_reader(replay)
        army_reader(replay)

    def get_feature(self,f):
        all_features=[]
        for game in range(0,len(self.training_data)):
            feature = []
            for observation in self.training_data[game]:
                feature.append(observation[3][f])
            feature=[observation[4],feature]
            all_features.append(feature)
        return all_features

    def plot_training_data(self):
        ##ONLY WORKS with three dimensional features!
  

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        xs = self.get_feature(0)
        ys = self.get_feature(1)
        zs = self.get_feature(2)
        
        for game in range(0,len(self.training_data)):
            ax.scatter(xs[game][1], ys[game][1], zs[game][1])

        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')

        plt.show()


    def find_nexus(self,path):
        print("Identifying nexus...")
        self.nexus = False
        MIN_MATCH_COUNT = 15

        img1 = cv2.imread('C:\\sc2centaurentaur\\data\\Nexus_Template.jpg',0)          # queryImage
        img2 = cv2.imread(path,0) # trainImage

        # Initiate SIFT detector
        sift = cv2.SIFT()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1,des2,k=2)

        # store all the good matches as per Lowe's ratio test.
        good = []
        for m,n in matches:
            if m.distance < 0.72*n.distance:
                good.append(m)

        if len(good)>MIN_MATCH_COUNT:
            self.nexus = True
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()

            h,w = img1.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts,M)

            cv2.polylines(img2,[np.int32(dst)],True,255,3)

        else:
            print "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)
            matchesMask = None

        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                           singlePointColor = None,
                           matchesMask = matchesMask, # draw only inliers
                           flags = 2)

        img3 = drawMatches(img1,kp1,img2,kp2,good)
        return self.nexus


        #plt.imshow(img3, 'gray'),plt.show()

'''
