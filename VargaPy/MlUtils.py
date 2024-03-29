#Functions for loading Machine Learning data

#########
#Imports#
#########

import sys
sys.path.append('/home/samuel.varga/python_packages/ml_workflow/') #ML_workflow package by mflora
sys.path.append('/home/samuel.varga/projects/2to6_hr_severe_wx/') #2-6 ML repo by mflora
from main.io import load_ml_data 
import pandas as pd
import numpy as np
import argparse
import numpy.random as npr


def Train_Ml_Parser():
    '''Returns an ArgParse Object that takes in command line input to modify predictor choices'''
    parser=argparse.ArgumentParser()
    parser.add_argument('-o', '--original', help="Original Variables", action='store_true')
    parser.add_argument('-ts', '--training_scale', help="Scale of Training variables (9,27,45)")
    parser.add_argument('-hs','--hazard_scale', help="Scale of Target Variables (9,18,36, all)")
    parser.add_argument('-hn', '--hazard_name', nargs='+', help="Target: hail, wind, tornado")
    parser.add_argument('-env','--environmental', help="Drop all intrastorm variables", action='store_true')
    parser.add_argument('-is' ,'--intrastorm', help="Drop all environmental variables", action='store_true')
    parser.add_argument('--SigSevere', action='store_true', help='Train Using Sig Severe as Targets')
    return parser

def All_Severe(base_path, mode='train', target_scale=36, FRAMEWORK='POTVIN', TIMESCALE='2to6', full_9km=True, SigSevere=False, appendUH=False, Three_km=False):
    '''base_path: Path like. Directory where ML feather files are located'''
    '''mode : str. Determines whether to load the training or testing dataset. Valid: ['train', 'test']'''
    '''target_scale: int. radius of target sizes in km. Valid: [9,18,36]'''
    '''Framework: str. Data framework to use. Determines the filepath. Valid: ['ADAM','POTVIN']'''
    '''Timescale: str. Time window for ML predictions. Determines the filepath. Valid: ['0to3','2to6']'''
    '''SigSevere: Bool. Flag used to train on sig-severe'''
    
    '''Loads the ML dataset with all severe weather types labeled as targets'''
    
    '''Return values:
    X: dataset of predictors
    y: array of all-severe targets corresponding to X
    metadata: metadata about the ML file '''
    #Data used for bulk training and evaluation - returns X, y, metadata
    if SigSevere:
        target_col=f'wind_sig_severe__{target_scale}km'
    else:
        target_col=f'wind_severe__{target_scale}km'
    X, y, metadata = load_ml_data(base_path=base_path,
                                      mode=mode,
                                      target_col=target_col,
                                      FRAMEWORK=FRAMEWORK,
                                      TIMESCALE=TIMESCALE, appendUH=appendUH, Three_km=Three_km, full_9km=full_9km)
    print(len(y[y>0])) #Number of points with wind targets
    for hazard in ['hail','tornado']:
        if SigSevere:
            target_col='{}_sig_severe__{}km'.format(hazard, target_scale)
        else:
            target_col='{}_severe__{}km'.format(hazard, target_scale)
        _, y1, _  = load_ml_data(base_path=base_path,
                                           mode=mode,
                                           target_col=target_col,
                                           FRAMEWORK=FRAMEWORK,
                                           TIMESCALE=TIMESCALE, Three_km=Three_km, full_9km=full_9km) 
        y +=y1
        print(len(y[y>0])) #Prints the number of wind+hail targets, then wind+hail+tornado

    y[y > 0] = 1 #All target points (y>1) are remapped to y=1
    
    return X, y, metadata
    



