# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
### change the path to my working directory
# os.chdir('/Users/chenyangkang/Desktop/MADS/521')
import warnings
import PIL
warnings.filterwarnings('ignore')
from bing_pictures import grap_figure
from selenium import webdriver
import random,time,requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import sys
import time
### import modules
import folium
from folium import plugins
from folium.plugins import HeatMap
import webbrowser
import time
import cv2

### using mouseposition so that my mouse will show the longtude and latitude
from folium.plugins import MousePosition

# %%
### define a funtion that take the observation data as input and output a merged dataframe with inno_data set.
def read_data(path):
    ### load the ebird (bird observation) data
    data=pd.read_table(path,sep='\t')
    ### set proper date format
    data['LAST EDITED DATE']=pd.to_datetime(data['LAST EDITED DATE'])
    data['OBSERVATION DATE']=pd.to_datetime(data['OBSERVATION DATE'])
    data['year']=data['OBSERVATION DATE'].dt.year
    data['month']=data['OBSERVATION DATE'].dt.month
    data['week']=data['OBSERVATION DATE'].dt.week
    ### fill some missing data
    data['OBSERVATION COUNT'][data['OBSERVATION COUNT']=='X']=5
    ### change data type
    data['OBSERVATION COUNT']=data['OBSERVATION COUNT'].astype('float')
    return data

# %%
### define a function that return a three-dimensional: 
# dimension1: week. each list belongs to a week of the years.
# dimension2: each observation data point.
# dimension3: a [longitude, latitude, observation counts] list.
def creat_plot_list(df1,year_list,start=1,end=53):
    out_list=[]
    for year in year_list:
        df=df1[df1['year']==year]
        for week in range(start,end+1):
            sub_data=df[df['week']==week][['LONGITUDE','LATITUDE','SCIENTIFIC NAME','OBSERVATION COUNT']]
            sub_data=sub_data.dropna()
            lat=sub_data['LATITUDE'].values
            long=sub_data['LONGITUDE'].values
            value=sub_data['OBSERVATION COUNT'].values
            list_=[[lat[i], long[i], value[i]] for i in range(0,len(lat))]
            out_list.append(list_)
    
    return out_list


