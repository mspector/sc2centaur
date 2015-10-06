"""
SC2Centaur class

Methods:
classify

"""
#import ipdb
import numpy as np
import cv2
import os
import sc2helper
import sc2reader
import plugins
import extract_replay_data
from os import path
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from custom_drawMatches import drawMatches


class SC2C(object):

    def __init__(self,training_file_directory,templates_directory,numbers_directory):
        "SC2C object initialized..."

        self.training_data=[]
        for dirpath,_,filenames in os.walk(training_file_directory):
            for f in filenames:
                filepath = os.path.abspath(os.path.join(dirpath, f))
                #print(filepath)
                label = f
                data = extract_replay_data.extract(filepath,1,label)
                aligned_data = extract_replay_data.align(data)
                self.training_data.append(aligned_data)


        #self.training_data = sc2helper.csv_read(files)

        self.n_games = len(self.training_data)
        
        self.templates=[]
        for dirpath,_,filenames in os.walk(templates_directory):
            for f in filenames:
                im = cv2.imread(os.path.abspath(os.path.join(dirpath, f)),0)
                self.templates.append(im)

        self.numbers=[]
        for dirpath,_,filenames in os.walk(numbers_directory):
            for f in filenames:
                im = cv2.imread(os.path.abspath(os.path.join(dirpath, f)),0)
                self.numbers.append(im)

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

    def read_hud(self,path,feature_dictionary):
        #ipdb.set_trace()
        img = cv2.imread(path,0) # total image

        x_min = 570
        x_max = 760
        y_min = 630
        y_max = 670

        hud_img = img[y_min:y_max,x_min:x_max]

        #cv2.imshow("hud",hud_img)
        #cv2.imshow("template",self.templates[2])

        hud_globalMax = 0
        feature_index = None
        for i in range(0,3):
            hud_result  = cv2.matchTemplate(hud_img,self.templates[i],cv2.TM_CCOEFF_NORMED)
            _, hud_max_val, _, _ = cv2.minMaxLoc(hud_result)
            
            if hud_max_val > hud_globalMax:
                hud_globalMax=hud_max_val
                feature_index = i
        try:        
            feature_id = feature_dictionary[feature_index]
        except KeyError:
            feature_id = None
            feature_index = None

        return feature_id,feature_index

    def read_time(self,path):

        img = cv2.imread(path,0) # total image

        x_min = 192
        x_max = 207
        y_min = 552
        y_max = 567
        minute_img = img[y_min:y_max,x_min:x_max]
        
        x_min = 192+18
        x_max = 207+18
        second1_img= img[y_min:y_max,x_min:x_max]

        x_min = 192+18+15
        x_max = 207+18+15
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

    '''
    def find_nexus(self,path):
        print("Identifying nexus...")
        self.nexus = False
        MIN_MATCH_COUNT = 15

        img1 = cv2.imread('C:\\sc2centaur\\data\\Nexus_Template.jpg',0)          # queryImage
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