def Drop_Unwanted_Variables(X, original=False, training_scale=False, intrastormOnly=False,  envOnly=False, dropList=None):
    '''Function that removes unwanted columns from X '''
    '''Arguments:
       X: input dataframe created by All_Severe or load_ml_data
       original:
       training_scale: float/int. Only predictors of this scale are kept
       intrastormOnly:
       envOnly: '''
    '''dropList: list. drops any variable that matches a list entry'''
    '''Returns X-like dataframe with fewer columns, and ts_suff/var_suff which are a suffix to be appended to the ML model'''
    
    #Dictionary of intrastorm variables. All other variables are environmental. 
    varDic={ 'ENS_VARS':  ['uh_2to5_instant',
                                'uh_0to2_instant',
                                'wz_0to2_instant',
                                'comp_dz',
                                'ws_80',
                                'hailcast',
                                'w_up',
                                'okubo_weiss',
                        ]}
    X=X[[col for col in X.columns if col not in ['NX','NY']]]
    
    if training_scale: #Removes all columns except for those with correct neighborhood scale
        X=X[[col for col in X.columns if '{}km'.format(training_scale) in col]] 
        ts_suff=str(training_scale)+'km'
    else:
        ts_suff='all'
    
    if original:
        print("Using Original Variables- Dropping IQR, 2nd lowest, 2nd highest, and intrastorm mean")
        X=X[[col for col in X.columns if 'IQR' not in col]] #Drops IQR for all IS vars
        X=X[[col for col in X.columns if '2nd' not in col]] #Drops 2nd lowest ens. member value for all IS vars
        X=X[[col for col in X.columns if '16th' not in col]] #Drops 2nd highest ens. member value for all IS vars
        badCols=np.array([])
        for strmvar in vardic['ENS_VARS']:
            badCols=np.append(badCols, [col for col in X.columns if 'mean' in col and strmvar in col] )

        X=X.drop(badCols, axis=1)
    else: #Drops 90th %ile computed w/ extrapolation
        print("Using new variables- dropping old 90th percentile")
        X=X[[col for col in X.columns if '90th' not in col]] #Keeps all columns except the old 90th %ile

    if envOnly or intrastormOnly: #Drops all intrastorm variables or drops all environmental variables
        badCols=np.array([])
        for strmvar in varDic['ENS_VARS']: 
            badCols=np.append(badCols, [col for col in X.columns if strmvar in col]) #Every column that has a storm var
        if envOnly:
            print("Dropping all intrastorm variables")
            X=X.drop(badCols, axis=1) #Drops all intrastorm variables
        elif intrastormOnly:
            print("Dropping all environmental variables")
            X=X[badCols] #drops all environmental variables
    if dropList:
        print(f'Dropping {dropList}')
        X=X.drop([colName for colName in X.columns for dropvar in dropList if dropvar in colName], axis=1)
        
    print(X.shape)
    print(ts_suff)
    
    if intrastormOnly or envOnly:
        var_suff = 'intrastorm' if intrastormOnly else 'environment'
    else:
        var_suff='control'
    
    return X, ts_suff, var_suff






def Simple_Random_Subsample(X_Full, y_Full, meta_full, p, seedObject=np.random.RandomState(42)):
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
        return X_Full, y_Full, meta_full
    else:
        n_samps=int(p*X_Full.shape[0]) #number of samples to choose
        inds=seedObject.choice(X_Full.shape[0], n_samps, replace=False) #Indices of  subsample
        X_sub=X_Full.iloc[inds]
        X_sub.reset_index(drop=True, inplace=True)
        y_sub=y_Full[inds]
        meta_sub=meta_full.iloc[inds]
        meta_sub.reset_index(drop=True, inplace=True) #Keep an eye on this to see if it breaks
        
        print(f'Base rate of y_full: {np.mean(y_Full)}')
        print(f'Base rate of subsample for {p*100}%: {np.mean(y_sub)}')
        
        return X_sub, y_sub, meta_sub
    
