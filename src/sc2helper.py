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
def time_string_to_decimals(hhmmss):
    [minutes, seconds] = [int(x) for x in hhmmss.split(':')]
    #time = datetime.timedelta(minutes=minutes, seconds=seconds)
    time = seconds+minutes*60
    return time

def csv_read(files):
    training_data =[]
    for filename in files:
        vectors = []
        with open(filename, 'rb') as csvfile:
            data=[]
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                row[0]=time_string_to_decimals(row[0])
                data.append(row)
            vectors.append(data)
        training_data.append(vectors)
    return training_data

def euclideanDistance(instance1, instance2, length):
    distance = 0
    for x in range(length):
        distance += pow((instance1[x]-instance2[x]),2)
    return math.sqrt(distance) 


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

