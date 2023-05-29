#import requests
#import json
import os
from os.path import exists, join
import urllib.request
from zipfile import ZipFile
#import shapefile
#from descartes import PolygonPatch
import geopandas as gpd
import matplotlib.patches as mpatches

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
        self.filename = filename if filename else f'day1otlk_{date}_1630-shp.zip' 
        #self.filename = filename if filename else f'day1otlk_{date}_1630.kmz'
        self.local_filename=local_filename if local_filename else '_'.join(self.filename.split('_')[0:-1])+f'_1630_{self.category}.shp'
        self.extract = extract
        self.colors = {'cat':{2:('TSTM','#c1e9c1') , 3:('MRGL','#80c580') , 4:('SLGT','#f7f780') , 5:('ENH','#e6c280') , 6:('MDT','#e68080') , 8:('HIGH','#ff80ff')},
                        'wind':{5:('5','#8b4726'), 15:('15','#ffc800'), 30:('30','#ff0000'), 45:('45','#ff00ff'), 60:('60','#912cee')},
                        'hail':{5:('5','#8b4726'), 15:('15','#ffc800'), 30:('30','#ff0000'), 45:('45','#ff00ff'), 60:('60','#912cee')},
                        'torn':{2:('2','#008b00'), 5:('5','#8b4726'), 10:('10','#ffc800'), 15:('15','#ff0000'), 30:('30','#ff00ff'), 45: ('45','#c896f7'), 60:('60', '#104e8b')}}
        self.legend_titles = {'cat':'Categorical Outlook Legend',
                              'hail':'Hail Probability Legend (in %)',
                              'wind':'Wind Probability Legend (in %)',
                              'torn':'Tornado Probability Legend (in %)'}
        
        #Download & Load SPC outlook files when class instance is created
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
        #urllib.request.urlretrieve(self.url + f'/{self.date[0:4]}/{self.filename}', join(self.base_path, self.filename)) #windows is silly

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
        #self.outlook = shapefile.Reader(join(self.base_path, self.local_filename))
        
        #Saves and sorts the values in order based on label
        self.outlook = gpd.read_file(join(self.base_path, self.local_filename)).sort_values(by='DN')  
        #self.outlook = gpd.read_file(self.base_path +'/'+ self.local_filename+'.shp')
        print(self.outlook)
        print(guidance for guidance in self.outlook.geometry)
        print(self.outlook.crs)
        return 
    
    def add_to_ax(self, ax, crs):
        '''Adds the outlook boundaries to an existing figure axis'''
        '''Params:
        ax: figure axis to plot outlook boundaries on
        crs: projection that data is being plotted in 
        '''
        self.outlook.geometry = self.outlook.geometry.to_crs(crs)
        #print(self.outlook)
        
        #self.outlook.plot(ax=ax, zorder=-1)
        #ax.add_geometries(self.outlook.geometry, crs=crs)

        for poly, dn in zip(self.outlook.geometry, self.outlook.DN):
            #Polygons are ordered from high to low, but we plot from low to high so the higher risk boundaries appear on top.
            #ax.add_geometries(poly, crs=crs, facecolor=self.colors[self.category][dn], edgecolor=self.colors[self.category][dn])
            ax.add_geometries(poly, crs=crs, facecolor='None', edgecolor=self.colors[self.category][dn][1])

        #for guidance in self.outlook.geometry:
            #ax.add_patch(PolygonPatch(guidance, fc='red', ec='red', alpha=0.5, zorder=2))
            #print(guidance)


        #for guidance in self.outlook.shapes():
        #for guidance in self.outlook.geometry:
            #poly=guidance.__geo_interface__
            #ax.add_patch(PolygonPatch( guidance, fc='red', ec'red', alpha=0.5, zorder=2))
            #ax.add_patch(PolygonPatch(guidance, fc='red', ec='red', alpha=0.5, zorder=2))
    
    def add_legend_to_ax(self, ax):
        '''adds the outlook legend to an existing figure axis. returns legend object'''
        
        order=[0,3,1,4,2,5] #Used to reorient the legend
        outlook_patches=[mpatches.Patch(facecolor=color[1], label=color[0]) for color in self.colors[self.category].values()]
        outlook_patches=[outlook_patches[i] for i in order[:len(outlook_patches)]]
        legend = ax.legend(handles=outlook_patches, ncol=3, title=self.legend_titles[self.category], markerfirst=False)
        ax.axis('off')
        
        return legend



'''    import cartopy.io.shapereader as shpreader
# Read shape file
reader = shpreader.Reader("ne_110m_admin_0_countries.shp")
# Filter for a specific country
kenya = [country for country in reader.records() if country.attributes["NAME_LONG"] == "Kenya"][0]
# Display Kenya's shape
shape_feature = ShapelyFeature([kenya.geometry], ccrs.PlateCarree(), facecolor="lime", edgecolor='black', lw=1)
ax.add_feature(shape_feature)'''