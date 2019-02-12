#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 09:48:17 2019

@author: caleb.pan
"""

import gdal
import numpy as np

import numpy as np
import gdal
import matplotlib.pyplot as plt

'''
THE PURPOSE OF THIS SCRIPT IS IS TO INTERPOLATE THE MODIS SNOW METRICS FOR
ALASKA SO IT WILL MATCH THE SPATIAL RESOLUTION AND DIMESIONS OF THE A TB
DERIVED SNOW PRODUCT AT 6.25 KM. 

THERE ARE TWO PRIMARY INPUTS; 1)DEFINE WHAT MODIS SNOW METRIC TO INTERPOLATE 
AND 2) WHICH TYPE OF INTERPOLATION TO USE (I.E. BILINEAR, MINIMUM,MEDIAN, MODE)
'''
def tiftoarray(openfile):
    opentif = gdal.Open(openfile)
    band = opentif.GetRasterBand(1)
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

# =============================================================================
# GET THE DIMENSIONS, GEOTRANSFORM, AND PROJECTION OF THE NEW GRID
# =============================================================================
prjfile = '/anx_lagr2/caleb/GitHub/snowmetrics/data/mmod_2008.tif'
geo = getgeo(prjfile)
prj = getprj(prjfile)
dim = getdim(prjfile)
array = tiftoarray(prjfile)


# =============================================================================
# SET YOUR DIRECTORIES AND DEFINE PARAMETERS
# =============================================================================
inroot = '/anx_lagr2/caleb/SnowAlaska/MODISsnowmetrics/'
root = inroot + 'snowmetricsdoy/'
metric = 'LCLD' #define the snowmetric
outext = '_bilin.tif' ##define the interpolation in the outfile name

for i in range(2001,2017,1):
    year = str(i)
    
    modfile = root + year + metric + '.tif'
    modopen = gdal.Open(modfile)
    modarray = tiftoarray(modfile)
    modprj = getprj(modfile)
    outfile = root + year +'_wy_metrics_v7_' + metric  + outext
    driver = gdal.GetDriverByName('GTiff')
    driver.Register()
    dst = driver.Create(outfile, dim[0],dim[1], 1,gdal.GDT_Int16)
    
    dst.SetGeoTransform(geo)
    dst.SetProjection(prj)
    
# =============================================================================
#     USE GDAL REPROJECT IMAGE TO SET THE MODIS TO THE MATCHING GRID 
# =============================================================================
    gdal.ReprojectImage(modopen, dst, modprj, prj, gdal.GRA_Bilinear) ## DEFINE HERE WHICH GDAL INTERP METHOD
    
    del driver, dst
    

