"""
==================================
Starcraft Assistive AI: Helper functions
==================================
"""
import csv
import datetime
import math
import operator
import cv2

#The feature_dict contains information about each Starcraft 2 unit.
#   E.g., a 'Drone' has a unit index of 0, and costs 50 minerals, 0 gas, and 1 supply.
#   Unit Name: [index],[mineral-cost, gas-cost, supply-cost]]
feature_dict = {        'Drone':            [0, [50,0,1]],
                        'Extractor':        [1, [0,0,0]],
                        'Hatchery':         [2, [0,0,0]],
                        'SpawningPool':     [3, [0,0,0]],
                        'Zergling':         [4, [50,0,1]]
                        }                       

"""
                        'Probe':            [0, [50,0,1]],
                        'MothershipCore':   [1, [100,100,2]],
                        'Mothership':       [2, [400,400,8]],
                        'Zealot':           [3, [100,0,2]],
                        'Stalker':          [4, [125,50,2]],
                        'Sentry':           [5, [50,100,2]],
                        'HighTemplar':      [6, [50,150,2]],
                        'DarkTemplar':      [7, [125,125,2]],
                        'Archon':           [8, [175,275,4]],
                        'Immortal':         [9, [250,100,4]],
                        'Colossus':         [10,[300,200,6]],
                        'Observer':         [11,[25,75,1]],
                        'Warp Prism':       [12,[200,0,2]],
                        'Phoenix':          [13,[150,100,2]],
                        'Void Ray':         [14,[250,150,4]],
                        'Oracle':           [15,[150,150,3]],
                        'Carrier':          [16,[350,250,6]],
                        'Tempest':          [17,[300,200,4]],
                        'PhotonCannon':     [18,[150,0,0]],
                        'Nexus':            [19,[0,0,0]],
                        'Pylon':            [20,[0,0,0]],
                        'Assimilator':      [21,[0,0,0]],
                        'Gateway':          [22,[0,0,0]],
                        'Forge':            [23,[0,0,0]],
                        'CyberneticsCore':  [24,[0,0,0]],
                        'RoboticsFacility': [25,[0,0,0]],   
                        'Stargate':         [26,[0,0,0]],
                        'TwilightCouncil':  [27,[0,0,0]],
                        'RoboticsBay':      [28,[0,0,0]],
                        'FleetBeacon':      [29,[0,0,0]],
                        'TemplarArchives':  [30,[0,0,0]],
                        'DarkShrine':       [31,[0,0,0]],
"""

def get_feature_dict():
    return feature_dict

def time_string_to_decimals(hhmmss):
    [minutes, seconds] = [int(x) for x in hhmmss.split(':')]
    time = seconds+minutes*60
    return time

def csv_read(file_to_read):
    training_data = []
    with open(file_to_read, 'rb') as csvfile:
        data=[]
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            data.append(row)
        training_data.append(data)
    return training_data

def getNeighbors(trainingSet, testInstance, k):
    #ipdb.set_trace()
    distances = []
    length = len(testInstance)-2 #subtract 2 because the last two indicies in testInstance aren't part of the feature vector
    for x in range(len(trainingSet)):
        dist = euclideanDistance(testInstance, trainingSet[x], length)
        distances.append((trainingSet[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(k):
        neighbors.append(distances[x][0])
        
    return neighbors


def euclideanDistance(instance1, instance2, length):
    distance = 0
    for x in range(length):
        distance += pow((instance1[x]-instance2[x]),2)
    return math.sqrt(distance) 


def getResponse(neighbors):
    classVotes = {}
    for x in range(len(neighbors)):
        response = neighbors[x][-1]
        if response in classVotes:
            classVotes[response]+=1
        else:
            classVotes[response]=1
    sortedVotes = sorted(classVotes.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedVotes[0][0]

