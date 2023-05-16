#IMPORT SYSTEM FILES
import argparse
import scipy.io.wavfile as wavfile
import traceback as tb
import os
import sys
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist, euclidean, cosine 
import warnings
from keras.models import load_model
import logging
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)


#IMPORT USER-DEFINED FUNCTIONS
from feature_extraction import get_embedding, get_embeddings_from_list_file
from preprocess import get_fft_spectrum
import parameters as p


def enroll(name,file):
    print("File name",file)

    print("Loading model weights from [{}]....".format(p.MODEL_FILE))
    try:
        model = load_model(p.MODEL_FILE)
    except:
        return "Failed to load weights from the weights file, please ensure *.pb file is present in the MODEL_FILE directory"
        exit()
    
    try:
        print("Processing enroll sample....")
        enroll_result = get_embedding(model, file, p.MAX_SEC)
        print("Enroll sample processed.")
        enroll_embs = np.array(enroll_result.tolist())
        print("Enroll sample embedded.")
        speaker = name
        print("Enrolling user [{}]....".format(speaker))
    except:
        return "Error processing the input audio file. Make sure the path."
    try:
        np.save(os.path.join(p.EMBED_LIST_FILE,speaker +".npy"), enroll_embs)
        return "Succesfully enrolled the user"
    except:
        return "Unable to save the user into the database."
    

def recognize(file):
    if os.path.exists(p.EMBED_LIST_FILE):
        embeds = os.listdir(p.EMBED_LIST_FILE)
    if len(embeds) == 0:
        return "No enrolled users found"
    print("Loading model weights from [{}]....".format(p.MODEL_FILE))
    try:
        model = load_model(p.MODEL_FILE)

    except:
        return "Failed to load weights from the weights file, please ensure *.pb file is present in the MODEL_FILE directory"
        exit()
        
    distances = {}
    print("Processing test sample....")
    print("Comparing test sample against enroll samples....")
    test_result = get_embedding(model, file, p.MAX_SEC)
    test_embs = np.array(test_result.tolist())
    for emb in embeds:
        enroll_embs = np.load(os.path.join(p.EMBED_LIST_FILE,emb))
        speaker = emb.replace(".npy","")
        distance = euclidean(test_embs, enroll_embs)
        distances.update({speaker:distance})
    if min(list(distances.values()))<p.THRESHOLD:
        return {"Recognized" : min(distances, key=distances.get)}
    else:
        return ("Could not identify the user, try enrolling again with a clear voice sample","Score: ",min(list(distances.values())))
