
### (Aurélien) Rajouter dans la classe material ou meme dans une autre classe la création de matériaux 
#   pour le modèle thermique -> regarder sur internet 

#  et aussi attention dans la classe stator -> regarder l'utilisation de la classe Material





import femm
from math import pi, cos, sqrt
import numpy as np


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
								Material definition
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """

class Material: 
	def __init__(self, name, Mu_x, Mu_y, H_c, J, Cduct, Lam_d, Phi_max, Lam_fill, Lam_type, Phi_hx, Phi_hy, Nstrands, WireD):
		
		self.Mu_x = Mu_x
		self.Mu_y = Mu_y
		self.H_c =  H_c
		self.J = J
		self.Cduct = Cduct
		self.Lam_d = Lam_d
		self.Phi_max = Phi_max
		self.Lam_fill = Lam_fill
		self.Lam_type = Lam_type
		self.Phi_hx = Phi_hx
		self.Phi_hy = Phi_hy
		self.Nstrands = Nstrands
		self.WireD = WireD  
	
	### (Aurélien) rajout du self dans la fonction add_materials

	def add_materials(J_den, SRatioLongueurActive, k_w, TempAimant, SNShunt):

		"""Material: FlagBHpoint=0 calcul linéaire et FlagBHpoint=1 calcul non linéaire """
#        FlagBHpoint=1                       # réutilisés dans Material_definition
		FlagBHpointAimant=0
		FlagToleranceAimant=2               # =1 mini		=2 nominal		=3 maxi
		
		" Air "
		air = Material('air', 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, None, None)
		femm.mi_addmaterial('air', air.Mu_x, air.Mu_y , air.H_c, air.J, air.Cduct, air.Lam_d, air.Phi_max, air.Lam_fill, air.Lam_type, air.Phi_hx, air.Phi_hy)
		
		
		" NOMEX "
		Nomex = Material('Nomex', 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, None, None)
		femm.mi_addmaterial('Nomex', Nomex.Mu_x, Nomex.Mu_y , Nomex.H_c, Nomex.J, Nomex.Cduct, Nomex.Lam_d, Nomex.Phi_max, Nomex.Lam_fill, Nomex.Lam_type, Nomex.Phi_hx, Nomex.Phi_hy);
		
			
		" COPPER WIRE "
		copper = Material('copper', 1, 1, 0, 0, 58, 0, 0, 1, 0, 0, 0, 0, 1)
		femm.mi_addmaterial('copper', copper.Mu_x, copper.Mu_y , copper.H_c, copper.J, copper.Cduct, copper.Lam_d, copper.Phi_max, copper.Lam_fill, copper.Lam_type, copper.Phi_hx, copper.Phi_hy, copper.Nstrands, copper.WireD);		
			
		# Cduct = 58 : conductance du cuivre  ;  =0 : résistance du bobinage non pris en compte, à rajouter aprés)
		# Lam_type = 0 :laminated in plane ; 3 : magnet wire) [AK]
		# WireD = 1 not considered in further calculation by FEMM [AK]
		
			
		
		""" specification for current density - J_den_tot """
		   
		J_MatiereCuivre_Ap= sqrt(2)*J_den*k_w    # J_den_tot
		femm.mi_addmaterial('A+', copper.Mu_x, copper.Mu_y , copper.H_c,J_MatiereCuivre_Ap, copper.Cduct, copper.Lam_d, copper.Phi_max, copper.Lam_fill, copper.Lam_type, copper.Phi_hx, copper.Phi_hy, copper.Nstrands, copper.WireD)	
		J_MatiereCuivre_An= (-1)* sqrt(2)*J_den*k_w
		femm.mi_addmaterial('A-', copper.Mu_x, copper.Mu_y , copper.H_c,J_MatiereCuivre_An, copper.Cduct, copper.Lam_d, copper.Phi_max, copper.Lam_fill, copper.Lam_type, copper.Phi_hx, copper.Phi_hy, copper.Nstrands, copper.WireD)	
			
		J_MatiereCuivre_Bp=sqrt(2)*J_den*k_w*cos(2*pi/3)
		femm.mi_addmaterial('B+', copper.Mu_x, copper.Mu_y , copper.H_c,J_MatiereCuivre_Bp, copper.Cduct, copper.Lam_d, copper.Phi_max, copper.Lam_fill, copper.Lam_type, copper.Phi_hx, copper.Phi_hy, copper.Nstrands, copper.WireD)		
		J_MatiereCuivre_Bn=(-1)* sqrt(2)*J_den*k_w*cos(2*pi/3);
		femm.mi_addmaterial('B-', copper.Mu_x, copper.Mu_y , copper.H_c,J_MatiereCuivre_Bn, copper.Cduct, copper.Lam_d, copper.Phi_max, copper.Lam_fill, copper.Lam_type, copper.Phi_hx, copper.Phi_hy, copper.Nstrands, copper.WireD)		
			
			
		J_MatiereCuivre_Cp=sqrt(2)*J_den*k_w*cos(4*pi/3)
		femm.mi_addmaterial('C+', copper.Mu_x, copper.Mu_y , copper.H_c,J_MatiereCuivre_Cp, copper.Cduct, copper.Lam_d, copper.Phi_max, copper.Lam_fill, copper.Lam_type, copper.Phi_hx, copper.Phi_hy, copper.Nstrands, copper.WireD)		
		J_MatiereCuivre_Cn=(-1)* sqrt(2)*J_den*k_w*cos(4*pi/3)
		femm.mi_addmaterial('C-', copper.Mu_x, copper.Mu_y , copper.H_c,J_MatiereCuivre_Cn, copper.Cduct, copper.Lam_d, copper.Phi_max, copper.Lam_fill, copper.Lam_type, copper.Phi_hx, copper.Phi_hy, copper.Nstrands, copper.WireD)
			
		
		""" MATERIAL SHEETS : MAAMAR """
		Maamar_tole = Material('FeSi M19 3%', 1000, 1000, 0, 0, 1/249.3e-9/1e6, 0.35, 0, SRatioLongueurActive, 0, 0, 0, None, None)
		
		# Cduct = 1/249.3e-9/1e6 (= 1/Resistivity) en Mega Siemens/metre
		# Lam_type = 0 :laminated in plane ; 3 : magnet wire)
		
		femm.mi_addmaterial('FeSi M19 3%', Maamar_tole.Mu_x, Maamar_tole.Mu_y , Maamar_tole.H_c, Maamar_tole.J, Maamar_tole.Cduct, Maamar_tole.Lam_d, Maamar_tole.Phi_max, Maamar_tole.Lam_fill, Maamar_tole.Lam_type, Maamar_tole.Phi_hx, Maamar_tole.Phi_hy)	
		BFeSi=np.array([0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2,2.1,2.2,2.3,2.4,2.5])
		HFeSi=np.array([0,9,17,26,35,43,52,60,71,88,111,145,213,446,1172,2865,5185,8405,13307,21050,54248,118110,197697,277265,356842,436420])
		
		for ii in range(BFeSi.size):
			femm.mi_addbhpoint('FeSi M19 3%',BFeSi[ii],HFeSi[ii])
		
			
		""" MATERIAL SHEETS : ECEPS FeSi """
		ECEPS_tole = Material('FeSi 0.35mm', 1000, 1000, 0, 0, 1/249.3e-9/1e6, 0.35, 0, SRatioLongueurActive, 0, 0, 0, None, None)
		femm.mi_addmaterial('FeSi 0.35mm', ECEPS_tole.Mu_x, ECEPS_tole.Mu_y , ECEPS_tole.H_c, ECEPS_tole.J, ECEPS_tole.Cduct, ECEPS_tole.Lam_d, ECEPS_tole.Phi_max, ECEPS_tole.Lam_fill, ECEPS_tole.Lam_type, ECEPS_tole.Phi_hx, ECEPS_tole.Phi_hy);	
		Htole=np.array([0,24,36,44,54,62,70,81,94,112,134,165,210,290,460,980,2660,5700,10700,18400,30000,45000,70000,120000,200000,280000])
		Btole=np.array([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2,2.1,2.2,2.3,2.4,2.5])
		
		for i in range (Htole.size):
			femm.mi_addbhpoint('FeSi 0.35mm',Btole[i],Htole[i])
		
			
		""" MATERIAL SUPPORT D'AIMANTS : MAAMAR """
		Maamar_aimant = Material('Losil 800/65', 2000, 2000, 0, 0, 1.67, 0, 0, 1, 0, 0, 0, None, None)
		
		# Cduct = 1.67 (=1.67 : Losil 800/65)
		# Lam_type = 0 :laminated in plane ; 3 : magnet wire)
		
		femm.mi_addmaterial('Losil 800/65', Maamar_aimant.Mu_x, Maamar_aimant.Mu_y , Maamar_aimant.H_c, Maamar_aimant.J, Maamar_aimant.Cduct, Maamar_aimant.Lam_d, Maamar_aimant.Phi_max, Maamar_aimant.Lam_fill, Maamar_aimant.Lam_type, Maamar_aimant.Phi_hx, Maamar_aimant.Phi_hy)
		BLosil=np.array([0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2,2.1,2.2,2.3,2.4,2.5])
		HLosil=np.array([0,18,37,55,74,84,96,110,130,155,190,240,320,450,680,1200,2200,5000,9000,15500,24000,36000,75789,155366,234944,314521])
		for ii in range (BLosil.size):
			femm.mi_addbhpoint('Losil 800/65',BLosil[ii],HLosil[ii])
		
			
		""" MATERIAL MAGNETS HOLDER : ECEPS """
		ECEPS_aimant = Material('Matiere_ROTOR', 2000, 2000, 0, 0, 1/130.3e-9/1e6, 0, 0, 1, 0, 0, 0, None, None)
		
		# Cduct = 1/130e-9/1e6 (= 1/Resistivity) en Mega Siemens/metre
		# Lam_type = 0 :laminated in plane ; 3 : magnet wire)
		
		femm.mi_addmaterial('Matiere_ROTOR', ECEPS_aimant.Mu_x, ECEPS_aimant.Mu_y , ECEPS_aimant.H_c, ECEPS_aimant.J, ECEPS_aimant.Cduct, ECEPS_aimant.Lam_d, ECEPS_aimant.Phi_max, ECEPS_aimant.Lam_fill, ECEPS_aimant.Lam_type, ECEPS_aimant.Phi_hx, ECEPS_aimant.Phi_hy)	
		Hrotor=np.array([0,42,70,79,86,95,106,118,132,149,176,210,274,347,576,791,2141,4187,8275,13500,23947,40320,120000,200000,280000,360000])
		Brotor=np.array([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2,2.1,2.2,2.3,2.4,2.5])
						
		for ii in range (Hrotor.size):
			femm.mi_addbhpoint('Matiere_ROTOR',Brotor[ii],Hrotor[ii])
			
			
		""" MAGNETS MATERIAL Sm2Co17 RECOMA 28 """
		Mu0=4*pi/1e7
		Mur=1.05
		CoeffBrTemp=-0.035/100
		
		if (FlagToleranceAimant == 1):
			Br20=1.04
		
		if (FlagToleranceAimant == 2):
			Br20=1.07
		if (FlagToleranceAimant == 3):
			Br20=1.10
		
			# 1.04 Tesla minimum  1.08 Tesla nominal for Parminder  1.07 Tesla nominal for Maamar
			
		Br=Br20*(1+CoeffBrTemp*(TempAimant-20))
		Hcb=Br/Mur/Mu0
