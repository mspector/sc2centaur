"""
This script is used to test key codes for the cv2.waitKey function.

Press any key to get it's value. Escape (33) will exit the program.
"""

import cv2
img = cv2.imread('/home/michael/projects/sc2centaur/data/unit_templates/nexus_template.png') # load a dummy image
while(1):
    cv2.imshow('img',img)
    k = cv2.waitKey(33)
    if k==27:    # Esc key to stop
        break
    elif k==-1:  # normally -1 returned,so don't print it
        continue
    else:
        print k # else print its value