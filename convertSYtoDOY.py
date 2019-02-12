#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 08:28:43 2019

@author: caleb.pan
"""

import numpy as np
import gdal
import matplotlib.pyplot as plt

'''
THE PURPOSE OF THIS SCRIPT IS TO SELECT A SNOWMETRIC BAND FROM THE MODIS
DERIVED SNOW METRIC, CONVERT THE METRICS FROM SNOW YEAR TO WATER YEAR AND 
THEN EXPOR TO A GEOTIFF.

MORE INFORMATION CAN BE FOUND IN Lyndsay et al. 2015 Remote Sensing

THE SNOW METRICS CAN BE DOWNLOADED VIA FTP HERE: 
http://static.gina.alaska.edu/NPS_products/MODIS_snow/MODIS_derived_snow_metrics/version_1.0/

THE DATA ARE A 12 BAND COMPOSITE AND DESCRIBED BELOW

METRIC                                                          ACRONYM  BAND
First snow day of the full snow season                            FSD       1
Last snow day of the full season                                  LSD       2
Duration of the full snow season                                 FLSDR      3
First snow day of the longest continuous snow season              LCFD      4
Last day of the longest continuous snow season                    LCLD      5
Duration of the longest continuous snow season                    LCDR      6
Number of days classified as snow after filtering                 SD        7
Number of days not classified as snow after filtering             NSD       8
Number of segments within continuous snow season                  CSN       9
Overall surface condition and snowcover character of pixel                  10
Number of days classified as cloud after filtering                CD        11
Total # of days within all continuous snow season segments        TCD       12

IN THIS SCRIPT WE WILL DEFINE WHICH SNOWMETRIC WE WANT USING THE BAND NUMBER
'''

def getname(num):
    acr = ['FSD','LSD','FLSDR','LCFD','LCLD','LCDR','SD','NSD',\
           'CSN',' ','CD','TCD']
    index = num -1
    if num == 10:
        return 'surface_condition'
    else:
        return acr[index]
    
def tiftoarray(openfile, num):
    opentif = gdal.Open(openfile)
    band = opentif.GetRasterBand(num)
    array = band.ReadAsArray().astype(np.float)
    array[array <= 0] = np.nan
    del opentif
    return array

def getgeo(openfile):
    opentif = gdal.Open(openfile,gdal.GDT_Byte)
    geo = opentif.GetGeoTransform()
    return geo

def getprj(openfile):
    opentif = gdal.Open(openfile,gdal.GDT_Byte)
    prj = opentif.GetProjection()
    return prj

def getdim(openfile):
    opentif = gdal.Open(openfile)
    wide = opentif.RasterXSize
    high = opentif.RasterYSize
    return wide, high

def plot(array):
    plt.imshow(array)
    plt.colorbar()
    plt.show()
    
inroot = '/anx_lagr2/caleb/GitHub/modis/snowmetrics/'
outroot = inroot + 'snowmetricsdoy/'

# =============================================================================
# THE MODIS SNOWMETRICS EXTEND FROM 2001 TO 2016 AND INCLUDE 4 LEAPYEARS
# =============================================================================
leapyears = [2004, 2008, 2012, 2016]
years = [2001,2002,2003,2004,2005,2006,2007,2009,2010,2011,2013,2014,2015]

#IF ITERATING THROUGH 'LEAPYEARS', CHANGE DAY TO 366, ELSE SET TO 365
day = 365

#DEFINE WHICH SNOW METRIC TO CONVERT
num = 5
metric = getname(num)

#DEFINE WHICH LIST TO LOOP THROUGH, EITHER 'LEAPYEARS' OR 'YEARS'
for i in years:
    year = str(i)
    infile = inroot + year + '_snowyear_metrics_v7.tif'
    array = tiftoarray(infile, num)
    dim = getdim(infile) #get array dimensions
    prj = getprj(infile) # get tif projection
    geo = getgeo(infile) #get tif geotransform
    plot(array)
    wyarray = np.zeros((dim[1], dim[0]))
    for y in range(dim[1]):
        for x in range(dim[0]):
            val = array[y,x]
# =============================================================================
#             IF THE PIXEL VALUE IS LESS THAN 365 OR 366, KEEP THE VALUE
# =============================================================================
            if val <= day:
                wy = val
# =============================================================================
#       IF THE PIXEL VALUE IS GREATER THAN 365 OR 366, SUBTRACT ACCORDINGLY
# =============================================================================
            else:
                wy = val - day
# =============================================================================
#             ASSIGN THE WY DAY TO THE EMPTY ARRAY
# =============================================================================
            wyarray[y,x] = wy
# =============================================================================
#     EXPORT THE ARRAY TO A NEW TIF
# =============================================================================
    outfile = outroot + year + '_wy_metrics_v7_' + metric + '.tif'
    driver = gdal.GetDriverByName('GTiff')
        
    dst = driver.Create(outfile, dim[0], dim[1], 1, gdal.GDT_Int16)
    dst.SetProjection(prj)
    dst.SetGeoTransform(geo)
    dst.GetRasterBand(1).WriteArray(wyarray)
    print 'exporting ' + outfile
    del driver, dst
    
        
# =============================================================================
# plot(wyarray)
# plot(array)
# =============================================================================
        
