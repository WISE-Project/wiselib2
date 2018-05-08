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

import Rayman as rm
import Fundation
import Optics
import ToolLib as tl
import csv
import FermiSource as Fermi

importlib.reload(Fundation)
importlib.reload(Optics)
importlib.reload(tl)
importlib.reload(rm)
importlib.reload(Fermi)

from must import *
from Fundation import OpticalElement

print(__name__)
if __name__ == '__main__':

	tl.Debug.On = True
	
	# SOURCE
	#------------------------------------------------------------
	Lambda = 5e-9
	Waist0 =Fermi.Waist0E(Lambda)
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
	f1 = Fermi.Dpi.Kbv.f1
	f2 = Fermi.Dpi.Kbv.f2
	GrazingAngle = Fermi.Dpi.Kbv.GrazingAngle
	
	kb_k = Optics.MirrorElliptic(f1 = f1, f2 = f2 , L= 0.4, Alpha = GrazingAngle)
	kb_k.ComputationSettings.UseIdeal = False
	kb_k.ComputationSettings.UseFigureError = True
	kb_k.ComputationSettings.UseRoughness = False 
	kb_k.FigureErrorLoad(File = "D:\\Topics\\WISE\\Scripts Sviluppo Fase 2c\\DATI\\kbv.txt", Step = 2e-3)
	
	kb_pd = Fundation.PositioningDirectives(
						ReferTo = 'source',
						PlaceWhat = 'upstream focus',
						PlaceWhere = 'centre')
	kb = OpticalElement(
						kb_k, 
						PositioningDirectives = kb_pd, 
						Name = 'kb')

	

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
	t.Append(kb)
	t.Append(d)
	t.RefreshPositions()

	#%%
	kb_k.XYStart
	kb_k._XYProp_End
	[XYs, XYe] = kb_k._ComputeXYStartXYEnd(kb_k.L,'lab')
	
	
	#%% ---- mostro profilo specchio ----
	
	x,y= kb_k.GetXY(300)
	xx,yy = kb_k.GetXY_IdealMirror(300)
	#%%	  Calcolo il campo: sorgente -> specchio
	
	t.ComputationSettings.NPools = 1
	t.ComputeFields(s,kb, Verbose = False)
	
	# Plotto il campo sullo specchio
	if 1==1:
		
		S = kb.ComputationResults.S
		E = kb.ComputationResults.Field
		#------------------
		plt.figure(10)
		plot(S*1e3, abs(E)**2)
		plt.xlabel('mm')
		plt.title('|E|^2 (mirror)')
		#------------------
		plt.figure(11)
		plot(S*1e3, np.angle(E))
		plt.xlabel('mm')
		plt.title('phase(E) (mirror)')
		
	#%%	  plotr Del raggio di curvature
	plt.figure(1)
	z_ = np.linspace(11,32,1000)
	R_ = s.CoreOptics.RCurvature(z_)
	plot(z_,R_-z_)
	#plot(z_,z_,'-')
	plt.xlabel('z (m)')
	plt.ylabel('R (m)')

#%% Caustica
#----------------------------------------------------------------------------------------------------------

	DefocusList = np.linspace(-5e-3, 5e-3,   21)
	DefocusList_mm = DefocusList * 1e3

	ResultList, HewList,SigmaList, More = Fundation.FocusSweep(kb, DefocusList, DetectorSize = 50e-6)

	N = len(ResultList)
	# Plotta il campo sui detector a varie distanze
	if 1==1:
		for Res in ResultList:
			plt.figure()
			plot(abs(Res.Field))
			plt.title('Caustic')


				
#%% Plot della HEW
	
	plt.figure()
	plot(DefocusList_mm, HewList,'.')
	plot(DefocusList_mm, 2*0.68* SigmaList,'x')
	
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
	

	 
	
	
	
	
