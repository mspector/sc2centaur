import numpy as np
import cv2
from custom_drawMatches import drawMatches
from matplotlib import pyplot as plt

img1 = cv2.imread('C:\\sc2centaur\\data\\Nexus_SC2_DevRend3.jpg',0)          # queryImage
img2 = cv2.imread("C:\\sc2centaur\\observations\\observation-0.bmp",0) # trainImage

# Initiate SIFT detector
sift = cv2.SIFT()

# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)

# BFMatcher with default params
bf = cv2.BFMatcher()
matches = bf.knnMatch(des1,des2, k=2)

# Apply ratio test
good = []
for m,n in matches:
    if m.distance < 0.75*n.distance:
        good.append(m)

print(good)

print(matches[0][1].queryIdx)
# cv2.drawMatchesKnn expects list of lists as matches.
img3 = drawMatches(img1,kp1,img2,kp2,good)

plt.imshow(img3),plt.show()