# %%
def plot_map_new(long_lat_value_list,index,image_path1=None,image_path2=None,image_path3=None):
    ### the folium.map funtion takes location (original central poin of the map), zoom level and tiles. 
    # Tiles are like OpenStreetMap, Stamen Toner, Stamen Watercolor, Cartodb Positron, 
    map = folium.Map(location=[np.median([list_[i][0] for list_ in long_lat_value_list for i in range(0,len(list_))]), \
                                np.median([list_[i][1] for list_ in long_lat_value_list for i in range(0,len(list_))])], \
                                    zoom_start=2, \
                                        tiles='OpenStreetMap', \
                                                auto_play=True)
    
    ### add image to the map (reference: https://nbviewer.org/github/python-visualization/folium/blob/main/examples/ImageOverlay.ipynb)
    if not image_path1==None:
        folium.raster_layers.ImageOverlay(
        image=image_path1,
        name="name_jpg",
        bounds=[[20, -120], [-20, -175]],
        opacity=1,
        interactive=False,
        cross_origin=True,
        zindex=1,
        alt=image_path1,
        ).add_to(map)

    if not image_path2==None:
        a=cv2.imread(image_path2)
        len_with_frac=a.shape[1]/a.shape[0]
        if a.shape[1]>=a.shape[0]:
            factor=1.3
        else:
            factor=2
        print("len_with_frac2 "+str(len_with_frac))
        folium.raster_layers.ImageOverlay(
        image=image_path2,
        name="picture1_jpg",
        bounds=[[-25, -153], [-25-(55/len_with_frac)/factor, -208]],
        opacity=1,
        interactive=False,
        cross_origin=True,
        zindex=1,
        alt=image_path2,
        ).add_to(map)

    if not image_path3==None:
        a=cv2.imread(image_path3)
        len_with_frac=a.shape[1]/a.shape[0]
        if a.shape[1]>=a.shape[0]:
            factor=1.3
        else:
            factor=1.8
        print("len_with_frac3 "+str(len_with_frac))
        folium.raster_layers.ImageOverlay(
        image=image_path3,
        name="picture2_jpg",
        bounds=[[-25-(55/len_with_frac)/factor, -89], [-25, -144]],
        opacity=1,
        interactive=False,
        cross_origin=True,
        zindex=1,
        alt=image_path3,
        ).add_to(map)

    ### add lines (reference: https://nbviewer.org/github/python-visualization/folium/blob/main/examples/VectorLayers.ipynb)
    north_pole_line=[[66.566,x] for x in np.linspace(-180,180,num=100)]
    south_pole_line=[[-66.566,x] for x in np.linspace(-180,180,num=100)]
    north_tropic_line=[[23.433,x] for x in np.linspace(-180,180,num=100)]
    south_tropic_line=[[-23.433,x] for x in np.linspace(-180,180,num=100)]

    folium.PolyLine(
    locations=north_pole_line,
    color="blue",
    weight=4,
    tooltip="north_pole_line", opacity=0.3
    ).add_to(map)

    folium.PolyLine(
    locations=south_pole_line,
    color="blue",
    weight=4,
    tooltip="south_pole_line",opacity=0.3
    ).add_to(map)

    folium.PolyLine(
    locations=north_tropic_line,
    color="red",
    weight=4,
    tooltip="north_tropic_line",opacity=0.3
    ).add_to(map)

    folium.PolyLine(
    smooth_factor=50,
    locations=south_tropic_line,
    color="red",
    weight=4,
    tooltip="south_tropic_line",opacity=0.3
    ).add_to(map)


    ### add mouse position to check longitude and latitude
    MousePosition().add_to(map)
    # make plot data
    plugins.HeatMapWithTime(long_lat_value_list,index=index, auto_play=True, max_opacity=0.3).add_to(map)
    

    # map.save('map_hp.html') #save in html
    # webbrowser.open('map_hp.html') #open it in browser
    return map

# %%
out_html=open('./All_species/index.html','w')
out_html.write("""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html( charset=utf-8" />
<title>Visualizing Bird Migration</title> 
<style type="text/css">

p {
    text-align: center;
    background-color:#e0ffff;
}

body {
    text-align: center;
}

h1 {
	background-color:#6495ed;
        text-align: center;
}

h2 {
    	background-color:#6495ed;
        text-align: center;
}

h3 {  	background-color:#6495ed;
        text-align: center;}



</style>
</head>
<body>

    <h1> Visualizing Bird Migration Process Using ebird Data</h1> <br>
    <h2> contributors: Yangkang  chenyangkang24@outlook.com<br>    
	&nbsp&nbsp&nbsp
	&nbsp&nbsp&nbsp
	&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp   
	Xiaohang  zhangxiaohang@ioz.ac.cn</h2>

    <p> Hi! Thanks for visiting. Feel free to click on these items. <br>
    It takes minitues to load the data (sorry because the server is located in China). <br>
    Or you can 'wget' the website to your local machine and open it.<br>
    For example, type this in your terminal: <font color="darkcyan">wget http://39.107.87.238/arctic_tern_2019.html</font><br>
    <br>
    If you still have trouble loading, try <b>Apus apus</b> or <b>Falco amurensis</b> data first, because they are relatively small.
    <br>To spead up the motion, pull the "fps" bar to 10. To replay the motion, click on the "replay" botton.
    To limite the time interval, you can drag the triangles on the on the time bar.<br>
    <br>
    If you find that some of the pictures are strange and make no sense, that's normal, because we simply use web crawler to request pictures from bing.com.<br>
    <font color="darkcyan">They didn't go through human review</font>, therefore, just for fun! :)
    </p>
<p2>
    <a href="http://39.107.87.238/apus_apus_2019.html">楼燕/北京雨燕 (Apus apus)</a><br>
    <a href="http://39.107.87.238/arctic_tern_2019.html">北极燕鸥 (Sterna paradisaea)</a><br>
    <a href="http://39.107.87.238/Falco_peregrinus_2019.html">游隼 (Falco peregrinus)</a><br>
    <a href="http://39.107.87.238/Falco_amurensis_2019.html">红脚隼/阿穆尔隼 (Falco amurensis)</a><br> \n
    
    """)

