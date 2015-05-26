"""
==================================
Starcraft Assistive AI
==================================
"""
import ipdb
import datetime
import numpy as np
import pylab as pl
import operator
import cv2
from extract_replay_data import extract
from hmmlearn.hmm import MultinomialHMM
from hmmlearn.utils import normalize
from matplotlib import pyplot as plt
print(__doc__)

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



def learn(): #replay_dir
	'''
    for subdir, dirs, files in os.walk(replay_dir):
        for file in files:
            
            replay_file = os.path.join(subdir, file)

            #player1_observations = extract(replay_file,1)
            player2_observations = extract(replay_file,2)

            print(player2_observations)
    '''
	X = extract('../data/replays/pvz-3gate-pressure.SC2Replay',2)
	print("Game observations extracted:")
	print(X)

	###############################################################################
	# Run Multinomial HMM
	print("fitting to HMM and decoding ...")

	# make an HMM instance and execute fit
	model = MultinomialHMM(n_components=5, n_iter=1000)
	model.n_symbols=32;
	model._set_emissionprob(np.zeros([model.n_components,model.n_symbols]))
	model.fit(X)

	# predict the optimal sequence of internal hidden state
	#hidden_states = model.predict(X)

	#print(hidden_states)
	print("done\n")

	observations = X
	transition = model._log_transmat
	startprob_prior = model._log_startprob
	emission = model._get_emissionprob();
	###############################################################################

def viterbi (self,observations,transition,startprob_prior,emission):
    """Return the best path, given an HMM model and a sequence of observations"""
    # A - initialise stuff
    nSamples = len(observations[0])
    nStates = transition.shape[0] # number of states
    c = np.zeros(nSamples) #scale factors (necessary to prevent underflow)
    viterbi = np.zeros((nStates,nSamples)) # initialise viterbi table
    psi = np.zeros((nStates,nSamples)) # initialise the best path table
    best_path = np.zeros(nSamples); # this will be your output

    # B- appoint initial values for viterbi and best path (bp) tables - Eq (32a-32b)
    viterbi[:,0] = startprob_prior * emission[:,0] #why have this prior added?
    c[0] = 1.0/np.sum(viterbi[:,0])
    viterbi[:,0] = c[0] * viterbi[:,0] # apply the scaling factor
    psi[0] = 0;

    # C- Do the iterations for viterbi and psi for time>0 until T
    for t in range(1,nSamples): # loop through time
        for s in range (0,nStates): # loop through the states @(t-1)
            trans_p = viterbi[:,t-1] * transition[:,s]
            psi[s,t], viterbi[s,t] = max(enumerate(trans_p), key=operator.itemgetter(1))
            viterbi[s,t] = viterbi[s,t]*emission[s,observations[t]]

        c[t] = 1.0/np.sum(viterbi[:,t]) # scaling factor
        viterbi[:,t] = c[t] * viterbi[:,t]

    # D - Back-tracking
    best_path[nSamples-1] =  viterbi[:,nSamples-1].argmax() # last state
    for t in range(nSamples-1,0,-1): # states of (last-1)th to 0th time step
        best_path[t-1] = psi[best_path[t],t]

    return best_path

def main():
	#learn()
    vision('/home/michael/projects/sc2centaur/data/screenshots/nexus_lores.jpg')

if __name__ == '__main__':
    main()