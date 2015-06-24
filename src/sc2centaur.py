"""
SC2Centaur class

"""
#import ipdb
import numpy as np
import cv2
import os
import sc2helper
import sc2reader
import plugins
from os import path
from matplotlib import pyplot as plt
from custom_drawMatches import drawMatches

class SC2C(object):

    def __init__(self,training_file_directory,templates_directory,numbers_directory):
        "SC2C object initialized..."
        files=[]
        for dirpath,_,filenames in os.walk(training_file_directory):
            for f in filenames:
                files.append(os.path.abspath(os.path.join(dirpath, f)))

        self.training_data = sc2helper.csv_read(files)
        self.n_games = len(self.training_data)
        
        self.templates=[]
        for dirpath,_,filenames in os.walk(templates_directory):
            for f in filenames:
                im = cv2.imread(os.path.abspath(os.path.join(dirpath, f)))
                self.templates.append(im)

        self.numbers=[]
        for dirpath,_,filenames in os.walk(numbers_directory):
            for f in filenames:
                im = cv2.imread(os.path.abspath(os.path.join(dirpath, f)))
                self.numbers.append(im)

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

    def read_hud(self,path):
        print("Reading HUD...")
        img = cv2.imread(path,0) # total image
        x_max = 330
        x_min = 275
        y_max = 795
        y_min = 775
        hud = img[y_min:y_max,x_min:x_max]
        return hud






    def read_time(self,path):
        print("Reading game time...")
        img = cv2.imread(path,0) # total image
        x_max = 330
        x_min = 275
        y_max = 794
        y_min = 779
        time_img = img[y_min:y_max,x_min:x_max]

        x_max = 290
        x_min = 275
        cv2.imshow("2",self.numbers[0])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        result = cv2.matchTemplate(time_img,self.numbers[0],cv2.TM_CCOEFF_NORMED)
        return time_img






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