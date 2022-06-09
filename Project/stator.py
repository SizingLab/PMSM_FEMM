import femm
from variable import Variable
from rotor import  IPM_Model, IPM_GeomGeneration, SPM_Model, SPM_GeomGeneration, Halbach_Model, Halbach_GeomGeneration
import numpy as np
from math import pi, cos, sin, asin, floor, tan, sqrt

import pandas as pd
import ipywidgets as widgets

class Concentrated:
        
    'Geometric paramters of the stator'
    Ne = Variable('Ne', 12, '[Slots]', 'Slot number of the motor')
    Ne_ref = Variable('Ne_ref', 12, '[Slots]', 'Slot number of the motor reference' )
    KNe = Variable('KNe', Ne.value/Ne_ref.value, '[-]', 'Coefficient ration of the slots')
    NbDemiEncoche = Variable('NbDemiEncoche', 0, '[-]', 'Number of half-slot (0:Single-layer, 2;Double-layer)')
    ACwind = Variable('ACwind', 0, '[-]', 'Sinisoidal winding: 0 (No sinusoidal winding) ou 1 (Sinusoidal winding)')
    SLa = Variable('SLa', 2.35, '[-]' ,'Opening slot width')
    SLo = Variable('SLo', 0.6, '[-]', 'Tooth thickness at the opening slot')
    SEp = Variable('SEp', 2.62, '[mm]', 'Yoke thickness')
    SLd = Variable('SLd', 4.48, '[mm]', 'Tooth thickness')
    SAngDepEncoche = Variable('SAngDepEncoche', 15*pi/180, '[-]', 'Clearance angle of the tooth at the opening')
    SHc = Variable('SHc', 1.00, '[-]', 'depression in the radius of the sheets in the breech')
    SHjx = Variable('SHjx', 0.10, '[-]', 'x-slot play of the plates in the cylinder head')
    SHjy = Variable('SHjy', 0.10, '[-]', 'y-slot play of the plates in the cylinder head')
    SENomex = Variable('SENomex', 0.3, '[mm]', 'thickness of the nomex film insulating in the slot') #0.3
    SRiNomex = Variable('SRiNomex',1.25 , '[mm]', 'Interior raidus of the Nomex film') #1.25
    SNShunt = Variable('SNShunt', 0/5, '[-]', 'into the shunt : 1 metal sheet out of 5')
    SRatioLongueurActive = Variable('SRatioLongueurActive', 0.97, '[-]', 'ratio giving the active length of the bundle of sheets participating in the torque')
    k_w = Variable('k_w', 0.24, '[-]', 'winding coefficient')
    

    """ Definition of the exterior contour limiting the problem """

### (Aurélien) Ajout du femm_wrapper

    def __init__(self, femm_wrapper, rotor_model='IPM', motif='10/12', repetition='1', SEp=SEp, SLd=SLd, Ne=Ne, Ne_ref=Ne_ref, KNe=KNe, NbDemiEncoche=NbDemiEncoche,
                 ACwind=ACwind, SLa=SLa, SLo=SLo, SAngDepEncoche=SAngDepEncoche, SHc=SHc, SHjx=SHjx, SHjy=SHjy, 
                 SENomex=SENomex, SRiNomex=SRiNomex, SNShunt=SNShunt, SRatioLongueurActive=SRatioLongueurActive, k_w=k_w):
        
        if rotor_model == 'IPM':
### (Aurélien) Changement en IPM_Model ???
            self.rotor = IPM_Model()
        elif rotor_model == 'SPM':
            self.rotor = SPM_Model()
        elif rotor_model == 'Halbach':
            self.rotor = Halbach_Model()
        else: 
            raise TypeError('Unknown rotor type')

        # Stator parameters
        self.parameters = {}
        self.repetition = repetition
        self.motif = motif
        self.rotor_type = rotor_model
        self.parameters[SEp.name] = SEp
        self.parameters[SLd.name] = SLd
        self.parameters[Ne.name] = Ne
        self.parameters[Ne_ref.name] = Ne_ref
        self.parameters[KNe.name] = KNe
        self.parameters[NbDemiEncoche.name] = NbDemiEncoche
        self.parameters[ACwind.name] = ACwind
        self.parameters[SLa.name] = SLa
        self.parameters[SLo.name] = SLo
        self.parameters[SAngDepEncoche.name] = SAngDepEncoche
        self.parameters[SHc.name] = SHc
        self.parameters[SHjx.name] = SHjx
        self.parameters[SHjy.name] = SHjy
        self.parameters[SENomex.name] = SENomex
        self.parameters[SRiNomex.name] = SRiNomex
        self.parameters[SNShunt.name] = SNShunt
        self.parameters[SRatioLongueurActive.name] = SRatioLongueurActive
        self.parameters[k_w.name] = k_w

        self.data_frame = pd.DataFrame()

        self.femm_wrapper = femm_wrapper

        self.build()

