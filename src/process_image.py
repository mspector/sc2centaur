
def extract_templates(path,out):
    img = cv2.imread(path,3) # total image

    x_min = 2740
    x_max = 2980
    y_min = 898
    y_max = 917

    template = img[y_min:y_max,x_min:x_max]
    cv2.imwrite(out,template)

def extract_numbers(path,out):
    img = cv2.imread(path,3) # total image
    x_min = 2195
    x_max = 2209
    y_min = 783
    y_max = 795
    minute_img = img[y_min:y_max,x_min:x_max]
    
    x_min = 2216
    x_max = 2230
    second1_img= img[y_min:y_max,x_min:x_max]

    x_min = 2232
    x_max = 2246
    second2_img= img[y_min:y_max,x_min:x_max]

    cv2.imwrite(out+'min.png',minute_img)
    cv2.imwrite(out+'sec1.png',second1_img)
    cv2.imwrite(out+'sec2.png',second2_img)

import replay_extractor
import os
replays_directory = 'C:\\Users\\Michael\\Documents\\projects\\sc2centaur\\data\\training_replays'
replay_extractor.process_directory(replays_directory)