def group_coefs(Cols, coefs, groupby=None):
    '''Takes in a list of column names, and the matching coefficients for LR, and returns a DF that can be grouped'''
    '''Cols- list of variable names
    coefs - coefficients from LR corresponding to the columns
    '''
    X=pd.DataFrame(columns=['name','variable','category','neighborhood','statistic', 'coef']) #Make an empty dataframe
    X['name']=Cols #'name' contains the unparsed variable names from the ml df
    X['coef']=np.abs(coefs) #Absolute value of coefs
    X['variable']=[var.split('__')[0] for var in Cols]
    X['category']=[var.split('__')[1] if 'Init Time' not in var else 'time_avg' for var in Cols]
    X['neighborhood']=[var.split('__')[2] if 'Init Time' not in var else '4km'for var in Cols]
    X['statistic']=[var.split('__')[3]if 'Init Time' not in var else 'N/A' for var in Cols]
    X=X.drop('name', axis=1)
    if groupby is None:
        return X
    else:
        return X.groupby(by=groupby)
    
    
def pseudo_all_severe_probs(models, X_test):
    '''Takes in a list of models trained on individual hazards, then predicts on X_test to produce probability of any severe hazard'''
    '''models - list of models, where each model is trained for an individual severe weather hazard'''
    '''X_test - data to generate predictions for'''   
    indiv_probs=[model[1].predict_proba(X_test)[:,1] for model in models] #List of probabilities that a given hazard occurs
    no_severe_probs=np.ones_like(indiv_probs)-indiv_probs #List of probabilities that a given hazard doesn't occur
    no_severe_probs=np.multiply.reduce(no_severe_probs, axis=0) #Multiplies all probabilites together at a given grid point - probability that none of the severe hazards occur at that point
    all_severe_probs=np.ones_like(no_severe_probs)-no_severe_probs #Complementary - (1-prob of no hazards)=prob of any (or all) hazards
    return all_severe_probs

def get_bl_col(target_scale, hazard_name, timescale):
    '''Returns the correct baseline column title for the given timescale, hazard, and target_scale'''
    '''Params:
    target_scale - radius of target neighborhood in km - 36/18/9
    hazard_name - name & severity of hazard
    timescale= timescale of forecast window: either 0to3 or 2to6'''
    
    bl_cols = {'0to3':{'36':{'hail_severe' :  'hailcast__nmep_>1_25_45km',
          'wind_severe' : 'ws_80__nmep_>40_27km',
          'tornado_severe' : 'uh_2to5_instant__nmep_>175_27km',
            'all_severe' : 'uh_2to5_instant__nmep_>100_27km'
         },
                      '18':{'hail_severe' :  'hailcast__nmep_>1_25_27km',
          'wind_severe' : 'ws_80__nmep_>40_27km',
          'tornado_severe' : 'uh_2to5_instant__nmep_>200_27km',
            'all_severe' : 'uh_2to5_instant__nmep_>150_27km'
         },
                      '9':{'hail_severe' :  'hailcast__nmep_>1_25_27km',
          'wind_severe' : 'ws_80__nmep_>40_27km',
          'tornado_severe' : 'uh_2to5_instant__nmep_>75_9km',
            'all_severe' : 'uh_2to5_instant__nmep_>75_9km'
         }},
    '2to6':{'36':{'hail_severe' :  'hailcast__nmep_>1_25_45km',
          'wind_severe' : 'ws_80__nmep_>50_45km',
          'tornado_severe' : 'uh_2to5_instant__nmep_>200_27km',
            'all_severe' : 'uh_2to5_instant__nmep_>150_45km'
         },
           '18':{'hail_severe' :  'hailcast__nmep_>1_25_27km',
          'wind_severe' : 'ws_80__nmep_>50_27km',
          'tornado_severe' : 'uh_2to5_instant__nmep_>200_27km',
            'all_severe' : 'uh_2to5_instant__nmep_>150_27km'
         },
           '9':{'hail_severe' :  'hailcast__nmep_>1_25_27km',
          'wind_severe' : 'ws_80__nmep_>50_27km',
          'tornado_severe' : 'uh_2to5_instant__nmep_>200_9km',
            'all_severe' : 'uh_2to5_instant__nmep_>175_27km'
         }}} 
    return bl_cols[timescale][target_scale][hazard_name]