#        self.build_data_frame()

    def build(self):
        repetition = self.repetition
        # Rotor parameters
        K = self.rotor.parameters['K'].value
        self.rotor.parameters['SRe'].value = self.rotor.parameters['SDe'].value/2
        SRe = self.rotor.parameters['SRe'].value 
        TailleMailleEntrefer = self.rotor.parameters['TailleMailleEntrefer'].value*K
        SRi = self.rotor.parameters['SRi'].value*K
        
        # Stator parameters
        Ne = int(self.motif.split('/')[1])
        self.parameters['Ne'].value = Ne       
        Ne = self.parameters['Ne'].value
        
        Ne_ref = self.parameters['Ne_ref'].value
        self.parameters['KNe'].value = Ne/Ne_ref
        KNe = self.parameters['KNe'].value
        
        SLa = self.parameters['SLa'].value*K/KNe
        SLo = self.parameters['SLo'].value*K/KNe
        SAngDepEncoche = self.parameters['SAngDepEncoche'].value*KNe
        SENomex = self.parameters['SENomex'].value
        SRiNomex = self.parameters['SRiNomex'].value/KNe*K
        
        if self.rotor_type == 'IPM':
            self.parameters['SEp'].value = 2.62 
            SEp = self.parameters['SEp'].value*K
            self.parameters['SLd'].value = 4.48 
            SLd = self.parameters['SLd'].value*K/KNe
            self.parameters['SLa'].value = 2.35
            SLa = self.parameters['SLa'].value*K/KNe
            self.parameters['SLo'].value = 0.6
            SLo = self.parameters['SLo'].value*K/KNe
            
        elif self.rotor_type == 'SPM' or 'Halbach':
            self.parameters['SEp'].value = 3.17
            SEp = self.parameters['SEp'].value*K
            self.parameters['SLd'].value = 6.83 
            SLd = self.parameters['SLd'].value*K
            self.parameters['SLa'].value = 2.35
            SLa = self.parameters['SLa'].value*K
            self.parameters['SLo'].value = 1.015
            SLo = self.parameters['SLo'].value*K
            
        self.parameters['SAngDepEncoche'].value = 15*pi*KNe/180
        SAngDepEncoche = self.parameters['SAngDepEncoche'].value

        self.SRfe = Variable('SRfe', SRe-SEp, '[mm]', 'Stator rayon at the end of the slot')  
        self.parameters['SRfe'] = self.SRfe
        SRfe = self.parameters['SRfe'].value

        """ Groups Definition"""
        # 	Magnets 					     : groupe 3
        #	air inside the rotor	         : groupe 1	
        #	breech         				     : groupe 4
        #	sheets 						     : groupe 6
        #   tooth                            : groupe 5
        #	coils phase 1  plus			     : groupe 7
        #	coils phase 1 minus			     : groupe 7
        #	coils phase 2 plus			     : groupe 7
        #	coils phase 2 minus 			 : groupe 7
        #	coils phase 3 plus 			     : groupe 7
        #	coils phase 3 minus 			 : groupe 7
        #	air in the oppening notch	     : groupe 2
        #	air inside the air gap 			 : groupe 2
        #   magnetic holder

        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Calcul of the winding filling tax (Calcul_BOBINAGE)
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
                # caractéristiques bobinage selon diamétre (RESULTAT_optimisation_Dfil) => choisir le diamétre qui convient
                # calculs bobinage: resitance, longueur fil, puissance dissipée...
        
        """ Calculation of the points defining the geometry of the notch """
        self.SReNomex = SRiNomex +SENomex        # Nomex's external bending radius
        self.SAngElec = 2*pi/Ne                  # angle P O M
        self.parameters['SAngElec']=self.SAngElec
        """ Definition of the connection of the notch bottom with the tooth: points Eo E1 and E2"""
        self.SEx = SLd/(2*repetition)                           # point E (without connecting radius)
        self.SEy = (SRfe**2-(SLd/2)**2)**.5					    # point E (without connecting radius)
        self.SAngEOY=asin(SLd/2/SRfe)						    # angle E Origin Axis Y
        self.SEox =SLd/2+self.SReNomex						    # centre Eo of the cercle
        self.SEoy=((SRfe-self.SReNomex)**2-self.SEox**2)**.5    # centre Eo of the cercle
        self.SAngEoOY=asin(self.SEox/(SRfe-self.SReNomex))	    # angle Eo Origin Axis Y
        self.SAngL1pOEo=self.SAngElec-self.SAngEoOY*2		    # angle Lp Origin Eo 
        self.SE1x=SRfe*sin(self.SAngEoOY)		                # connection of the notch bottom with the connection radius E1
        self.SE1y=SRfe*cos(self.SAngEoOY)	             		# raccordement du fond d'encoche avec le rayon de raccordement E1
        self.SE2x=SLd/2											# connection of the connection radius with the tooth E2
        self.SE2y=self.SEoy						       			# connection of the connection radius with the tooth E2
        self.SAngE1EoE2=pi/2+self.SAngEoOY						# angle E1 Eo E2
        
        """ Definition of point H """
        self.SAngVOH=asin(SLa/2/SRi)*2					         	# angle Ip O H
        self.SHx=SRi*(sin(self.SAngElec/2-self.SAngVOH/2))			# point H
        self.SHy=SRi*(cos(self.SAngElec/2-self.SAngVOH/2))			# point H
        self.SAngHOI=self.SAngElec-self.SAngVOH						# angle Ip Origin H
        
        """ Definition of point G """
        self.SGx=self.SHx+SLo*sin(self.SAngElec/2-self.SAngVOH/2)			# point G
        self.SGy=self.SHy+SLo*cos(self.SAngElec/2-self.SAngVOH/2)			# point G
        
        """ Definition of the connection of the tooth with the polar form: points FO F1 and F2 """
        self.SAngYFG=pi/2+SAngDepEncoche+self.SAngElec/2		    				# angle axis Y with FG segment
        self.SFx=SLd/2													          # point F (without connection radius)
        self.SFy=self.SGy+(self.SGx-self.SFx)*tan(SAngDepEncoche+self.SAngElec/2)			   # point F (without connection radius)
        self.SFox=SLd/2+self.SReNomex											      # centre of the cercle FO	
        self.SFoy=self.SFy+self.SReNomex/tan(self.SAngYFG/2)							      # centre of the cercle FO
        self.SF1x=self.SFx                                                     # connection of the tooth with the polar form : point F1	
        self.SF1y=self.SFoy            									          # connection of the tooth with the polar form : point F1
        self.SF2x=self.SFox+self.SReNomex*cos(-(SAngDepEncoche+self.SAngElec/2)-pi/2)	   # connection of the tooth with the polar form : point F2
        self.SF2y=self.SF1y+self.SReNomex*sin(-(SAngDepEncoche+self.SAngElec/2)-pi/2)	   # connection of the tooth with the polar form : point F2
        
        self.SAngF1FoF2=(pi/2-self.SAngYFG/2)*2       						       # angle F1 Fo F2
        """% fprintf(1,'SAngYFG = %f degr� \n',SAngYFG/pi*180);
        % fprintf(1,'SAngF1FoF2 = %f degr� \n',SAngF1FoF2/pi*180);"""
        
        """ Definition of point L mirror of E relative to Y """
        self.SLx=-self.SEx
        self.SLy=self.SEy
        
        """ Definition of points L1 and L2 mirror of E1 and E2 relative to Y """
        self.SL1x=-self.SE1x
        self.SL1y=self.SE1y
        self.SL2x=-self.SE2x
        self.SL2y=self.SE2y
        
        """ Definition of point I mirror of H relative to Y """
        self.SIx=-self.SHx
        self.SIy=self.SHy	
        
        """ Definition of point J mirror of G relative to Y """
        self.SJx=-self.SGx
        self.SJy=self.SGy
        
        """ Definition of points K1 and K2 mirror of F1 and F2 relative to Y """
        self.SK1x=-self.SF1x
        self.SK1y=self.SF1y
        self.SK2x=-self.SF2x
        self.SK2y=self.SF2y		
        
        """ Definition of point M """
        self.SMx=-SRfe*sin(self.SAngElec/2)
        self.SMy=SRfe*cos(self.SAngElec/2)
        
        """ Definition of point Z """
        self.SZx=-(SRe)*sin(self.SAngElec/2)
        self.SZy=(SRe)*cos(self.SAngElec/2)
        
        """ Definition of point W """
        self.SWx=-self.SZx
        self.SWy=self.SZy
        
        """ Definition of point N """
        self.SNx=-(self.SJx**2+self.SJy**2)**.5*sin(self.SAngElec/2)
        self.SNy=(self.SJx**2+self.SJy**2)**.5*cos(self.SAngElec/2)
        
        """ Definition of point P """
        self.SPx=-self.SMx
        self.SPy=self.SMy
        
        """ Definition of point U """
        self.SUx = -self.SNx
        self.SUy = self.SNy
        
        """ Definition of variables used to select arcs and segments """
        self.SPE1x=SRfe*sin((self.SAngElec/2+self.SAngEoOY)/2)
        self.SPE1y=SRfe*cos((self.SAngElec/2+self.SAngEoOY)/2)
        self.SE1E2x=self.SEox+self.SReNomex*cos(pi/2-self.SAngElec/2+self.SAngE1EoE2/2)
        self.SE1E2y=self.SEoy+self.SReNomex*sin(pi/2-self.SAngElec/2+self.SAngE1EoE2/2)
        self.SF1F2x=self.SFox+self.SReNomex*cos(pi+self.SAngF1FoF2/2)
        self.SF1F2y=self.SF1y+self.SReNomex*sin(pi+self.SAngF1FoF2/2)
        self.SL1Mx=-self.SPE1x
        self.SL1My=self.SPE1y
        self.SL1L2x=-self.SE1E2x
        self.SL1L2y=self.SE1E2y
        self.SK1K2x=-self.SF1F2x
        self.SK1K2y=self.SF1F2y
        self.SIJx=0
        self.SIJy=SRi

        
        """ Définition of the max angles for the arcs """
        self.MaxSegDegOG=TailleMailleEntrefer/(self.SGx**2+self.SGy**2)**.5*360
        self.MaxSegDegE1E2=10
        self.MaxSegDegPE1=self.SAngL1pOEo*180/pi/10
            
        """ Definition of these same points for the surface without Nomex """
        """ Right half coil points """
        self.SE1Ix=(SRfe-SENomex)*sin(self.SAngEoOY)                   # Abscissa oh the point SE1I
        self.SE1Iy=(SRfe-SENomex)*cos(self.SAngEoOY)
        self.SE2Ix=SLd/2+SENomex
        self.SE2Iy=self.SEoy
        self.SF1Ix=SLd/2+SENomex
        self.SF1Iy=self.SF1y
        self.SF2Ix=self.SFox+(self.SReNomex-SENomex)*cos(-(SAngDepEncoche+self.SAngElec/2)-pi/2)
        self.SF2Iy=self.SF1y+(self.SReNomex-SENomex)*sin(-(SAngDepEncoche+self.SAngElec/2)-pi/2)
        self.SPIx=(SRfe-SENomex)*sin(self.SAngElec/2)
        self.SPIy=(SRfe-SENomex)*cos(self.SAngElec/2)
        self.SGIx=self.SHx+(SLo+SENomex)*sin(self.SAngElec/2-self.SAngVOH/2)
        self.SGIy=self.SHy+(SLo+SENomex)*cos(self.SAngElec/2-self.SAngVOH/2)	
        self.SUIx=(self.SGIx**2+self.SGIy**2)**.5*sin(self.SAngElec/2)
        self.SUIy=(self.SGIx**2+self.SGIy**2)**.5*cos(self.SAngElec/2)

        """ variables for arcs and segments of the right half notch """
        self.SPIE1Ix=(SRfe-SENomex)*sin((self.SAngElec/2+self.SAngEoOY)/2)
        self.SPIE1Iy=(SRfe-SENomex)*cos((self.SAngElec/2+self.SAngEoOY)/2)
        self.SE1IE2Ix=self.SEox+(self.SReNomex-SENomex)*cos(pi/2-self.SAngElec/2+self.SAngE1EoE2/2)
        self.SE1IE2Iy=self.SEoy+(self.SReNomex-SENomex)*sin(pi/2-self.SAngElec/2+self.SAngE1EoE2/2)
        self.SF1IF2Ix=self.SFox+(self.SReNomex-SENomex)*cos(pi+self.SAngF1FoF2/2)
        self.SF1IF2Iy=self.SFoy+(self.SReNomex-SENomex)*sin(pi+self.SAngF1FoF2/2)
            
        """ Left half coil points """
        self.SMIx=-self.SPIx
        self.SMIy=self.SPIy
        self.SL1Ix=-self.SE1Ix
        self.SL1Iy=self.SE1Iy		
        self.SL2Ix=-self.SE2Ix
        self.SL2Iy=self.SE2Iy
        self.SK1Ix=-self.SF1Ix
        self.SK1Iy=self.SF1Iy
        self.SK2Ix=-self.SF2Ix
        self.SK2Iy=self.SF2Iy
        self.SJIx=-self.SGIx
        self.SJIy=self.SGIy
        self.SNIx=-self.SUIx
        self.SNIy=self.SUIy
        
        """ variables for arcs and segments of the left half notch """
        self.SMIL1Ix=-self.SPIE1Ix
        self.SMIL1Iy=self.SPIE1Iy
        self.SL1IL2Ix=-self.SE1IE2Ix
        self.SL1IL2Iy=self.SE1IE2Iy
        self.SK1IK2Ix=-self.SF1IF2Ix
        self.SK1IK2Iy=self.SF1IF2Iy       
    
    def get_value_temp_s2(self):
        return self.SPx,self.SPy,self.SE1x,self.SE1y,self.SE2x,self.SE2y,self.SF1x,self.SF1y,self.SF2x,self.SF2y,self.SGx,self.SGy,self.SUx,self.SUy,self.SMx,self.SMy,self.SZx,self.SZy,self.SWx,self.SWy,self.SAngL1pOEo,self.SAngE1EoE2,self.SAngF1FoF2,self.SPE1x,self.SPE1y,self.SE1E2x,self.SE1E2y,self.SF1F2x,self.SF1F2y,self.MaxSegDegOG
    
    def get_value_stator(self):
        return self.SHx,self.SHy,self.SIx,self.SIy,self.SJx,self.SJy,self.SK1x,self.SK1y,self.SK2x,self.SK2y,self.SL1x,self.SL1y,self.SL2x,self.SL2y,self.SNx,self.SNy,self.SL1Mx,self.SL1My,self.SIJx,self.SIJy,self.SL1L2x,self.SL1L2y,self.SK1K2x,self.SK1K2y,self.SAngHOI,self.BSigneBob,self.BNomBob,self.NbDemiEncoche,self.MaxSegDegPE1,self.MaxSegDegE1E2

    def draw_preliminary(self):
        # Stator parameters
        NbDemiEncoche = self.parameters['NbDemiEncoche'].value
        SNShunt = self.parameters['SNShunt'].value
        SRatioLongueurActive = self.parameters['SRatioLongueurActive'].value
        k_w = self.parameters['k_w'].value
        
        # Rotor parameters 
        AngleSommetMinMaillage = self.rotor.parameters['AngleSommetMinMaillage'].value
        Precision = self.rotor.parameters['Precision'].value
        J_den = self.rotor.parameters['J_den'].value
        TempAimant = self.rotor.parameters['TempAimant'].value
        K = self.rotor.parameters['K'].value
        TailleMailleEntrefer = self.rotor.parameters['TailleMailleEntrefer'].value*K
        TailleMailleBobine = self.rotor.parameters['TailleMailleBobine'].value*K
        SEt = self.rotor.parameters['SEt'].value*K
        
        SPx = self.SPx
        SPy = self.SPy
        SE1x = self.SE1x
        SE1y = self.SE1y
        SE2x = self.SE2x
        SE2y = self.SE2y
        SF1x = self.SF1x
        SF1y = self.SF1y
        SF2x = self.SF2x
        SF2y = self.SF2y
        SGx = self.SGx
        SGy = self.SGy
        SUx = self.SUx
        SUy = self.SUy
        SMx = self.SMx
        SMy = self.SMy
        SZx = self.SZx
        SZy = self.SZy
        SWx = self.SWx
        SWy = self.SWy
        SAngL1pOEo = self.SAngL1pOEo
        SAngE1EoE2 = self.SAngE1EoE2
        SAngF1FoF2 = self.SAngF1FoF2
        SPE1x = self.SPE1x
        SPE1y = self.SPE1y
        SE1E2x = self.SE1E2x
        SE1E2y = self.SE1E2y
        SF1F2x = self.SF1F2x
        SF1F2y = self.SF1F2y
        MaxSegDegOG = self.MaxSegDegOG

        
        
        """ CALCUL of the windings surface (Nomex compris : "half_solt.fem" """
        self.femm_wrapper.openfemm(1)
        self.femm_wrapper.newdocument(0)						# probléme en magnétique
        self.femm_wrapper.probdef(0,'millimeters','planar',Precision,SEt,AngleSommetMinMaillage)
         					# Précision between 1e-008 and 1e-016
        					# thickness 110mm to adjust
        					# Minimum vertex angle of the elements between 1° and 33.8°
        
        """ AIR """
        Mu_x = 1
        Mu_y = 1
        H_c = 0
        J = 0
        Cduct = 0
        Lam_d = 0
        Phi_max = 0
        Lam_fill = 1
        Lam_type = 0 		# (0 :laminated in plane ; 3 : magnet wire)
        Phi_hx = 0
        Phi_hy =0
        self.femm_wrapper.addmaterial('air',Mu_x,Mu_y ,H_c,J,Cduct,Lam_d,Phi_max,Lam_fill,Lam_type,Phi_hx,Phi_hy)								
        
        """ Surface building """
        self.femm_wrapper.addnode(SPx,SPy)
        self.femm_wrapper.addnode(SE1x,SE1y)
        self.femm_wrapper.addnode(SE2x,SE2y)
        self.femm_wrapper.addnode(SF1x,SF1y)
        self.femm_wrapper.addnode(SF2x,SF2y)
        self.femm_wrapper.addnode(SGx,SGy)
        self.femm_wrapper.addnode(SUx,SUy)
