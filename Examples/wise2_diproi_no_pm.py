# -*- coding: utf-8 -*-
"""
Created on Tue May  9 11:30:42 2017

@author: Mic
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:56:47 2017

@author: Mic

- Funziona
- la lascio che c'è da correggere in EllipticalMirror pTan e quindi VersosNorm
- la lascio che c'è ancora l'inifto bisticco tra XYCentre e XYCentre, XYkb1 e XYkb1


"""
import warnings
warnings.filterwarnings("ignore")

import importlib
import numpy as np

import wiselib2.Rayman as rm
import wiselib2.Fundation as Fundation
import wiselib2.Optics as Optics
import wiselib2.ToolLib as tl
importlib.reload(Fundation)
importlib.reload(Optics)
importlib.reload(tl)
importlib.reload(rm)

from wiselib2.must import *
from wiselib2.Fundation import OpticalElement


# SOURCE
#----------------------------------------------------
tl.Debug.On = False
Lambda = 5e-9

# Gaussian Source (if used)
FermiFactor = {'fel1' : 1.25, 'fel2':1.5}['fel2']
FermiSigma = FermiFactor * Lambda * 1e9
FermiWaist = FermiSigma * np.sqrt(2)    
FermiDivergence = Lambda / np.pi/FermiWaist


s = OpticalElement(
                Optics.SourceGaussian(Lambda, FermiWaist, PropagationAngle = 0*0.0008257924757473173 ), 
                PositioningDirectives = Fundation.PositioningDirectives(
                        ReferTo = 'absolute', 
                        XYCentre = [0,1],
                        Angle = np.deg2rad(0)), 
                Name = 'source', IsSource = True)

#----------------------------------------------------
# kb1
#----------------------------------------------------
kb1 = OpticalElement(
                Optics.MirrorElliptic(
                        f1 = 98.5, f2 = 1.180, L= 0.4, Alpha = np.deg2rad(2)), 
                PositioningDirectives = Fundation.PositioningDirectives(
                        ReferTo = 'upstream',
                        PlaceWhat = 'upstream focus',
                        PlaceWhere = 'centre',
                        Distance = 98.5), 
                Name = 'kb1')
            
#----------------------------------------------------
# det (detector)
#----------------------------------------------------
det = OpticalElement(
                Optics.OpticsNumericalDependent(
                        ParentOptics = kb1.CoreOptics, 
                        GetXYFunction = kb1.CoreOptics.GetXY_TransversePlaneAtF2,  
                        N = 200,
                        L = 50e-6,
                        Defocus = 0,
                        ReferenceFrame = 'lab') , 
                PositioningDirectives = None, # they are not necessary
                Name = 'det')
#----------------------------------------------------
#% Creo la sequenza di elementi
t = Fundation.BeamlineElements()
t.Append(s)
t.Append(kb1)
t.Append(det)
t.RefreshPositions()
#t.Paint()


NManual =OpticalElement.GetNSamples_2Body(s.CoreOptics.Lambda, kb1,det)


kb1.UseCustomSampling = False
kb1.CustomSamples = NManual

det.UseCustomSampling = True
det.CustomSamples = NManual

#%% propagazione automatica
print(t)
t.ComputeFields()

#%%propagazione a mano m1 --> f5
Lambda = s.OpticsCore.Lambda
m1_x, m1_y = m1.GetXY(NManual)
m1.ComputedField = s.OpticsCore.EvalField(Lambda,m1_x, m1_y)
plt.figure(9)
plt.plot(abs(m1.ComputedField))
plt.title('Amplitude on m1')

f5_x, f5_y = f5.GetXY(NManual)
f5.ComputedField = rm.HuygensIntegral_1d_MultiPool(Lambda, m1.ComputedField, m1_x, m1_y, f5_x, f5_y, NPools=1)
plt.figure(91)
plt.plot(abs(f5.ComputedField))
plt.title('Amplitude on f5')

#%% propagazione a mano  f5 ---> det

f5_x, f5_y = f5.GetXY(NManual)
det_x, det_y = det.GetXY(NManual)
det.ComputedField = rm.HuygensIntegral_1d_MultiPool(s_k.Lambda, f5.ComputedField, f5_x, f5_y, det_x, det_y, NPools=5)
#%%
plt.figure(11)
plt.plot(abs(det.ComputedField))
plt.title('Amplitude on the screen')


