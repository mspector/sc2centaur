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



class sc2centaur(object):

    def __init__(self,training_data,numbers_directory,feature_dictionary,template_dictionary):
        "sc2centaur object initialized..."


        self.training_data=training_data

        self.n_games = len(self.training_data)

        self.numbers=[]
        for dirpath,_,filenames in os.walk(numbers_directory):
            for f in filenames:
                im = cv2.imread(os.path.abspath(os.path.join(dirpath, f)),0)
                self.numbers.append(im)

        self.feature_dictionary=feature_dictionary
        self.template_dictionary=template_dictionary

        self.time = None
        
    def classify(self,observation,k):
        
        time = observation[0]
        test_feature_vector = [time]+observation[3]
        training_set = []
        
        for game in self.training_data:
            training_feature_vector = [time]+game[time][3]+[game[time][4]]
            training_set.append(training_feature_vector)
        

        #ipdb.set_trace()
        
        k_nearest_neighbors = sc2helper.getNeighbors(training_set,test_feature_vector, k)    
        label = sc2helper.getResponse(k_nearest_neighbors)
        return label
        


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


    def test_plugins(self,path_to_replay):
        replay=sc2reader.load_replay(path_to_replay)

        army_reader = plugins.ArmyTracker()
        engagement_reader = plugins.EngagementTracker()

        engagement_reader(replay)
        army_reader(replay)

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
        for unit_name in self.feature_dictionary.keys():
            '''
            I'm completely reworking how the "feature dictionary" is used.
            My goal is to have everything refer to a single huge feature_dictionary, held in the main.py script .
            Right now, I'm changing this for loop to loop over the keys in the dictionary.
            This will require me to design the "self.templates" initialization to account for it...
            '''
            #ipdb.set_trace()

            template = self.template_dictionary[unit_name]
            hud_result  = cv2.matchTemplate(hud_img,template,cv2.TM_CCOEFF_NORMED)
            _, hud_max_val, _, _ = cv2.minMaxLoc(hud_result)
            
            if hud_max_val > hud_globalMax:
                hud_globalMax=hud_max_val
                feature_id = unit_name
                print('CURRENT BEST MATCH: '+unit_name)
                print('SCORE: '+str(hud_globalMax))
        try:        
            feature_index = self.feature_dictionary[unit_name][0]
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
            
            '''
            print(minute_result)
            print("Number:"+str(self.numbers[i])+"\n")
            print(np.shape(self.numbers[i]))
            print("Image number:" +str(minute_img)+"\n")
            print(np.shape(minute_img))
            '''

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


    def get_statistics(self,observation_label):
        """
        Input:  a label of a build (e.g., "speedling rush")
        Output: two arrays: one with the army values over time, and the other 
                with the worker count over time for that build
        """

        total_army_stats = []
        total_worker_stats = []
        for game_idx in range(0,len(self.training_data)):
            game_label = self.training_data[game_idx][0][-1]
            army_stats = []
            worker_stats = []
            if game_label == observation_label:
                for observation in self.training_data[game_idx]:
                    army_stats.append(observation[1])
                    worker_stats.append(observation[2])
            total_army_stats.append(army_stats)
            total_worker_stats.append(worker_stats)
        return total_army_stats,total_worker_stats
    

    '''
    I'm not sure which of these classes below are actually used anymore
    '''
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
        '''
        ONLY WORKS with three dimensional features!

        '''  

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


    '''
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