#              self.femm_wrapper.addnode(SZx,SZy)
#              self.femm_wrapper.addnode(SWx,SWy)
        
        self.femm_wrapper.addsegment(SE2x,SE2y,SF1x,SF1y)
        self.femm_wrapper.addsegment(SF2x,SF2y,SGx,SGy)
        self.femm_wrapper.addsegment(SGx,SGy,SUx,SUy)
        self.femm_wrapper.addsegment(SUx,SUy,SPx,SPy)
        self.femm_wrapper.addsegment(SMx,SMy,SZx,SZy)
        self.femm_wrapper.addsegment(SPx,SPy,SWx,SWy)
        
        self.femm_wrapper.addarc(SPx,SPy,SE1x,SE1y,SAngL1pOEo/2*180/pi,1)
        self.femm_wrapper.addarc(SE1x,SE1y,SE2x,SE2y,SAngE1EoE2*180/pi,1)
        self.femm_wrapper.addarc(SF1x,SF1y,SF2x,SF2y,SAngF1FoF2*180/pi,1)
        
        self.femm_wrapper.selectnode(SPx,SPy)
        self.femm_wrapper.selectnode(SE1x,SE1y)
        self.femm_wrapper.selectnode(SE2x,SE2y)
        self.femm_wrapper.selectnode(SF1x,SF1y)
        self.femm_wrapper.selectnode(SF2x,SF2y)
        self.femm_wrapper.selectnode(SGx,SGy)
        self.femm_wrapper.selectnode(SUx,SUy)
        self.femm_wrapper.selectnode(SZx,SZy)
        self.femm_wrapper.selectnode(SWx,SWy)
        self.femm_wrapper.setnodeprop('TOTALE',200)
        self.femm_wrapper.clearselected()
        		
        self.femm_wrapper.selectsegment((SE2x+SF1x)/2,(SE2y+SF1y)/2)
        self.femm_wrapper.selectsegment((SF2x+SGx)/2,(SF2y+SGy)/2)
        self.femm_wrapper.selectsegment((SGx+SUx)/2,(SGy+SUy)/2)
        self.femm_wrapper.selectsegment((SUx+SPx)/2,(SUy+SPy)/2)
        self.femm_wrapper.selectsegment((SZx+SMx)/2,(SZy+SMy)/2)
        self.femm_wrapper.selectsegment((SWx+SPx)/2,(SWy+SPy)/2)
        self.femm_wrapper.setsegmentprop('TOTALE',TailleMailleBobine,1,0,200)			
        self.femm_wrapper.clearselected()
        
        self.femm_wrapper.selectarcsegment(SPE1x,SPE1y)
        self.femm_wrapper.selectarcsegment(SE1E2x,SE1E2y)
        self.femm_wrapper.selectarcsegment(SF1F2x,SF1F2y)
        self.femm_wrapper.setarcsegmentprop(MaxSegDegOG,'TOTALE',0,200) 
        self.femm_wrapper.clearselected()
        
        self.femm_wrapper.addblocklabel((SPx+SF2x)/2,(SPy+SF2y)/2);
        self.femm_wrapper.selectlabel((SPx+SF2x)/2,(SPy+SF2y)/2);
        self.femm_wrapper.setblockprop('air',0,TailleMailleEntrefer,0,0,200,1);
        self.femm_wrapper.clearselected()
        
        self.femm_wrapper.zoomnatural
        self.femm_wrapper.saveas('Half_solt.fem')
        self.femm_wrapper.analyze(0)
        self.femm_wrapper.loadsolution()
        self.femm_wrapper.smooth('on')
        self.femm_wrapper.groupselectblock(200)
        SEdemi_totale = self.femm_wrapper.blockintegral(5)*1e6
        # SE_slot = SEdemi_totale*2
        self.SE_totale= SEdemi_totale*2
        if (NbDemiEncoche==0):
            self.femm_wrapper.selectsegment((SUx+SPx)/2,(SUy+SPy)/2)
            self.femm_wrapper.deleteselectedsegments   			
            self.femm_wrapper.clearselected()
      
        self.femm_wrapper.purgemesh
        
        ### (Aurélien) à modifier dans le fichier motor plutot
        
        # New FEMM document
        self.femm_wrapper.newdocument(0)						# Magnetic problem
        self.femm_wrapper.probdef(0,'millimeters','planar',Precision,SEt,AngleSommetMinMaillage)
 					# Précision between 1e-008 and 1e-016
        from materials import Material
        k_w = self.parameters['k_w'].value
        Material.add_materials(J_den=J_den, SRatioLongueurActive=SRatioLongueurActive, k_w=k_w, TempAimant=TempAimant, SNShunt=SNShunt)
                        
        
    def draw(self):
        # motor parameter
        repetition = self.repetition
        
        # Rotor parameters
        Np = self.rotor.parameters['Np'].value
        K = self.rotor.parameters['K'].value
        if self.rotor_type == 'IPM':
            e = self.rotor.parameters['e'].value*K
        else:
            ALo = self.rotor.parameters['ALo'].value*K
            self.rotor.parameters['e'].value = ALo+1.2*K
            e = self.rotor.parameters['e'].value
        SRfe = self.parameters['SRfe'].value
        SRi = self.rotor.parameters['SRi'].value*K
        RRe = self.rotor.parameters['RRe'].value
        SRe = self.rotor.parameters['SRe'].value
        ALa = self.rotor.parameters['ALa'].value/repetition

        # Stator parameters      
        NbDemiEncoche = self.parameters['NbDemiEncoche'].value
        ACwind = self.parameters['ACwind'].value
        SAngDepEncoche = self.parameters['SAngDepEncoche'].value
        KNe = self.parameters['KNe'].value
        SENomex = self.parameters['SENomex'].value
        SRiNomex = self.parameters['SRiNomex'].value/KNe*K
        Ne = int(self.motif.split('/')[1])
        self.parameters['Ne'].value = Ne
        
        
        
        TailleMailleEntrefer = self.rotor.parameters['TailleMailleEntrefer'].value    
        TailleMailleBobine = self.rotor.parameters['TailleMailleBobine'].value*K
        TailleMaille = self.rotor.parameters['TailleMaille'].value*K
        ACwind = self.parameters['ACwind'].value
        
        if self.rotor_type == 'IPM':
            self.parameters['SEp'].value = 2.62
            SEp = self.parameters['SEp'].value*K
            self.parameters['SLd'].value = 4.48 
            SLd = self.parameters['SLd'].value*K/KNe
            self.parameters['SLa'].value = 2.35
            SLa = self.parameters['SLa'].value*K/KNe
            self.parameters['SLo'].value = 0.6
            SLo = self.parameters['SLo'].value*K/KNe
            
        elif self.rotor_type == 'SPM' or 'Halbach':
            self.parameters['SEp'].value = 3.17
            SEp = self.parameters['SEp'].value*K
            self.parameters['SLd'].value = 6.83 
            SLd = self.parameters['SLd'].value*K
            self.parameters['SLa'].value = 5.84
            SLa = self.parameters['SLa'].value*K
            self.parameters['SLo'].value = 1.49 
            SLo = self.parameters['SLo'].value*K
        
        
        """ Notch's node coordinates """
        SAngElec = self.SAngElec/repetition
        
        SPx = SRfe*sin(SAngElec/2) 
        SPy = SRfe*cos(SAngElec/2) 
        
        SReNomex = (SRiNomex+SENomex)/repetition
        
        SEox = SLd/2+SReNomex*repetition
        SEoy = ((SRfe-SReNomex)**2-SEox**2)**.5

        SAngEoOY = asin(SEox/(SRfe-SReNomex))

        SE1x = SRfe*sin(SAngEoOY/repetition) 
        SE1y = SRfe*cos(SAngEoOY/repetition) 
        
        SE2x = SLd/(2*repetition) 
        SE2y = SEoy 
        
        SAngVOH = asin(SLa/(2*repetition)/SRi)*2
        
        SHx = SRi*(sin(SAngElec/2-SAngVOH/(2*repetition)))
        SHy = SRi*(cos(SAngElec/2-SAngVOH/(2*repetition))) 
        
        SGx = SHx+SLo*sin(SAngElec/2-SAngVOH/(2*repetition)) 
        SGy = SHy+SLo*cos(SAngElec/2-SAngVOH/(2*repetition))
        
        SFx = SLd/(2*repetition)
        SFy = SGy+(SGx-SFx)*tan(SAngDepEncoche+SAngElec/2)
        
        SAngYFG = pi/2+SAngDepEncoche+SAngElec/2
        
        SFox = SLd/(2*repetition)+SReNomex
        SFoy = SFy+SReNomex/tan(SAngYFG/2)
        
        SF1x = SLd/(2*repetition)
        SF1y = SFoy
        
        SF2x = SFox+SReNomex*cos(-(SAngDepEncoche+SAngElec/2)-pi/2)
        SF2y = SF1y+SReNomex*sin(-(SAngDepEncoche+SAngElec/2)-pi/2) 
        
        SJx = -SGx
        SJy = SGy
        
        SNx = -(SJx**2+SJy**2)**.5*sin(SAngElec/2)
        SNy = (SJx**2+SJy**2)**.5*cos(SAngElec/2)

        SUx = -SNx
        SUy = SNy
        
        SMx = -SRfe*sin(SAngElec/2)
        SMy = SRfe*cos(SAngElec/2)
        
        SZx = -(SRe)*sin(SAngElec/2)
        SZy = (SRe)*cos(SAngElec/2) 
        
        SWx = -SZx
        SWy = SZy 
        
        SAngL1pOEo = SAngElec-SAngEoOY*2/repetition 
        SAngE1EoE2 = pi/2+SAngEoOY/repetition 
        SAngF1FoF2 = (pi/2-SAngYFG/2)*2 
        
        SPE1x = SRfe*sin((SAngElec/2+SAngEoOY/repetition)/2) 
        SPE1y = SRfe*cos((SAngElec/2+SAngEoOY/repetition)/2)
        
        SE1E2x = SEox+SReNomex*cos(pi/2-SAngElec/2+SAngE1EoE2/2)
        SE1E2y = SEoy+SReNomex*sin(pi/2-SAngElec/2+SAngE1EoE2/2)
                
        SF1F2x = SFox+SReNomex*cos(pi+SAngF1FoF2/2)
        SF1F2y = SF1y+SReNomex*sin(pi+SAngF1FoF2/2)
        
        SIx = -SHx
        SIy = SHy
        
        SK1x = -SF1x
        SK1y = SF1y
        
        SK2x = -SF2x
        SK2y = SF2y
        
        SL1x = -SE1x
        SL1y = SE1y
        
        SL2x = -SE2x 
        SL2y = SE2y 
                
        SL1Mx = -SPE1x 
        SL1My = SPE1y 
        
        SIJx = self.SIJx
        SIJy = self.SIJy
        
        SL1L2x = -SE1E2x 
        SL1L2y = SE1E2y 
        
        SK1K2x = -SF1F2x 
        SK1K2y = SF1F2y 
        
        SRx = 0
        SRy = SRe
                
        SAngHOI = SAngElec-SAngVOH/repetition 
        NbDemiEncoche = self.parameters['NbDemiEncoche'].value
        MaxSegDegPE1 = self.MaxSegDegPE1
        MaxSegDegE1E2 = self.MaxSegDegE1E2

        """ Definition of the Winding structure (A verifier:https://www.emetor.com/edit/windings) """
        BPeriodeBob=Ne
        if (Np == 10) | (Np== 4):
            if (ACwind==1):
                BNomBob=["A","B","C","A","B","C","A","B","C","A","B","C"] 
                BSigneBob=np.array([1,-1,1,-1,1,-1,1,-1,1,-1,1,-1])       
            elif (NbDemiEncoche==0):
                BNomBob=['A','A','B','B','C','C','A','A','B','B','C','C']            
                BSigneBob=np.array([1,-1,-1,1,1,-1,-1,1,1,-1,-1,1])
            elif (NbDemiEncoche==2):
                BNomBob=['A','A','A','A','B','B','B','B','C','C','C','C','A','A','A','A','B','B','B','B','C','C','C','C']
                BSigneBob=np.array([1,-1,-1,1,-1,1,1,-1,1,-1,-1,1,-1,1,1,-1,1,-1,-1,1,-1,1,1,-1])
        if (Np == 14):
            if (ACwind==1):
                BNomBob=['A','B','C','A','B','C','A','B','C','A','B','C']
                BSigneBob=np.array([1,-1,1,-1,1,-1,1,-1,1,-1,1,-1])
            elif (NbDemiEncoche==0):
                BNomBob=['A','A','C','C','B','B','A','A','C','C','B','B']            
                BSigneBob= np.array([1,-1,-1,1,1,-1,-1,1,1,-1,-1,1]) 
            elif (NbDemiEncoche==2):
                BNomBob=['A','A','A','A','B','B','B','B','C','C','C','C','A','A','A','A','B','B','B','B','C','C','C','C']
                BSigneBob=np.array([1,-1,-1,1,-1,1,1,-1,1,-1,-1,1,-1,1,1,-1,1,-1,-1,1,-1,1,1,-1])
        if (Np == 16):
            if (ACwind==1):
                pass
            elif (NbDemiEncoche==0):
                BNomBob = ['A','A','B','B','B','B','C','C','A','A','A','A','B','B','C','C','C','C']
                BSigneBob=np.array([1,-1,-1,1,-1,1,1,-1,-1,1,-1,1,1,-1,-1,1,-1,1])
            elif (NbDemiEncoche==2):
                BNomBob = ['A','A','A','B','B','B','B','B','B','C','C','C','C','C','C','A','A','A','A','A','A','B','B','B','B','B','B','C','C','C','C','C','C','A','A','A']
                BSigneBob=np.array([-1,-1,1,-1,1,1,-1,-1,1,-1,1,1,-1,-1,1,-1,1,1,-1,-1,1,-1,1,1,-1,-1,1,-1,1,1,-1,-1,1,-1,1,1])
        if (Np == 20):
            if (ACwind==1):
                pass
            elif (NbDemiEncoche==0):
                BNomBob=['A','A','B','B','C','C','A','A','B','B','C','C','A','A','B','B','C','C','A','A','B','B','C','C']            
                BSigneBob=np.array([1,-1,-1,1,1,-1,-1,1,1,-1,-1,1,1,-1,-1,1,1,-1,-1,1,1,-1,-1,1])
            elif (NbDemiEncoche==2):
                BNomBob=['A','A','A','A','B','B','B','B','C','C','C','C','A','A','A','A','B','B','B','B','C','C','C','C']
                BSigneBob=np.array([1,-1,-1,1,-1,1,1,-1,1,-1,-1,1,-1,1,1,-1,1,-1,-1,1,-1,1,1,-1])
        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
                                 STATOR MODELISATION """

        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                          Draw sheet package
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
                    	
        """ Draw Slot """
        Anglep=0-2*pi/Ne;
        SPxrot=SMx*cos(Anglep)-SMy*sin(Anglep);
        SPyrot=SMx*sin(Anglep)+SMy*cos(Anglep);
        self.femm_wrapper.addnode(SPxrot,SPyrot);
        self.femm_wrapper.selectnode(SPxrot,SPyrot);	
        self.femm_wrapper.setnodeprop('TOLE',2);
        self.femm_wrapper.clearselected()
        	
        for AngleDeg in np.arange (0,(360+Ne)/repetition,360/(repetition*Ne)):
            Angle=AngleDeg*pi/180
            S=sin(Angle)
            C=cos(Angle)
            SE1xrot=SE1x*C-SE1y*S
            SE1yrot=SE1x*S+SE1y*C
            SE2xrot=SE2x*C-SE2y*S
            SE2yrot=SE2x*S+SE2y*C		
            SF1xrot=SF1x*C-SF1y*S
            SF1yrot=SF1x*S+SF1y*C
            SF2xrot=SF2x*C-SF2y*S
            SF2yrot=SF2x*S+SF2y*C		
            SGxrot=SGx*C-SGy*S
            SGyrot=SGx*S+SGy*C
            SHxrot=SHx*C-SHy*S
            SHyrot=SHx*S+SHy*C
            SIxrot=SIx*C-SIy*S
            SIyrot=SIx*S+SIy*C
            SJxrot=SJx*C-SJy*S
            SJyrot=SJx*S+SJy*C		
            SK1xrot=SK1x*C-SK1y*S
            SK1yrot=SK1x*S+SK1y*C
            SK2xrot=SK2x*C-SK2y*S
            SK2yrot=SK2x*S+SK2y*C		
            SL1xrot=SL1x*C-SL1y*S
            SL1yrot=SL1x*S+SL1y*C
            SL2xrot=SL2x*C-SL2y*S
            SL2yrot=SL2x*S+SL2y*C		
            SMxrot=SMx*C-SMy*S
            SMyrot=SMx*S+SMy*C
            SNxrot=SNx*C-SNy*S
            SNyrot=SNx*S+SNy*C	   
            SUxrot=SUx*C-SUy*S
            SUyrot=SUx*S+SUy*C          
            SPE1xrot=SPE1x*C-SPE1y*S
            SPE1yrot=SPE1x*S+SPE1y*C
            SL1Mxrot=SL1Mx*C-SL1My*S
            SL1Myrot=SL1Mx*S+SL1My*C
            SIJxrot=SIJx*C-SIJy*S
            SIJyrot=SIJx*S+SIJy*C	
            SE1E2xrot=SE1E2x*C-SE1E2y*S
            SE1E2yrot=SE1E2x*S+SE1E2y*C
            SF1F2xrot=SF1F2x*C-SF1F2y*S
            SF1F2yrot=SF1F2x*S+SF1F2y*C
            SL1L2xrot=SL1L2x*C-SL1L2y*S
            SL1L2yrot=SL1L2x*S+SL1L2y*C
            SK1K2xrot=SK1K2x*C-SK1K2y*S
            SK1K2yrot=SK1K2x*S+SK1K2y*C
            SRxrot = SRx*C-SRy*S
            SRyrot = SRx*S+SRy*C
            
            self.femm_wrapper.addnode(SE1xrot,SE1yrot)
            self.femm_wrapper.addnode(SE2xrot,SE2yrot)
            self.femm_wrapper.addnode(SF1xrot,SF1yrot)
            self.femm_wrapper.addnode(SF2xrot,SF2yrot)
            self.femm_wrapper.addnode(SGxrot,SGyrot)
            self.femm_wrapper.addnode(SHxrot,SHyrot)
            self.femm_wrapper.addnode(SIxrot,SIyrot)
            self.femm_wrapper.addnode(SJxrot,SJyrot)
            self.femm_wrapper.addnode(SK1xrot,SK1yrot)
            self.femm_wrapper.addnode(SK2xrot,SK2yrot)			
            self.femm_wrapper.addnode(SL1xrot,SL1yrot)
            self.femm_wrapper.addnode(SL2xrot,SL2yrot)
            self.femm_wrapper.addnode(SMxrot,SMyrot)
            self.femm_wrapper.addnode(SNxrot,SNyrot)
            self.femm_wrapper.addnode(SUxrot,SUyrot)
            
            self.femm_wrapper.addsegment(SE2xrot,SE2yrot,SF1xrot,SF1yrot)
            self.femm_wrapper.addsegment(SF2xrot,SF2yrot,SGxrot,SGyrot)
            self.femm_wrapper.addsegment(SGxrot,SGyrot,SHxrot,SHyrot)
            self.femm_wrapper.addsegment(SIxrot,SIyrot,SJxrot,SJyrot)
            self.femm_wrapper.addsegment(SJxrot,SJyrot,SK2xrot,SK2yrot)
            self.femm_wrapper.addsegment(SK1xrot,SK1yrot,SL2xrot,SL2yrot)
           		
            self.femm_wrapper.addarc(SPxrot,SPyrot,SE1xrot,SE1yrot,SAngL1pOEo/2*180/pi,1)
            self.femm_wrapper.addarc(SE1xrot,SE1yrot,SE2xrot,SE2yrot,SAngE1EoE2*180/pi,1)
            self.femm_wrapper.addarc(SF1xrot,SF1yrot,SF2xrot,SF2yrot,SAngF1FoF2*180/pi,1)
            self.femm_wrapper.addarc(SHxrot,SHyrot,SIxrot,SIyrot,SAngHOI*180/pi,1)
            self.femm_wrapper.addarc(SL1xrot,SL1yrot,SMxrot,SMyrot,SAngL1pOEo/2*180/pi,1)
            self.femm_wrapper.addarc(SL2xrot,SL2yrot,SL1xrot,SL1yrot,SAngE1EoE2*180/pi,1)
            self.femm_wrapper.addarc(SK2xrot,SK2yrot,SK1xrot,SK1yrot,SAngF1FoF2*180/pi,1)
            self.femm_wrapper.addarc(SJxrot,SJyrot,SNxrot,SNyrot,SAngL1pOEo/2*180/pi,1)
            self.femm_wrapper.addarc(SGxrot,SGyrot,SUxrot,SUyrot,SAngL1pOEo/2*180/pi,1)
        		
            self.femm_wrapper.selectnode(SE1xrot,SE1yrot)
            self.femm_wrapper.selectnode(SE2xrot,SE2yrot)
            self.femm_wrapper.selectnode(SF1xrot,SF1yrot)
            self.femm_wrapper.selectnode(SF2xrot,SF2yrot)
            self.femm_wrapper.selectnode(SGxrot,SGyrot)
            self.femm_wrapper.selectnode(SHxrot,SHyrot)
            self.femm_wrapper.selectnode(SIxrot,SIyrot)
            self.femm_wrapper.selectnode(SJxrot,SJyrot)
            self.femm_wrapper.selectnode(SK1xrot,SK1yrot)
            self.femm_wrapper.selectnode(SK2xrot,SK2yrot)
            self.femm_wrapper.selectnode(SL1xrot,SL1yrot)
            self.femm_wrapper.selectnode(SL2xrot,SL2yrot)
            self.femm_wrapper.selectnode(SMxrot,SMyrot)
            self.femm_wrapper.selectnode(SNxrot,SNyrot)
            self.femm_wrapper.selectnode(SUxrot,SUyrot)
            self.femm_wrapper.setnodeprop('TOLE',6)
            self.femm_wrapper.clearselected()
           		
            self.femm_wrapper.selectsegment((SE2xrot+SF1xrot)/2,(SE2yrot+SF1yrot)/2)
            self.femm_wrapper.selectsegment((SF2xrot+SGxrot)/2,(SF2yrot+SGyrot)/2)
            self.femm_wrapper.selectsegment((SJxrot+SK2xrot)/2,(SJyrot+SK2yrot)/2)
            self.femm_wrapper.selectsegment((SK1xrot+SL2xrot)/2,(SK1yrot+SL2yrot)/2)
            self.femm_wrapper.setsegmentprop('TOLE',TailleMaille,1,0,6)
            self.femm_wrapper.clearselected()
        		
            self.femm_wrapper.selectsegment((SGxrot+SHxrot)/2,(SGyrot+SHyrot)/2)
            self.femm_wrapper.selectsegment((SIxrot+SJxrot)/2,(SIyrot+SJyrot)/2)
            self.femm_wrapper.setsegmentprop('TOLE',TailleMailleEntrefer,1,0,6)
            self.femm_wrapper.clearselected()
        		
            self.femm_wrapper.selectarcsegment(SPE1xrot,SPE1yrot)
            self.femm_wrapper.selectarcsegment(SL1Mxrot,SL1Myrot)
            self.femm_wrapper.setarcsegmentprop(MaxSegDegPE1,'TOLE',0,6)
            self.femm_wrapper.clearselected()
                
            self.femm_wrapper.selectarcsegment(SE1E2xrot,SE1E2yrot)
            self.femm_wrapper.selectarcsegment(SF1F2xrot,SF1F2yrot)
            self.femm_wrapper.selectarcsegment(SL1L2xrot,SL1L2yrot)
            self.femm_wrapper.selectarcsegment(SK1K2xrot,SK1K2yrot)
            self.femm_wrapper.setarcsegmentprop(MaxSegDegE1E2,'TOLE',0,6) 
            self.femm_wrapper.clearselected()
        		
            self.femm_wrapper.selectarcsegment(SIJxrot,SIJyrot)
            MaxSegDeg=2*asin(TailleMailleEntrefer/2/SRi)*180/pi
            self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'TOLE',0,6)
            self.femm_wrapper.clearselected()
        		
            SPxrot=SMxrot
            SPyrot=SMyrot
        
        self.femm_wrapper.addnode(SWx,SWy)
        self.femm_wrapper.addnode(SZx,SZy)
        self.femm_wrapper.addsegment(SMx,SMy,SZx,SZy)
        self.femm_wrapper.addsegment(SPx,SPy,SWx,SWy)
        self.femm_wrapper.addsegment(SL2x,SL2y,SE2x,SE2y)
                 
        self.femm_wrapper.addblocklabel((SMx/2)*cos(SAngElec/(5*repetition))-((SL1y+SRe)/2)*sin(SAngElec/(5*repetition)),(SMx/2)*sin(SAngElec/(5*repetition))+((SL1y+SRe)/2)*cos(SAngElec/(5*repetition)))
        self.femm_wrapper.selectlabel((SMx/2)*cos(SAngElec/(5*repetition))-((SL1y+SRe)/2)*sin(SAngElec/(5*repetition)),(SMx/2)*sin(SAngElec/(5*repetition))+((SL1y+SRe)/2)*cos(SAngElec/(5*repetition)))
        MatiereTole='FeSi 0.35mm'
        self.femm_wrapper.setblockprop(MatiereTole,0,TailleMaille,0,0,4,1)
        self.femm_wrapper.clearselected()
            
        self.femm_wrapper.addblocklabel((2*SK1x+SF1x)/2,(SL2y+SK1y)/2)
        self.femm_wrapper.selectlabel((2*SK1x+SF1x)/2,(SL2y+SK1y)/2)
        MatiereTole='FeSi 0.35mm'
        self.femm_wrapper.setblockprop(MatiereTole,0,TailleMaille,0,0,5,1)
        self.femm_wrapper.clearselected()
        
        self.femm_wrapper.addblocklabel(-(SRe-TailleMaille)*sin(Angle/2),(SRe-TailleMaille)*cos(Angle/2))
        self.femm_wrapper.selectlabel(-(SRe-TailleMaille)*sin(Angle/2),(SRe-TailleMaille)*cos(Angle/2))
        self.femm_wrapper.MatiereTole='FeSi 0.35mm'
        self.femm_wrapper.setblockprop(MatiereTole,0,TailleMaille,0,0,6,1)
        self.femm_wrapper.clearselected()
        
                   
        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                          Draw simple winding 
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
            
        """ COIL PHASE 1 """ 
        
        Anglep=0-2*pi/Ne
        SUxrot=SNx*cos(Anglep)-SNy*sin(Anglep)
        SUyrot=SNx*sin(Anglep)+SNy*cos(Anglep)
        SPxrot=SMx*cos(Anglep)-SMy*sin(Anglep)
        SPyrot=SMx*sin(Anglep)+SMy*cos(Anglep)
        
        SEox = SLd/2+SReNomex*repetition
        SEoy = ((SRfe-SReNomex)**2-SEox**2)**.5

        Range = Ne
        if (NbDemiEncoche==0):
            for jjNe in range (Range):
                Angle1=2*pi/(Ne*repetition)*(jjNe)
                S=sin(Angle1)
                C=cos(Angle1)
                SPxrot=SPx*C-SPy*S
                SPyrot=SPx*S+SPy*C
                SUxrot=SUx*C-SUy*S
                SUyrot=SUx*S+SUy*C  
                
                self.femm_wrapper.addblocklabel(((SF2x+SE1x)/2)*C-((SF1y+SE1y)/2)*S,((SF2x+SE1x)/2)*S+((SF1y+SE1y)/2)*C)
                self.femm_wrapper.selectlabel(((SF2x+SE1x)/2)*C-((SF1y+SE1y)/2)*S,((SF2x+SE1x)/2)*S+((SF1y+SE1y)/2)*C)
        
                Sens=BSigneBob[jjNe]
                Phase=BNomBob[jjNe]
                
                if (Phase=='A'):
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('A+',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('A-',0,TailleMaille,0,0,7,1)       
                if(Phase=='B'):
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('B+',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('B-',0,TailleMaille,0,0,7,1)
                if (Phase=='C'):
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('C+',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('C-',0,TailleMaille,0,0,7,1)
                self.femm_wrapper.clearselected()
            if repetition>1:
                self.femm_wrapper.addblocklabel(((SK2x+SL1x)/2)*C-((SK1y+SL1y)/2)*S,((SK2x+SL1x)/2)*S+((SK1y+SL1y)/2)*C)
                self.femm_wrapper.selectlabel(((SK2x+SL1x)/2)*C-((SK1y+SL1y)/2)*S,((SK2x+SL1x)/2)*S+((SK1y+SL1y)/2)*C)
                self.femm_wrapper.setblockprop('A+',0,TailleMaille,0,0,7,1)
 
        """         ------------------------------------------------------- """
        if (NbDemiEncoche==2):
            jjBper=1    
            for jjNe in range (Ne):
                Angle1=2*pi/(Ne*repetition)*(jjNe)
                jjPer=(jjNe-1)%BPeriodeBob+1
                jjBob1=2*(jjPer-1)+1
                jjBob2=2*(jjPer-1)+2
                    
                S=sin(Angle1)
                C=cos(Angle1)
                    
                SPxrot=SPx*C-SPy*S
                SPyrot=SPx*S+SPy*C
                    
                SUxrot=SUx*C-SUy*S
                SUyrot=SUx*S+SUy*C
                    
                SF2xrot=SF2x*C-SF2y*S
                SF2yrot=SF2x*S+SF2y*C
                    
                SK2xrot=SK2x*C-SK2y*S
                SK2yrot=SK2x*S+SK2y*C
                    
                SMxrot=SMx*C-SMy*S
                SMyrot=SMx*S+SMy*C
                    
                SNxrot=SNx*C-SNy*S
                SNyrot=SNx*S+SNy*C
                    
        #       Half coil on the right side of the tooth
                
                self.femm_wrapper.addsegment(SUxrot,SUyrot,SPxrot,SPyrot)
                self.femm_wrapper.selectsegment((SUxrot+SPxrot)/2,(SUyrot+SPyrot)/2)
                self.femm_wrapper.setsegmentprop('BOBINE',TailleMailleBobine,1,0,7)
                self.femm_wrapper.clearselected()
                    
                self.femm_wrapper.addblocklabel((SPxrot+SF2xrot)/2,(SPyrot+SF2yrot)/2)
                self.femm_wrapper.selectlabel((SPxrot+SF2xrot)/2,(SPyrot+SF2yrot)/2)
                    
                Sens=BSigneBob[jjBper]
                Phase=BNomBob[jjBper]
                      
                if  (Phase=='A'):
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('A+',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('A-',0,TailleMaille,0,0,7,1)                          
                    if (Phase=='B'):
                        if (Sens==1):
                            self.femm_wrapper.setblockprop('B+',0,TailleMaille,0,0,7,1)
                        else:
                            self.femm_wrapper.setblockprop('B-',0,TailleMaille,0,0,7,1)           
                    if (Phase=='C'): 
                        if (Sens==1):
                            self.femm_wrapper.setblockprop('C+',0,TailleMaille,0,0,7,1)
                        else:
                            self.femm_wrapper.setblockprop('C-',0,TailleMaille,0,0,7,1)
            
        #       Half coil on the left side of the tooth """
                self.femm_wrapper.addsegment(SMxrot,SMyrot,SNxrot,SNyrot)
                self.femm_wrapper.selectsegment((SMxrot+SNxrot)/2,(SMyrot+SNyrot)/2)
                self.femm_wrapper.setsegmentprop('BOBINE',TailleMailleBobine,1,0,7)
                self.femm_wrapper.clearselected()
                    
                self.femm_wrapper.addblocklabel((SMxrot+SK2xrot)/2,(SMyrot+SK2yrot)/2)
                self.femm_wrapper.selectlabel((SMxrot+SK2xrot)/2,(SMyrot+SK2yrot)/2)
                Sens=BSigneBob(1,jjBper+1)
                Phase=BNomBob(1,jjBper+1)
                
                if (Phase=='A'):
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('A+',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('A-',0,TailleMaille,0,0,7,1)
                if (Phase=='B'):
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('B+',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('B-',0,TailleMaille,0,0,7,1)
                if (Phase=='C'): 
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('C+',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('C-',0,TailleMaille,0,0,7,1)
                
                self.femm_wrapper.addblocklabel((SMxrot+SNxrot)/2,(SMyrot+SNyrot)/2)
                self.femm_wrapper.selectlabel((SMxrot+SNxrot)/2,(SMyrot+SNyrot)/2)
        
                Sens=BSigneBob[jjBper+1]
                Phase=BNomBob[jjBper+1]
                if (Phase=='A'):
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('MatiereCuivre_pA',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('MatiereCuivre_nA',0,TailleMaille,0,0,7,1)
                if (Phase=='B'):
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('MatiereCuivre_pB',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('MatiereCuivre_nB',0,TailleMaille,0,0,7,1)
                if (Phase=='C'): 
                    if (Sens==1):
                        self.femm_wrapper.setblockprop('MatiereCuivre_pC',0,TailleMaille,0,0,7,1)
                    else:
                        self.femm_wrapper.setblockprop('MatiereCuivre_nC',0,TailleMaille,0,0,7,1)
        
                jjBper=jjBper+2
        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """        
        
        self.femm_wrapper.selectgroup(3)
        self.femm_wrapper.selectgroup(9)
        self.femm_wrapper.moverotate(0,0,0)
        
        
        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                          Draw Air gap
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
            
        """ AIR GAP : sheet construction """
        if self.rotor_type == 'IPM':
                
            self.femm_wrapper.addnode(SZx,SZy)
            self.femm_wrapper.addnode(SWx,SWy)
            
                
            self.femm_wrapper.selectnode(0,SRe)		
            self.femm_wrapper.selectnode(0,-SRe)
            self.femm_wrapper.setnodeprop('TOLE',2)
            self.femm_wrapper.clearselected()
               	
            self.femm_wrapper.selectarcsegment(SRe,0)
            self.femm_wrapper.selectarcsegment(-SRe,0)
            MaxSegDeg=2*asin(TailleMaille/2/SRe)*180/pi
            self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'TOLE',0,2)  			
            self.femm_wrapper.clearselected()
            
            ARe = self.rotor.parameters['ARe'].value   
            IndEntreferMax=floor((SRi-ARe)/TailleMailleEntrefer)
            IndEntreferMax=3
            for IndREntrefer in range (1,IndEntreferMax+1):
                REntrefer=RRe+(SRi-RRe)/IndEntreferMax*IndREntrefer
                MaxSegDeg=TailleMailleEntrefer/REntrefer*360
                SEntreferxcoupe=-(REntrefer)*sin(Angle)
                SEntreferycoupe=(REntrefer)*cos(Angle)
                if (REntrefer == SRi):
                    self.femm_wrapper.addblocklabel((2*SK1x+SF1x)/2,REntrefer-TailleMailleEntrefer/2)      # tailleMailleEntrefer à changer si probl�me de d�finition mat�riau
                    self.femm_wrapper.selectlabel((2*SK1x+SF1x)/2,REntrefer-TailleMailleEntrefer/2)
                    self.femm_wrapper.setblockprop('air',0,e/4,0,0,2,1)
                    self.femm_wrapper.clearselected()
                else:
                    if repetition>1:
                        self.femm_wrapper.addnode(0,REntrefer)
                        self.femm_wrapper.addnode(SEntreferxcoupe,SEntreferycoupe)
                        self.femm_wrapper.addarc(0,REntrefer,SEntreferxcoupe,SEntreferycoupe,360/repetition,1)
                    
                        self.femm_wrapper.selectnode(0,REntrefer)
                        self.femm_wrapper.selectnode(SEntreferxcoupe,SEntreferycoupe)
                        self.femm_wrapper.setnodeprop('ENTREFER',2)
                        self.femm_wrapper.clearselected()
                			
                        self.femm_wrapper.selectarcsegment(0,-REntrefer)
                        self.femm_wrapper.selectarcsegment(0,REntrefer)
                        self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'ENTREFER',0,2)
                        self.femm_wrapper.clearselected()
                        self.femm_wrapper.addblocklabel((2*SK1x+SF1x)/2,REntrefer-TailleMailleEntrefer/2)
                        self.femm_wrapper.selectlabel((2*SK1x+SF1x)/2,REntrefer-TailleMailleEntrefer/2)
                    else :
                        self.femm_wrapper.addnode(REntrefer,0)
                        self.femm_wrapper.addnode(-REntrefer,0)
                        self.femm_wrapper.addarc(REntrefer,0,-REntrefer,0,180,1)
                        self.femm_wrapper.addarc(-REntrefer,0,REntrefer,0,180,1)
                        
                        self.femm_wrapper.selectnode(REntrefer,0)
                        self.femm_wrapper.selectnode(-REntrefer,0)
                        self.femm_wrapper.setnodeprop('ENTREFER',2)
                        self.femm_wrapper.clearselected()
                			
                        self.femm_wrapper.selectarcsegment(0,-REntrefer)
                        self.femm_wrapper.selectarcsegment(0,REntrefer)
                        self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'ENTREFER',0,2)
                        self.femm_wrapper.clearselected()
                        self.femm_wrapper.addblocklabel(0,REntrefer-TailleMailleEntrefer/2)
                        self.femm_wrapper.selectlabel(0,REntrefer-TailleMailleEntrefer/2)

                    if (IndREntrefer == 1):
                        NumeroGroupe=1
                    else:
                        NumeroGroupe=2
                        
                    self.femm_wrapper.setblockprop('air',0,TailleMailleEntrefer,0,0,NumeroGroupe,1)
                    self.femm_wrapper.clearselected()
            self.femm_wrapper.clearselected()
        
            SWxcoupe=(SRe*sin(SAngElec/2))*cos(Angle)-(SRe*sin(SAngElec/2))*sin(Angle) #self.SPx
            SWycoupe=(SRe*cos(SAngElec/2))*sin(Angle)+(SRe*cos(SAngElec/2))*cos(Angle) #self.SPy            
            
            if repetition <2:
                """ Draw the circule with a radius of Sre """
                self.femm_wrapper.addnode(0,SRe)
                self.femm_wrapper.addnode(0,-SRe)
                self.femm_wrapper.addarc(0,-SRe,0,SRe,180,1)
                self.femm_wrapper.addarc(0,SRe,0,-SRe,180,1)
            
            if repetition > 1 : 
                
                self.femm_wrapper.addnode(0,0)
                self.femm_wrapper.addnode(SRx,SRy)
                self.femm_wrapper.addnode(SRxrot,SRyrot)

                self.femm_wrapper.addsegment(SRx,SRy,0,0)
                self.femm_wrapper.addsegment(0,0,SRxrot,SRyrot)

                self.femm_wrapper.addarc(SPx,SPy,SE1x,SE1y,SAngL1pOEo/2*180/pi,1)
                
                                  
        elif self.rotor_type == 'SPM':
            if repetition < 2:
                """ Draw the circule with a radius of Sre """
                self.femm_wrapper.addnode(0,SRe)
                self.femm_wrapper.addnode(0,-SRe)
                self.femm_wrapper.addarc(0,-SRe,0,SRe,180,1)
                self.femm_wrapper.addarc(0,SRe,0,-SRe,180,1)
                
            self.femm_wrapper.addnode(SZx,SZy)
                          
            self.femm_wrapper.selectnode(0,SRe)		
            self.femm_wrapper.selectnode(0,-SRe)
            self.femm_wrapper.setnodeprop('TOLE',2)
            self.femm_wrapper.clearselected()
               	
            self.femm_wrapper.selectarcsegment(SRe,0)
            self.femm_wrapper.selectarcsegment(-SRe,0)
            MaxSegDeg=2*asin(TailleMaille/2/SRe)*180/pi
            self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'TOLE',0,2)  			
            self.femm_wrapper.clearselected()
            
            self.femm_wrapper.addnode(0,0)        
        
        elif self.rotor_type == 'Halbach':
            if repetition <2:
                """ Draw the circule with a radius of Sre """
                self.femm_wrapper.addnode(0,SRe)
                self.femm_wrapper.addnode(0,-SRe)
                self.femm_wrapper.addarc(0,-SRe,0,SRe,180,1)
                self.femm_wrapper.addarc(0,SRe,0,-SRe,180,1)
                
            self.femm_wrapper.addnode(SZx,SZy)
                          
            self.femm_wrapper.selectnode(0,SRe)		
            self.femm_wrapper.selectnode(0,-SRe)
            self.femm_wrapper.setnodeprop('TOLE',2)
            self.femm_wrapper.clearselected()
               	
            self.femm_wrapper.selectarcsegment(SRe,0)
            self.femm_wrapper.selectarcsegment(-SRe,0)
            MaxSegDeg=2*asin(TailleMaille/2/SRe)*180/pi
            self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'TOLE',0,2)  			
            self.femm_wrapper.clearselected()        
        
        if repetition > 1:
            """ Cerlce with SRe radius """
            self.femm_wrapper.addnode(0,SRe)
            self.femm_wrapper.addnode(-SRe*sin(Angle),SRe*cos(Angle))
            self.femm_wrapper.addarc(0,SRe,-SRe*sin(Angle),SRe*cos(Angle),360/repetition,1)
            
            """ Cut realisation """         
            self.femm_wrapper.addnode(ALa/repetition,SRe)
            self.femm_wrapper.addnode(RRe+TailleMaille,0)

            self.femm_wrapper.selectrectangle(ALa/repetition,SRe,RRe+TailleMaille,0)
                            
            self.femm_wrapper.selectnode(SIxrot,SIyrot)
            self.femm_wrapper.selectnode(SNxrot,SNyrot)
            self.femm_wrapper.selectnode(SJxrot,SJyrot)
            self.femm_wrapper.selectnode(SK2xrot,SK2yrot)
            self.femm_wrapper.selectnode(SK1xrot,SK1yrot)
            self.femm_wrapper.selectnode(SL2xrot,SL2yrot)
            self.femm_wrapper.selectnode(SL1xrot,SL1yrot)
            self.femm_wrapper.selectnode(SMx*cos(Angle)-SMy*sin(Angle),SMx*sin(Angle)+SMy*cos(Angle))
            
            self.femm_wrapper.deleteselected()
            self.femm_wrapper.clearselected()
            
            """ Repetion of the part """
            self.femm_wrapper.selectcircle(0,0,SRe+TailleMaille,4)
            self.femm_wrapper.copyrotate(0,0,360/repetition,repetition)
            self.femm_wrapper.clearselected()
                        
            if self.rotor_type == 'Halbach':
                """trace entrefer"""
                self.femm_wrapper.addblocklabel(-(RRe+(ALo+e)/2)*sin(Angle/2),(RRe+(ALo+e)/2)*cos(Angle/2))
                self.femm_wrapper.selectlabel(-(RRe+(ALo+e)/2)*sin(Angle/2),(RRe+(ALo+e)/2)*cos(Angle/2))
                self.femm_wrapper.setblockprop('air',0,TailleMailleEntrefer,0,0,2,1)
                self.femm_wrapper.clearselected()
            
    def __str__(self):
        s = 'Parameters of the stator: \n'
        for var in self.parameters.keys():
            s += var.__str__()
        return s
#
#    def build_data_frame(self):
#        col_names = ['Component', 'Name', 'Value', 'Units', 'Desc']
#        data = []
#        for var in self.parameters.keys():
#            {'Component': 'Stator', 'Name': var.name, 'Value': var.value, 'Unit': var.units, 'Desc': var.desc}
#
#        self.data_frame = self.data_frame.append(data)[col_names]
#
#    def f(self, component):
#        return self.data_frame[self.data_frame.Component==component]
#
#    def print_variables(self):
#        self.build_data_frame()
#        widgets.interact(self.f, Component=set(self.data_frame.Component))