import data_extractor

#Set data locations
#   replay_dir contains the replays that are used as training data.
#   template_dir contains the template images of the units and buildings on the screen.
#   numbers_dir contains the template images of numbers used for reading the game time.
def process_replays(replay_dir,feature_dict,output_dir):
    
    #ipdb.set_trace()
    training_data={'Protoss':[], 'Zerg':[], 'Terran':[]}
    output_dir = os.path.join(dir,'..\\data\\training_data')

    for dirpath,_,filenames in os.walk(replay_dir):
        for f in filenames:
            filepath = os.path.abspath(os.path.join(dirpath, f))
            #print(filepath)
            
            #Replays should be in the following format:
            #X-build.SC2Replay
            #Where X is P, Z, or T 
            label = f.split('-')[1]
            fileprefix = f.split('.')[0]

            for player in [1, 2]:
                [data,race] = extract_replays(filepath,player,label,feature_dict)
                aligned_data = align_replays(data)
                
                training_data[race].append(aligned_data)

                    
                with open(output_dir+'\\'+race+'\\'+fileprefix+'.csv', 'wb') as csvfile:
                    csvwriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    csvwriter.writerows(data)

    return training_data