#        BHmax=Br*Hcb/4
		Cduct=1/((.75e6+.9e6)/2)/1e6
		
		if (FlagBHpointAimant == 0):
			RECOMA_aimant = Material('Sm2Co17', Mur, Mur, Hcb, 0, 1/((.75e6+.9e6)/2)/1e6, 0, 0, 1, 0, 0, 0, None, None)
			# Lam_type = 0 :laminated in plane ; 3 : magnet wire)
			femm.mi_addmaterial('Sm2Co17', RECOMA_aimant.Mu_x, RECOMA_aimant.Mu_y , RECOMA_aimant.H_c, RECOMA_aimant.J, RECOMA_aimant.Cduct, RECOMA_aimant.Lam_d, RECOMA_aimant.Phi_max, RECOMA_aimant.Lam_fill, RECOMA_aimant.Lam_type, RECOMA_aimant.Phi_hx, RECOMA_aimant.Phi_hy)	
		else:
			HAim=np.array([0,.1,.2,.3,.4,.5,.6,.7,.8])
			BAim=np.array([0,.1375,.275,.4125,.55,.6875,.825,.9625,1.1])
			BSmCo=np.array([])
			HSmCo=np.array([])
			for ii in range (HAim.size):
				BSmCo.append(BAim[ii]+Br-BAim[9])
				HSmCo.append(HAim[ii]*1e6)
				if (BSmCo[1]<0):
					BSmCo[1]=0
			RECOMA_28_aimant = Material('Sm2Co17 Recoma 28', Mur, Mur, HSmCo[9], 0, 1/((.75e6+.9e6)/2)/1e6, 0, 0, 1, 0, 0, 0, None, None)
			# Lam_type = 0 :laminated in plane ; 3 : magnet wire)
			femm.mi_addmaterial('Sm2Co17 Recoma 28', RECOMA_28_aimant.Mu_x, RECOMA_28_aimant.Mu_y , RECOMA_28_aimant.H_c, RECOMA_28_aimant.J, RECOMA_28_aimant.Cduct, RECOMA_28_aimant.Lam_d, RECOMA_28_aimant.Phi_max, RECOMA_28_aimant.Lam_fill, RECOMA_28_aimant.Lam_type, RECOMA_28_aimant.Phi_hx, RECOMA_28_aimant.Phi_hy)	
			for ii in range (BSmCo.size):
				femm.mi_addbhpoint('Sm2Co17 Recoma 28',BSmCo[ii],HSmCo[ii])
		
		
		""" SHEETS MATERIAL """
		tole = Material('FeSi M19 3% SHUNT', 1000, 1000, 0, 0, 1/249.3e-9/1e6, 0.35, 0, SNShunt*SRatioLongueurActive, 0, 0, 0, None, None)
		
		# Cduct = 1/249.3e-9/1e6 (= 1/Resistivity) en Mega Siemens/metre
		# Lam_type = 0 :laminated in plane ; 3 : magnet wire)
		
		femm.mi_addmaterial('FeSi M19 3% SHUNT', tole.Mu_x, tole.Mu_y, tole.H_c, tole.J, tole.Cduct, tole.Lam_d, tole.Phi_max, tole.Lam_fill, tole.Lam_type, tole.Phi_hx, tole.Phi_hy)	
		BFeSi=np.array([0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2,2.1,2.2,2.3,2.4,2.5])
		HFeSi=np.array([0,9,17,26,35,43,52,60,71,88,111,145,213,446,1172,2865,5185,8405,13307,21050,54248,118110,197697,277265,356842,436420])
		for ii in range (BFeSi.size):
			femm.mi_addbhpoint('FeSi M19 3% SHUNT',BFeSi[ii],HFeSi[ii])
		
		
		""" MATERIAL ROTOR INSIDER TUBE  : CX13VDW measured by CEDRAT """
		CX13VDW_tube_int_rot = Material('CX13VDW', 2000, 2000, 0, 0, 1/77e-8/1e6, 0, 0, 1, 0, 0, 0, None, None)
		
		# Cduct = 1/77e-8/1e-6 (= 1/Resistivity) en Mega Siemens/metre
		# Lam_type = 0 :laminated in plane ; 3 : magnet wire)
		
		femm.mi_addmaterial('CX13VDW', CX13VDW_tube_int_rot.Mu_x, CX13VDW_tube_int_rot.Mu_y , CX13VDW_tube_int_rot.H_c, CX13VDW_tube_int_rot.J, CX13VDW_tube_int_rot.Cduct, CX13VDW_tube_int_rot.Lam_d, CX13VDW_tube_int_rot.Phi_max, CX13VDW_tube_int_rot.Lam_fill, CX13VDW_tube_int_rot.Lam_type, CX13VDW_tube_int_rot.Phi_hx, CX13VDW_tube_int_rot.Phi_hy)
		HCX13VDW=np.array([0,262,720,1049,1532,1863,2315,2799,3092,3614,3914,4388,4888,5216,5689,5995,6770,13561,20121,27517,37246,48142,86000,166000,246000,326000,406000,486000,566000,646000,726000,806000])
		BCX13VDW=np.array([0,0.0118,0.0295,0.0407,0.0634,0.0793,0.1148,0.1639,0.2069,0.3221,0.4083,0.5155,0.5981,0.6449,0.7016,0.7341,0.8026,1.1120,1.2626,1.3768,1.4829,1.5527,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5])
		for ii in range (BCX13VDW.size):
			femm.mi_addbhpoint('CX13VDW',BCX13VDW[ii],HCX13VDW[ii])
			
			
		"""" MATERIAL ROTOR INSIDER TUBE : XD15NW measured by CEDRAT """
		XD15NW_tube_int_rot = Material('CX13VDW', 2000, 2000, 0, 0, 1/77e-8/1e6, 0, 0, 1, 0, 0, 0, None, None)
		
		# Cduct = 1/77e-8/1e6 (= 1/Resistivity) en Mega Siemens/metre
		# Lam_type = 0 :laminated in plane ; 3 : magnet wire)
		
		femm.mi_addmaterial('XD15NW', XD15NW_tube_int_rot.Mu_x, XD15NW_tube_int_rot.Mu_y , XD15NW_tube_int_rot.H_c, XD15NW_tube_int_rot.J,Cduct, XD15NW_tube_int_rot.Lam_d, XD15NW_tube_int_rot.Phi_max, XD15NW_tube_int_rot.Lam_fill, XD15NW_tube_int_rot.Lam_type, XD15NW_tube_int_rot.Phi_hx, XD15NW_tube_int_rot.Phi_hy)	
		HXD15NW=np.array([0,359,902,1230,1738,2043,2520,2898,3351,3848,4174,4701,4953,5512,5795,6333,6897,13965,20704,29830,37490,43295,61200,221200,381200,541200,701200,861200,1021200])
		BXD15NW=np.array([0,0.0134,0.0242,0.0335,0.0467,0.0577,0.0740,0.0849,0.1064,0.1337,0.1652,0.2252,0.2893,0.3918,0.4529,0.5216,0.5938,0.8822,0.9902,1.0813,1.1379,1.1776,1.2,1.4,1.6,1.8,2.0,2.2,2.4])
		for ii in range (BXD15NW.size):
			femm.mi_addbhpoint('XD15NW',BXD15NW[ii],HXD15NW[ii])
			
			
		""" MATERIAL ROTOR INSIDER TUBE : BS-S98, ECEPS data"""
		BS_S98_tube_int_rot = Material('CX13VDW', 2000, 2000, 0, 0, 1/77e-8/1e6, 0, 0, 1, 0, 0, 0, None, None)
		
		# Cduct = 1/77e-8/1e6 (= 1/Resistivity) en Mega Siemens/metre
		# Lam_type = 0 :laminated in plane ; 3 : magnet wire)
		
		femm.mi_addmaterial('BS_S98', BS_S98_tube_int_rot.Mu_x, BS_S98_tube_int_rot.Mu_y , BS_S98_tube_int_rot.H_c, BS_S98_tube_int_rot.J, BS_S98_tube_int_rot.Cduct, BS_S98_tube_int_rot.Lam_d, BS_S98_tube_int_rot.Phi_max, BS_S98_tube_int_rot.Lam_fill, BS_S98_tube_int_rot.Lam_type, BS_S98_tube_int_rot.Phi_hx, BS_S98_tube_int_rot.Phi_hy)
		HBSS98=np.array([0,80,239,398,557,796,955,1194,1592,3183,3979,4775,7958,11937,15915,19894,99894,179894,259894,339894,419894,499894])
		BBSS98=np.array([0,0.013,0.03,0.05,0.08,0.17,0.35,0.8,1.185,1.59,1.66,1.72,1.805,1.835,1.84,1.845,1.945,2.045,2.145,2.245,2.345,2.445])	
		for ii in range (BBSS98.size):
				femm.mi_addbhpoint('BS-S98',BBSS98[ii],HBSS98[ii])
