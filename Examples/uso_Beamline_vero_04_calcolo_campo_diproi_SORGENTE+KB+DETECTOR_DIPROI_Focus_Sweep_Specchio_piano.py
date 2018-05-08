# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:56:47 2017

@author: Mic

- Funziona
- la lascio che c'è da correggere in EllipticalMirror pTan e quindi VersosNorm
- la lascio che c'è ancora l'inifto bisticco tra XYCentre e XYCentre, XYF1 e XYF1


"""
import importlib
import numpy as np

import wiselib2.Rayman as rm
import wiselib2.Fundation as Fundation
import wiselib2.Optics as Optics
import wiselib2.ToolLib as tl
import csv
importlib.reload(Fundation)
importlib.reload(Optics)
importlib.reload(tl)
importlib.reload(rm)

from wiselib2.must import *
from wiselib2.Fundation import OpticalElement

print(__name__)
if __name__ == '__main__':

    tl.Debug.On = True
    # SOURCE
    #------------------------------------------------------------
    Lambda = 5e-9
    Waist0 =60e-6
    s_k = Optics.SourceGaussian(Lambda, Waist0)
    s_pd = Fundation.PositioningDirectives(
                        ReferTo = 'absolute', 
                        XYCentre = [0,0],
                        Angle = np.deg2rad(0))
    s = OpticalElement(
                        s_k, 
                        PositioningDirectives = s_pd, 
                        Name = 'source', IsSource = True)


    # KB(h)
    #------------------------------------------------------------    
    f1 = 16
    f2 = 4
    kbh_k = Optics.MirrorElliptic(f1 = f1, f2 = f2 , L= 0.4, Alpha = np.deg2rad(2.5))
    kbh_pd = Fundation.PositioningDirectives(
                        ReferTo = 'source',
                        PlaceWhat = 'upstream focus',
                        PlaceWhere = 'centre')
    kbh = OpticalElement(
                        kbh_k, 
                        PositioningDirectives = kbh_pd, 
                        Name = 'kbh')

    

    # detector (h)
    #------------------------------------------------------------
    d_k = Optics.Detector(
                        L=100e-6, 
                        AngleGrazing = np.deg2rad(90) )
    d_pd = Fundation.PositioningDirectives(
                        ReferTo = 'upstream',
                        PlaceWhat = 'centre',
                        PlaceWhere = 'downstream focus',
                        Distance = 0)
    d = OpticalElement(
                        d_k, 
                        PositioningDirectives = d_pd, 
                        Name = 'detector')


    # Assemblamento beamline
    #------------------------------------------------------------
    t = None
    t = Fundation.BeamlineElements()
    t.Append(s)
#    t.Append(pm1a)
    t.Append(kbh)
    t.Append(d)
    t.RefreshPositions()




    #%%      Calcolo il campo fin sullo specchio
    
    t.ComputationSettings.NPools = 1
    t.ComputeFields(s,kbh, Verbose = False)
    
    #%%      plotr Del raggio di curvature
    plt.figure(1)
    z_ = np.linspace(11,32,1000)
    R_ = s.CoreOptics.RCurvature(z_)
    plot(z_,R_-z_)
    #plot(z_,z_,'-')
    plt.xlabel('z (m)')
    plt.ylabel('R (m)')

#%% Focus Sweep

    '''
    Il modo più semplice di pensare il focus sweep è:
        - propagare il campo fin sullo specchio (lo specchio POSSIEDE un campo calcolato)
        - usare la funzione Focus

    '''
    DefocusList = np.linspace(-40e-3, 0e-3,   21)
    DefocusList_mm = DefocusList * 1e3

    ResultList, HewList, More = Fundation.FocusSweep(kbh, DefocusList, DetectorSize = 50e-6)

    N = len(ResultList)
    
    for Res in ResultList:
        plt.figure()
        plot(abs(Res.Field))

#%%
    
    plt.figure()
    plot(DefocusList_mm, HewList,'.')
    plt.xlabel('defocus (mm)')
    plt.ylabel('Hew')
    
#%% confronto con waist

    iMin = tl.MinHew(HewList)
    zMin = DefocusList[iMin]
    r = ResultList[iMin].S
    ISym = abs(ResultList[iMin].Field)**2
    ISym = ISym / max(ISym)
    
    (a, x0, sigma) = tl.FitGaussian1d(ISym, r)
    
    plt.figure(1)
    plot(r*1e6,ISym,'g')
    plt.xlabel('um')
    #%%
    plt.figure()
    r2 = np.linspace(-100e-6, 100e-6, 1000)
    ITeo2 = s.CoreOptics.Amplitude(r2,0)**2
    
    
    (a2, x02, sigma2) = tl.FitGaussian1d(ITeo2, r2)
     
    plot(r2*1e6,ITeo2 ,'r')
    plt.xlabel('um')


    sigma2/sigma
    
    #%% provo a vedere quanto vale il pi*w0^2/lambda^2/z^2, che chiamo gamma
    z = f1
#    zRatio = (np.pi * s_k.Waist0**2 / s_k.Lambda/z)**2
    zRatio = s_k.RayleighRange**2/z**2
    g = zRatio * 1e3
    gg = 25/g
    print(g)
    print(gg)
    
    
    #%% provo con la costruzione geometrica
    
    N = 100
    [Mir_x, Mir_y] = kbh.CoreOptics.GetXY(N)

    pOutList = np.zeros(N)
    for (i,x) in enumerate( Mir_x):
        pIn, pOut = kbh_k.TraceRay([0,0], x)
        pOutList[i] = pOut    
     
    
    
    
    