for cat in ['ducks','swift','falcon','semipalmated_sandpiper','pectoral_sandpiper', \
    'sooty_shearwater','pied_wheatear','short_tailed_shearwater']:
    print(cat)
    data=read_data(cat+'_data.txt')
    out_html.write('<br><h3>——————————————————%s——————————————————</h3><br>'%(cat))
    for species,scientificname in zip(pd.unique(data['COMMON NAME']),pd.unique(data['SCIENTIFIC NAME'])):
            species=species.replace('/','_or_')
            scientificname=scientificname.strip(r'[.]+')
            start=1
            end=53
            year_list=[i for i in range(2010,2021)]
            label_list=[]
            for year in year_list:
                day_start=[pd.to_datetime(str(year-1)+'-12-31')+pd.Timedelta((x*7-6), unit='D') for x in range(start,end+1)]
                day_end=[str(x.month).zfill(2)+'-'+str(x.day).zfill(2) for x in [x+pd.Timedelta(6, unit='D') for x in day_start]]
                day_start=[str(x.month).zfill(2)+'-'+str(x.day).zfill(2) for x in  [pd.to_datetime(str(year-1)+'-12-31')+pd.Timedelta((x*7-6), unit='D') for x in range(start,end+1)]]
                week=[str(x) for x in range(start,end+1)]
                label=['year: '+str(year)+', from: '+str(x[1])+', to: '+str(x[2]) +', week: '+str(x[0]).zfill(2) for x in zip(week,day_start,day_end)]
                label_list.extend(label)

            try:
                plt.axis([-1,1,-1,1])
                plt.text(-0.9,0.8,'Common Name:',fontsize=26)
                plt.text(-0.9,0.5,species,fontsize=26)
                plt.text(-0.9,-0.2,'Scientific Name:',fontsize=26)

                sci_name_it=''
                count=0
                for i in scientificname.split(' '):
                    count+=1
                    if count==1 or count==2:
                        sci_name_it+='$\it{%s}$'%(str(i))
                    else:
                        sci_name_it+=str(i)
                    sci_name_it+=" "

                sci_name_it=sci_name_it.strip(' ')

                plt.text(-0.9,-0.5,sci_name_it,fontsize=26)

                plt.axis(False)
                plt.savefig('out.jpg')
                plt.close()


                pic1='./All_species/%s.jpg'%(species.replace(' ','_')+"_1")
                pic2='./All_species/%s.jpg'%(species.replace(' ','_')+"_2")

                if (not os.path.exists(pic1)) or (not os.path.exists(pic2)):
                    grap_figure(species)

                time.sleep(random.uniform(1, 3))

                plot_list=creat_plot_list(data[(data['COMMON NAME']==species)],year_list,start=start,end=end)
                map = plot_map_new(plot_list,label_list,'out.jpg',pic1,pic2)
                if not os.path.exists('./All_species/'+cat):
                    os.mkdir('./All_species/'+cat)
                map.save('./All_species/%s/%s___%s__2019.html'%(cat,species.replace(' ','_'),scientificname.replace(' ','_'))) #save in html
                out_html.write('    <a href="http://39.107.87.238/%s___%s__2019.html"> Common Name: %s;     Scientific Name: %s</a><br>\n'%(species.replace(' ','_'),scientificname.replace(' ','_'),species.replace(' ','_'),scientificname.replace(' ','_')))
                
                print("Finished***:   "+species)
            except Exception as e:
                print(str(e))
                print("killed.....:   "+species)
                continue

out_html.write("""
</p2>

<div>
<p3> <font color=white> <a href="http://39.107.87.238/visitor.html">visitor check</font></p3>

</body>
</html>

""")
out_html.close()


