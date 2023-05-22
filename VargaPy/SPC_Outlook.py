import requests
import json
import os
from os.path import exists, join
import urllib.request
from zipfile import ZipFile
import shapefile
from descartes import PolygonPatch

class SPCoutlook: 
    '''Class for acessing SPC Convective Outlooks'''
    '''Params:
    date: YYYYMMDD - date of outlook
    category:  category of outlook to load - can be any from []
    base_path: local directory to where outlook files are saved
    outlook_time: time when outlook was published - default is 1630
    url: can specify a URL to request shapefiles from. Default is the SPC outlook archive.
    filename: can specify a filename to request from URL. By default, the zipped shapefiles are requested.
    local_filename: can specify a local filename to load. By default, the shapefiles for the given category are loaded. 
    extract: If true, the zipped shapefiles are automatically unzipped when downloaded.
    '''
    
    def __init__(self, date, category, base_path, outlook_time='1630', url='https://www.spc.noaa.gov/products/outlook/archive',
                 filename=None, local_filename=None, extract=True):
        self.date = date
        self.category = category
        self.base_path = join(base_path, date)
        self.outlook_time = outlook_time
        self.url = url
        #self.filename = filename if filename else f'day1otlk_{date}_1630-shp.zip' 
        self.filename = filename if filename else f'day1otlk_{date}_1630.kmz'
        self.local_filename=local_filename if local_filename else '_'.join(self.filename.split('_')[0:-1])+f'_1630_{self.category}'
        self.extract = extract
        
        self.load_spc_outlook()
        
    def download_spc_outlook(self):
        '''Downloads the shapefiles for a given date from the SPC archive, then unzips them'''
    
        #directory doesn't exist:
        if not exists(self.base_path): 
            #make directory
            print(f'Making {self.base_path}')
            os.mkdir(self.base_path)

        #Download file
        print(f'Downloading outlook from {join(self.url, f"{self.date[0:4]}/{self.filename}")}')
        urllib.request.urlretrieve(join(self.url, f'{self.date[0:4]}/{self.filename}'), join(self.base_path, self.filename))

        #Extract files    
        if self.extract: 
            print(f'Extracting {self.filename} in {self.base_path}')
            with ZipFile(join(self.base_path, self.filename)) as ZF:
                ZF.extractall(self.base_path)
        return 
    
    def load_spc_outlook(self):
        ''' Loads the outlook for a given date and category'''

        #If file doesn't exist locally, download the file from SPC archive
        if not exists(join(self.base_path, self.filename)):
            self.download_spc_outlook()
        else:
            print('Outlook file already exists locally')

        #Load outlook shapefile
        print(f'Loading {self.local_filename}')
        self.outlook = shapefile.Reader(join(self.base_path, self.local_filename))

        return 
    
    def add_to_ax(self, ax):
        '''Adds the outlook boundaries to an existing figure axis'''
        '''Params:
        ax: figure axis to plot outlook boundaries on
        '''
        for guidance in self.outlook.shapes():
            poly=guidance.__geo_interface__
            ax.add_patch(PolygonPatch(poly, fc='red', ec='red', alpha=0.5, zorder=2))