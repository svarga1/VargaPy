#Python Package used for Various Machine Learning Utilities

#########
#Imports#
#########

import sys
sys.path.append('/home/samuel.varga/python_packages/ml_workflow/') #ML_workflow package by mflora
sys.path.append('/home/samuel.varga/projects/2to6_hr_severe_wx/') #2-6 ML repo by mflora
from main.io import load_ml_data 
import pandas as pd
import numpy as np
import numpy.random as npr


def All_Severe(base_path, mode='train', target_scale=36, FRAMEWORK='POTVIN', TIMESCALE='2to6', Big=True):
    '''base_path: Path like. Directory where ML feather files are located'''
    '''mode : str. Determines whether to load the training or testing dataset. Valid: ['train', 'test']'''
    '''target_scale: int. radius of target sizes in km. Valid: [9,18,36]'''
    '''Framework: str. Data framework to use. Determines the filepath. Valid: ['ADAM','POTVIN']'''
    '''Timescale: str. Time window for ML predictions. Determines the filepath. Valid: ['0to3','2to6']'''
    '''Big: Bool. Flag used to grab the un-subsampled dataset'''
    
    '''Loads the ML dataset with all severe weather types labeled as targets'''
    
    '''Return values:
    X: dataset of predictors
    y: array of all-severe targets corresponding to X
    metadata: metadata about the ML file '''
    
    target_col=f'wind_severe__{target_scale}km'
    X, y, metadata = load_ml_data(base_path=base_path,
                                  mode=mode,
                                  target_col=target_col,
                                  FRAMEWORK=FRAMEWORK,
                                  TIMESCALE=TIMESCALE,
                                  Big=Big)
    print(len(y[y>0])) #Number of points with wind targets
    for hazard in ['hail','tornado']:
        target_col='{}_severe__{}km'.format(hazard, target_scale)
        SPAM, y1, SPAM  = load_ml_data(base_path=base_path,
                                       mode=mode,
                                       target_col=target_col,
                                       FRAMEWORK=FRAMEWORK,
                                       TIMESCALE=TIMESCALE,
                                       Big=Big) 
        y +=y1
        print(len(y[y>0])) #Prints the number of wind+hail targets, then wind+hail+tornado
       
    y[y > 0] = 1 #All target points (y>1) are remapped to y=1
    
    return X, y, metadata


def Simple_Random_Subsample(X_Full, y_Full, p, seedObject=np.random.RandomState(42)):
    '''Returns a random subsample of X_full and associated targets consisting of p% of the full training dataset'''
    
    '''X_Full: dataframe. The dataframe to draw the random sample from.'''
    '''y_Full: array. The array of target values (0,1) for X_full'''
    '''p: float. The fraction of the dataset to keep in the subsample. Must be between (0,1]'''
    '''seedObject: a random state object from numpy.random to allow reproducibility'''
    
    '''Return values:
    X_sub: subsampled dataframe of predictors
    y_sub: subsampled array of target values'''
    
    if p <=0 or p>1:
        print('p must be a value between (0,1]')
        return None
    elif p==1:
        print(f'Base rate of y_full: {np.mean(y_Full)}')
        return X_Full, y_Full
    else:
        n_samps=int(p*X_Full.shape[0]) #number of samples to choose
        inds=seedObject.choice(X_Full.shape[0], n_samps, replace=False) #Indices of  subsample
        X_sub=X_Full.iloc[inds]
        X_sub.reset_index(drop=True, inplace=True)
        y_sub=y_Full[inds]
        
        print(f'Base rate of y_full: {np.mean(y_Full)}')
        print(f'Base rate of subsample for {p*100}%: {np.mean(y_sub)}')
        
        return X_sub, y_sub