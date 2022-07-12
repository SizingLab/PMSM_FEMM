from attr import get_run_validators
import femm
import numpy as np
from math import pi, cos, sin, asin, tan

from variable import Variable

import pandas as pd
import ipywidgets as widgets

class BaseRotor:

    'Solver Parameters '
    AngleSommetMinMaillage = Variable('AngleSommetMinMaillage', 10, '[-]', 'Minimum submit angle of the mesh element')
    Precision  = Variable('Precision', 1e-008, '[-]', 'Solver precision')
    
    'Type of command (AC:Flag_AC_DC=1) and (DC:Flag_AC_DC=0) '
    Flag_AC_DC = Variable('Flag_AC_DC', 1, '[-]', 'Type of command AC : 1, DC:0')
    
    'Matirial: FlagBHpoint=0 calcul linéaire et FlagBHpoint=1 calcul non linéaire'
    FlagBHpoint = Variable('FlagBHpoint', 1, '[-]', 'for materials definiton')
    FlagBHpointAimant = Variable('FlagBHpointAimant', 0, '[-]', ' ')
    FlagToleranceAimant = Variable('FlagToleranceAimant', 2, '[-]', '1:Mini, 2:Normal, 3:Maxi')

    'Definition of the geometry which supports the magnets'
    RAngDepSupport = Variable('RAngDepSupport', 12*pi/180, '[Deg]', 'Taper angle of the support when opening')

    'Definition of the permanent magnety geometry'
    
    'Definition of the permanent magnet geometry'
    TempAimant = Variable('TempAimant', 20, '[°C]', 'Magnet temperature')
    
    
   

    def __init__(self, AngleSommetMinMaillage=AngleSommetMinMaillage, Precision=Precision, Flag_AC_DC=Flag_AC_DC, FlagBHpoint=FlagBHpoint, FlagBHpointAimant=FlagBHpointAimant, FlagToleranceAimant=FlagToleranceAimant, TempAimant=TempAimant, RAngDepSupport=RAngDepSupport):
            self.parameters = {}
            self.parameters[AngleSommetMinMaillage.name] = AngleSommetMinMaillage
            self.parameters[Precision.name]=Precision
            self.parameters[Flag_AC_DC.name] = Flag_AC_DC
            self.parameters[FlagBHpoint.name] = FlagBHpoint
            self.parameters[FlagBHpointAimant.name] = FlagBHpointAimant
            self.parameters[FlagToleranceAimant.name] = FlagToleranceAimant
            self.parameters[TempAimant.name] = TempAimant
            self.parameters[RAngDepSupport.name] = RAngDepSupport

            self.data_frame = pd.DataFrame()

            
#            self.build_data_frame()

    def get_value_rotor(self,name):
        return self.parameters[name].value
    
    def add_parameter(self, name, value, units, desc):
        self.parameters[name] = Variable(name, value, units, desc)

    def __str__(self):
        s = 'Parameters of the rotor: \n'
        for var in self.parameters.keys():
            s += var.__str__()
        return s

    def build_data_frame(self):
        col_names = ['Component', 'Name', 'Value', 'Units', 'Desc']
        data = []
        for var in self.parameters.keys():
            {'Component': 'Rotor', 'Name': var.name, 'Value': var.value, 'Unit': var.units, 'Desc': var.desc}

        self.data_frame = self.data_frame.append(data)[col_names]

    def f(self, component):
        return self.data_frame[self.data_frame.Component==component]

    def print_variables(self):
        self.build_data_frame()
        widgets.interact(self.f, Component=set(self.data_frame.Component))
 
### (Aurélien) Découpage de la classe IPM en deux classes : une pour le modèle et une pour la géométrie.

class IPM_Model(BaseRotor):
    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Motor geometric variables definition (BLAC_parametres_geometrie)_IPM
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    
    SDe = Variable('SDe', 120, '[mm]', 'Stator Exterior diameter')
    
    """ Form factor definition: (relative to the exterior stator rayon)"""
    SRe = Variable('SRe', SDe.value/2, '[mm]', 'Stator_Exterior radius')
    SRe_ref = Variable('Sre_ref', 62./2, '[mm]', 'Reference Exterior Stator rayon')
    K = Variable('K', SRe.value/SRe_ref.value, '[-]', 'Form factor')
    SEt = Variable('SEt', 45, '[-]', 'Motor, length')               # Motor Lenght 
    
    SRi = Variable('SRi', 18.36, '[mm]', 'Stator interior radius')
    ALa = Variable('ALa', 4.76, '[mm]', 'Permanent Magnet thickness')
    RRi = Variable('RRi', 7.44, '[mm]', 'Rotor Interior Radius')
    J_den = Variable('J_den', 17, '[A/mm²]', 'Wire density')
        
    Np_ref = Variable('Np_ref', 10, '[Magnets]', 'Reference permanent magnet number')
    Np = Variable('Np', 10, '[Magnets]', 'Permanent magnet number')
    KNp = Variable('KNp', Np.value/Np_ref.value, '[-]', 'Coefficient ratio of the pole number')

    'Airgap definition'
    e = Variable('e', 0.4, '[mm]', 'Air gap thickness')

    'Definition of the geometry which supports the magnets (Rotor)'
    RRe  = Variable('RRe', SRi.value-e.value, '[mm]', 'Exterior rotor radius')
    
    """ Definition of the Permanent Magnets geometry"""
    RLo = Variable('RLo', 0.8, '[mm]', ' ')
    RLa = Variable('RLa', 0.8, '[mm]', ' ')
    ALo = Variable('ALo', 0.88*RRe.value-RRi.value, '[mm]', 'Magnet length')
    ARi = Variable('ARi', RRi.value+RLo.value, '[mm]', 'Magnet interior radius')
    ARe = Variable('ARe', ARi.value+ALo.value, '[mm]', 'Magnet exterior radius')

    """ Mesh Definition:"""
    TailleMailleEntrefer = Variable('TailleMailleEntrefer', e.value/2, '[-]', 'Used for airgap material definition')
    TailleMaille = Variable('TailleMaille', 1.0, '[-]', 'Mesh size')
    TailleMailleJeu = Variable('TailleMailleJeu', 0.25, '[-]', 'Mesh size in the clearence')
    TailleMailleBobine= Variable('TailleMailleBobine', 1, '[-]', 'Mesh size for the winding')
    
    
    def __init__(self, motif='10/12', repetition='1', Np=Np, Np_ref=Np_ref, KNp=KNp, SDe=SDe, SRi=SRi, ALa=ALa, RRi=RRi, J_den=J_den, SRe=SRe, SRe_ref=SRe_ref, K=K, SEt=SEt, e=e, RRe=RRe, RLo=RLo, RLa=RLa, ALo=ALo, ARi=ARi, ARe=ARe, TailleMailleEntrefer=TailleMailleEntrefer, TailleMaille=TailleMaille, TailleMailleJeu=TailleMailleJeu, TailleMailleBobine=TailleMailleBobine):
        
        #super(BaseRotor, self).__init__()
        super().__init__()
        #self.parameters = {}
        self.motif = motif
        self.repetition = repetition
        self.parameters[Np.name] = Np
        self.parameters[Np_ref.name] = Np_ref
        self.parameters[KNp.name] = KNp
        self.parameters[SDe.name] = SDe
        self.parameters[SRi.name] = SRi
        self.parameters[ALa.name] = ALa
        self.parameters[RRi.name] = RRi
        self.parameters[J_den.name] = J_den
        self.parameters[SRe.name] = SRe
        self.parameters[SRe_ref.name] = SRe_ref
        self.parameters[K.name] = K
        self.parameters[SEt.name] = SEt
        self.parameters[e.name] = e
        self.parameters[RRe.name] = RRe
        self.parameters[RLo.name] = RLo
        self.parameters[RLa.name] = RLa
        self.parameters[ALo.name] = ALo
        self.parameters[ARi.name] = ARi
        self.parameters[ARe.name] = ARe
        self.parameters[TailleMailleEntrefer.name] = TailleMailleEntrefer
        self.parameters[TailleMaille.name] = TailleMaille
        self.parameters[TailleMailleJeu.name] = TailleMailleJeu
        self.parameters[TailleMailleBobine.name] = TailleMailleBobine

class IPM_GeomGeneration(BaseRotor):

    def __init__(self, IPMModel, femm_wrapper):
        self.IPMModel =  IPMModel
        self.femm_wrapper = femm_wrapper  
        """SRe=self.IPMModel.parameters[SRe.name]"""

    def get_value(self, name):
        
        return self.IPMModel.parameters[name].value

    
    def variable_calcul(self,SRe,J_den):
        return self.IPMModel.SRe.value, self.IPMModel.J_den.value
    
    def draw(self, stator):
        repetition = self.IPMModel.repetition
        self.IPMModel.parameters['Np'].value = int(self.IPMModel.motif.split('/')[0])
        Np = self.IPMModel.parameters['Np'].value
        Np_ref = self.IPMModel.parameters['Np_ref'].value
        
        self.IPMModel.parameters['KNp'].value = Np/Np_ref
        KNp = self.IPMModel.parameters['KNp'].value

        K = self.IPMModel.parameters['K'].value
        Np_ref = self.IPMModel.parameters['Np_ref'].value
        SRi = self.IPMModel.parameters['SRi'].value*K
        ALa = self.IPMModel.parameters['ALa'].value*K/(KNp*repetition)
        RRi = self.IPMModel.parameters['RRi'].value*K
        e = self.IPMModel.parameters['e'].value*K
        self.IPMModel.parameters['RRe'].value = SRi-e
        RRe = self.IPMModel.parameters['RRe'].value
        RLo = self.IPMModel.parameters['RLo'].value*K/KNp
        RLa = self.IPMModel.parameters['RLa'].value*K/KNp
        self.IPMModel.parameters['ALo'].value = 0.88*RRe-RRi
        ALo = self.IPMModel.parameters['ALo'].value
        self.IPMModel.parameters['ARi'].value = RRi + RLo
        ARi = self.IPMModel.parameters['ARi'].value
        self.IPMModel.parameters['ARe'].value = ARi+ALo
        ARe = self.IPMModel.parameters['ARe'].value
        self.IPMModel.parameters['TailleMailleEntrefer'].value = e/2
        TailleMailleEntrefer = self.IPMModel.parameters['TailleMailleEntrefer'].value
        TailleMaille = self.IPMModel.parameters['TailleMaille'].value*K
        self.IPMModel.parameters['SRe'].value = self.IPMModel.parameters['SDe'].value/2
        SRe = self.IPMModel.parameters['SRe'].value


        MaxSegDegPE1 = stator.MaxSegDegPE1 
        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                         Draw Rotor
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
        
        """ CALCULATION OF THE COORDINATES OF THE POINTS USED FOR THE CONSTRUCTION OF THE ROTOR """
        
        """ calculation of the points defining the geometry of the support """
        RAngElec=2*pi/(Np*repetition)        # angle P O M		
        
        """ Definition of the external part of the support: point E """
        REx=ALa/2               # point E 
        REy=(RRe**2-REx**2)**.5	# point E 
        RE1x=REx-(0.5*K)/repetition
        RE1y=REy-0.1*K
        RE2x=RE1x+(0.05*K)/repetition
        RE2y=RE1y-(0.7*K)/repetition
        RE3x=REx-(0.2*K)/repetition
        RE3y=RE2y
        RE4x=REx
        RE4y=RE2y-(0.2*K)/repetition
        
        """ Définition of the angle """
        RAngEOY=asin(REx/RRe)                   # angle E Origin Axis Y
        RAngLOE=RAngElec-RAngEOY*2              # angle L Origin E 
        
        """ Definition of the point H """
        RAngVOH=asin(RLa/2/RRi)*2	              # angle Ip O H
#        RAngHOI=RAngElec-RAngVOH					# angle Ip Origin H
        RH1x=(RRi+0.6*K)*(sin(RAngElec/2-RAngVOH/2))				# point H1
        RH1y=(RRi+0.6*K)*(cos(RAngElec/2-RAngVOH/2))
        RH2x=ALa/2
        RH2y=RRi
        
        """ Definition of the point G """
        RGx=RH1x+RLo*sin(RAngElec/2);								# point G
        RGy=RH1y+RLo*cos(RAngElec/2);								# point G
        
        """ Definition of the point F """
        RFx=ALa/2											# point F (without connecting radius)
        RFy=ARi
        
        """ Definition of the point L mirror of E relative of Y """
        RLx=-REx
        RLy=REy
        RL1x=-RE1x
        RL1y=RE1y
        RL2x=-RE2x
        RL2y=RE2y
        RL3x=-RE3x
        RL3y=RE3y
        RL4x=-RE4x
        RL4y=RE4y
        
        " Definition of the point I mirror of H relative to Y """
        RI1x=-RH1x
        RI1y=RH1y
        RI2x=-RH2x
        RI2y=RH2y
        
        """ Definition of the point J mirror of G relative to Y """
        RJx=-RGx
        RJy=RGy
        
        """ Definition of the point K1 and K2 mirror of F1 and F2 relative to Y """
        RKx=-RFx
        RKy=RFy
        		
        """ Definition of the point M	"""
        RMx=-RRe*sin(RAngElec/2)
        RMy=RRe*cos(RAngElec/2)
        
#        """ Définition du point P """
#        RPx=-RMx
#        RPy=RMy
        
        """ Definition of variables used to select arcs and segments """
        RPEx=RRe*sin((RAngElec/2+RAngEOY)/2)                                   
        RPEy=RRe*cos((RAngElec/2+RAngEOY)/2)
        RLMx=-RPEx
        RLMy=RPEy
#        RHIx=0   
#        RHIy=RRi
        
        """ Definition of the points of the part between the inner tube and the magnet  """  
        R1x=0.4*K
        R1y=RRi
        R2x=R1x
        R2y=ARi
        R3x=-R2x
        R3y=R2y
        R4x=-R1x
        R4y=R1y
        
        """ Upper part of the magnet """
        A1x=ALa/2
        A1y=ARe-(0.3*K)/repetition
        A4x=-A1x
        A4y=A1y
        
        RRx = 0
        RRy = ARi
        
        """ draw magent holder """
        RAnglep=0-2*pi/Np
        RPxrot=RMx*cos(RAnglep)-RMy*sin(RAnglep)
        RPyrot=RMx*sin(RAnglep)+RMy*cos(RAnglep)
        self.femm_wrapper.addnode(RPxrot,RPyrot)
        self.femm_wrapper.selectnode(RPxrot,RPyrot)	
        self.femm_wrapper.setnodeprop('rotor',9)
        self.femm_wrapper.clearselected()
                
        for AngleDeg in np.arange (0,(360+Np)/repetition,360/(repetition*Np)):
            Angle=AngleDeg*pi/180
            S=sin(Angle);
            C=cos(Angle);
            RExrot=REx*C-REy*S;
            REyrot=REx*S+REy*C;
            RE1xrot=RE1x*C-RE1y*S;
            RE1yrot=RE1x*S+RE1y*C;
            RE2xrot=RE2x*C-RE2y*S;
            RE2yrot=RE2x*S+RE2y*C;
            RE3xrot=RE3x*C-RE3y*S;
            RE3yrot=RE3x*S+RE3y*C;
            RE4xrot=RE4x*C-RE4y*S;
            RE4yrot=RE4x*S+RE4y*C;
            RFxrot=RFx*C-RFy*S;
            RFyrot=RFx*S+RFy*C;		
            RH1xrot=RH1x*C-RH1y*S;
            RH1yrot=RH1x*S+RH1y*C;
            RH2xrot=RH2x*C-RH2y*S;
            RH2yrot=RH2x*S+RH2y*C;
            RI1xrot=RI1x*C-RI1y*S;
            RI1yrot=RI1x*S+RI1y*C;
            RI2xrot=RI2x*C-RI2y*S;
            RI2yrot=RI2x*S+RI2y*C;		
            RGxrot=RGx*C-RGy*S;
            RGyrot=RGx*S+RGy*C;
            RJxrot=RJx*C-RJy*S;
            RJyrot=RJx*S+RJy*C;
            RKxrot=RKx*C-RKy*S;
            RKyrot=RKx*S+RKy*C;		
            RLxrot=RLx*C-RLy*S;
            RLyrot=RLx*S+RLy*C;
            RL1xrot=RL1x*C-RL1y*S;
            RL1yrot=RL1x*S+RL1y*C;
            RL2xrot=RL2x*C-RL2y*S;
            RL2yrot=RL2x*S+RL2y*C;
            RL3xrot=RL3x*C-RL3y*S;
            RL3yrot=RL3x*S+RL3y*C;
            RL4xrot=RL4x*C-RL4y*S;
            RL4yrot=RL4x*S+RL4y*C;		
            RMxrot=RMx*C-RMy*S;
            RMyrot=RMx*S+RMy*C;		
            RPExrot=RPEx*C-RPEy*S;
            RPEyrot=RPEx*S+RPEy*C;
            RLMxrot=RLMx*C-RLMy*S;
            RLMyrot=RLMx*S+RLMy*C;
#            RIJxrot=RHIx*C-RHIy*S;
#            RIJyrot=RHIx*S+RHIy*C;        
            R1xrot=R1x*C-R1y*S;
            R1yrot=R1x*S+R1y*C;
            R2xrot=R2x*C-R2y*S;
            R2yrot=R2x*S+R2y*C;
            R3xrot=R3x*C-R3y*S;
            R3yrot=R3x*S+R3y*C;
            R4xrot=R4x*C-R4y*S;
            R4yrot=R4x*S+R4y*C;  
                
            A1xrot=A1x*C-A1y*S;
            A1yrot=A1x*S+A1y*C;
            A4xrot=A4x*C-A4y*S;
            A4yrot=A4x*S+A4y*C;
        		
            self.femm_wrapper.addnode(RExrot,REyrot);
            self.femm_wrapper.addnode(RE1xrot,RE1yrot);
            self.femm_wrapper.addnode(RE2xrot,RE2yrot);
            self.femm_wrapper.addnode(RE3xrot,RE3yrot);
            self.femm_wrapper.addnode(RE4xrot,RE4yrot);
            self.femm_wrapper.addnode(RLxrot,RLyrot);
            self.femm_wrapper.addnode(RL1xrot,RL1yrot);
            self.femm_wrapper.addnode(RL2xrot,RL2yrot);
            self.femm_wrapper.addnode(RL3xrot,RL3yrot);
            self.femm_wrapper.addnode(RL4xrot,RL4yrot);
            self.femm_wrapper.addnode(RMxrot,RMyrot);
            self.femm_wrapper.addnode(A1xrot,A1yrot);
            self.femm_wrapper.addnode(A4xrot,A4yrot);
            
            self.femm_wrapper.addsegment(RE1xrot,RE1yrot,RExrot,REyrot);
            self.femm_wrapper.addsegment(RE1xrot,RE1yrot,RE2xrot,RE2yrot);
            self.femm_wrapper.addsegment(RE2xrot,RE2yrot,RE3xrot,RE3yrot);
            self.femm_wrapper.addsegment(RE3xrot,RE3yrot,RE4xrot,RE4yrot);
            self.femm_wrapper.addsegment(RL1xrot,RL1yrot,RLxrot,RLyrot);
            self.femm_wrapper.addsegment(RL1xrot,RL1yrot,RL2xrot,RL2yrot);
            self.femm_wrapper.addsegment(RL2xrot,RL2yrot,RL3xrot,RL3yrot);
            self.femm_wrapper.addsegment(RL3xrot,RL3yrot,RL4xrot,RL4yrot);
            self.femm_wrapper.addsegment(RL4xrot,RL4yrot,A4xrot,A4yrot);
            self.femm_wrapper.addsegment(RE4xrot,RE4yrot,A1xrot,A1yrot);
        		   		
            self.femm_wrapper.addarc(RPxrot,RPyrot,RExrot,REyrot,RAngLOE/2*180/pi,1)
            self.femm_wrapper.addarc(RLxrot,RLyrot,RMxrot,RMyrot,RAngLOE/2*180/pi,1);
        			
            self.femm_wrapper.selectnode(RExrot,REyrot);
            self.femm_wrapper.selectnode(RE1xrot,RE1yrot);
            self.femm_wrapper.selectnode(RE2xrot,RE2yrot);
            self.femm_wrapper.selectnode(RE3xrot,RE3yrot);
            self.femm_wrapper.selectnode(RE4xrot,RE4yrot);
            self.femm_wrapper.selectnode(RKxrot,RKyrot);
            self.femm_wrapper.selectnode(RLxrot,RLyrot);
            self.femm_wrapper.selectnode(RL1xrot,RL1yrot);
            self.femm_wrapper.selectnode(RL2xrot,RL2yrot);
            self.femm_wrapper.selectnode(RL3xrot,RL3yrot);
            self.femm_wrapper.selectnode(RL4xrot,RL4yrot);
            self.femm_wrapper.selectnode(RMxrot,RMyrot);
            self.femm_wrapper.setnodeprop('rotor',9);
            self.femm_wrapper.clearselected()
           		
            self.femm_wrapper.selectsegment((RE1xrot+RExrot)/2,(RE1yrot+REyrot)/2);
            self.femm_wrapper.selectsegment((RE1xrot+RE2xrot)/2,(RE1yrot+RE2yrot)/2);
            self.femm_wrapper.selectsegment((RE2xrot+RE3xrot)/2,(RE2yrot+RE3yrot)/2);
            self.femm_wrapper.selectsegment((RE4xrot+RE3xrot)/2,(RE4yrot+RE3yrot)/2);
            self.femm_wrapper.selectsegment((RFxrot+RGxrot)/2,(RFyrot+RGyrot)/2);
            self.femm_wrapper.selectsegment((RH1xrot+RGxrot)/2,(RH1yrot+RGyrot)/2);
            self.femm_wrapper.selectsegment((RH2xrot+R1xrot)/2,(RH2yrot+R1yrot)/2);
            self.femm_wrapper.selectsegment((R2xrot+R1xrot)/2,(R2yrot+R1yrot)/2);
            self.femm_wrapper.selectsegment((R2xrot+R3xrot)/2,(R2yrot+R3yrot)/2);
            self.femm_wrapper.selectsegment((R3xrot+R4xrot)/2,(R3yrot+R4yrot)/2);
            self.femm_wrapper.selectsegment((R4xrot+RI2xrot)/2,(R4yrot+RI2yrot)/2);
            self.femm_wrapper.selectsegment((RI1xrot+RJxrot)/2,(RI1yrot+RJyrot)/2);
            self.femm_wrapper.selectsegment((RJxrot+RKxrot)/2,(RJyrot+RKyrot)/2);
            self.femm_wrapper.selectsegment((RL1xrot+RLxrot)/2,(RL1yrot+RLyrot)/2);
            self.femm_wrapper.selectsegment((RL1xrot+RL2xrot)/2,(RL1yrot+RL2yrot)/2);
            self.femm_wrapper.selectsegment((RL2xrot+RL3xrot)/2,(RL2yrot+RL3yrot)/2);
            self.femm_wrapper.selectsegment((RL4xrot+RL3xrot)/2,(RL4yrot+RL3yrot)/2);
            self.femm_wrapper.selectsegment((RKxrot+RL4xrot)/2,(RKyrot+RL4yrot)/2);
            self.femm_wrapper.setsegmentprop('rotor',TailleMaille,1,0,9);	
            self.femm_wrapper.clearselected()
        		
            self.femm_wrapper.selectarcsegment(RPExrot,RPEyrot);		
            self.femm_wrapper.selectarcsegment(RLMxrot,RLMyrot);		
            self.femm_wrapper.setarcsegmentprop(MaxSegDegPE1,'rotor',0,9); 
            self.femm_wrapper.clearselected()
        										
            RPxrot=RMxrot;
            RPyrot=RMyrot;
            A=(ALa/2+2*pi*(ARi+ALo/2)/Np)/(2*repetition);
            B= ARi+ALo/2;
            Ax= A*C-S*B;
            Ay= A*S+B*C;
            self.femm_wrapper.addblocklabel(Ax,Ay);
            self.femm_wrapper.selectlabel(Ax,Ay);
            MatiereSupportAimant='FeSi 0.35mm';
            self.femm_wrapper.setblockprop(MatiereSupportAimant,0,TailleMaille,0,0,9,1);
            self.femm_wrapper.clearselected()
        
        """ Definition points for magnet construction """
        A1x=ALa/2;
        A1y=ARe-(0.3*K)/repetition;
        A2x=A1x-(0.3*K)/repetition;
        A2y=ARe;
        A3x=-A2x;
        A3y=A2y;
        A4x=-A1x;
        A4y=A1y;
        A8x=A1x;
        A8y=ARi+0.3*K;
        A7x=A2x;
        A7y=ARi;
        A5x=-A8x;
        A5y=A8y;
        A6x=-A7x;
        A6y=A7y;
        
        AngleA1OA2=45;
        
        """ Draw the Magnets """     
        Sens=pi

        for AngleDeg in np.arange (0,(360+Np)/repetition,360/(repetition*Np)):
            Angle=AngleDeg*pi/180
            S=sin(Angle)
            C=cos(Angle)
        		
            A1xrot=A1x*C-A1y*S
            A1yrot=A1x*S+A1y*C
            A2xrot=A2x*C-A2y*S
            A2yrot=A2x*S+A2y*C
            A3xrot=A3x*C-A3y*S
            A3yrot=A3x*S+A3y*C
            A4xrot=A4x*C-A4y*S
            A4yrot=A4x*S+A4y*C
            A5xrot=A5x*C-A5y*S
            A5yrot=A5x*S+A5y*C
            A6xrot=A6x*C-A6y*S
            A6yrot=A6x*S+A6y*C
            A7xrot=A7x*C-A7y*S
            A7yrot=A7x*S+A7y*C
            A8xrot=A8x*C-A8y*S
            A8yrot=A8x*S+A8y*C
            RRxrot=RRx*C-RRy*S
            RRyrot=RRx*S+RRy*C

            self.femm_wrapper.addnode(A1xrot,A1yrot)
            self.femm_wrapper.addnode(A2xrot,A2yrot)
            self.femm_wrapper.addnode(A3xrot,A3yrot)
            self.femm_wrapper.addnode(A4xrot,A4yrot)
            self.femm_wrapper.addnode(A5xrot,A5yrot)
            self.femm_wrapper.addnode(A6xrot,A6yrot)
            self.femm_wrapper.addnode(A7xrot,A7yrot)
            self.femm_wrapper.addnode(A8xrot,A8yrot)
                
            self.femm_wrapper.addsegment(A2xrot,A2yrot,A3xrot,A3yrot)
            self.femm_wrapper.addsegment(A4xrot,A4yrot,A5xrot,A5yrot)
            self.femm_wrapper.addsegment(A6xrot,A6yrot,A7xrot,A7yrot)
            self.femm_wrapper.addsegment(A8xrot,A8yrot,A1xrot,A1yrot)
        
            if (AngleDeg>=360/(Np*repetition)):
                self.femm_wrapper.addsegment(A7xrot,A7yrot,A9x,A9y)
               
            self.femm_wrapper.addarc(A1xrot,A1yrot,A2xrot,A2yrot,AngleA1OA2,1)
            self.femm_wrapper.addarc(A3xrot,A3yrot,A4xrot,A4yrot,AngleA1OA2,1)
            self.femm_wrapper.addarc(A5xrot,A5yrot,A6xrot,A6yrot,AngleA1OA2,1)
            self.femm_wrapper.addarc(A7xrot,A7yrot,A8xrot,A8yrot,AngleA1OA2,1)
                
            self.femm_wrapper.selectnode(A1xrot,A1yrot)
            self.femm_wrapper.selectnode(A2xrot,A2yrot)
            self.femm_wrapper.selectnode(A3xrot,A3yrot)
            self.femm_wrapper.selectnode(A4xrot,A4yrot)
            self.femm_wrapper.selectnode(A5xrot,A5yrot)
            self.femm_wrapper.selectnode(A6xrot,A6yrot)
            self.femm_wrapper.selectnode(A7xrot,A7yrot)
            self.femm_wrapper.selectnode(A8xrot,A8yrot)
            self.femm_wrapper.setnodeprop('aimants',3)
            self.femm_wrapper.clearselected()
                         		
            self.femm_wrapper.selectsegment((A2xrot+A3xrot)/2,(A2yrot+A3yrot)/2)
            self.femm_wrapper.selectsegment((A4xrot+A5xrot)/2,(A4yrot+A5yrot)/2)
            self.femm_wrapper.selectsegment((A6xrot+A7xrot)/2,(A6yrot+A7yrot)/2)
            self.femm_wrapper.selectsegment((A8xrot+A1xrot)/2,(A8yrot+A1yrot)/2)
                
            if (AngleDeg>=360/(Np*repetition)):
                self.femm_wrapper.selectsegment((A7xrot+A9x)/2,(A7yrot+A9y)/2)
            
            self.femm_wrapper.setsegmentprop('aimant',TailleMaille,1,0,3)
            self.femm_wrapper.clearselected()
                
            self.femm_wrapper.selectarcsegment (A2xrot,A2yrot)
            self.femm_wrapper.selectarcsegment (A3xrot,A3yrot)
            self.femm_wrapper.selectarcsegment (A5xrot,A5yrot)
            self.femm_wrapper.selectarcsegment (A7xrot,A7yrot)
            MaxSegDeg=2*asin(TailleMailleEntrefer/2/RRe)*180/pi
            self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'aimant',0,3)
            self.femm_wrapper.clearselected()
            # segment above the magnets
            self.femm_wrapper.selectsegment((A4xrot+RL4xrot)/2,(A4yrot+RL4yrot)/2)
            self.femm_wrapper.selectsegment((A1xrot+RE4xrot)/2,(A1yrot+RE4yrot)/2)
            self.femm_wrapper.setsegmentprop('rotor',TailleMaille,1,0,3)
            self.femm_wrapper.clearselected()
                 
            self.femm_wrapper.addblocklabel(((A5x+A7x)/2)*C-((A2y+A7y)/2)*S,((A5x+A7x)/2)*S+((A2y+A7y)/2)*C)
            self.femm_wrapper.selectlabel(((A5x+A7x)/2)*C-((A2y+A7y)/2)*S,((A5x+A7x)/2)*S+((A2y+A7y)/2)*C)
            MatiereAimant='Sm2Co17'
            self.femm_wrapper.setblockprop(MatiereAimant,0,TailleMaille,0,AngleDeg+Sens*180/pi,3,1)
            self.femm_wrapper.clearselected()
                
            Sens=Sens+pi;
                
            A9x=A6xrot;
            A9y=A6yrot;
            self.femm_wrapper.addnode(A9x,A9y)
            S=sin(Angle)
            C=cos(Angle)
            
        Sens=Sens+pi;
        
        if repetition > 1:
            
            self.femm_wrapper.addblocklabel((-(2*A5x+A8x)/2)*C-((A4y+A5y)/2)*S,(-(2*A5x+A8x)/2)*S+((A4y+A5y)/2)*C)
            self.femm_wrapper.selectlabel((-(2*A5x+A8x)/2)*C-((A4y+A5y)/2)*S,(-(2*A5x+A8x)/2)*S+((A4y+A5y)/2)*C)
            MatiereAimant='Sm2Co17'
            self.femm_wrapper.setblockprop(MatiereAimant,0,TailleMaille,0,AngleDeg-180,3,1) #
            self.femm_wrapper.clearselected()
            
            """ Carrying out the cut """
            self.femm_wrapper.addnode((A2x+A3x)/2,(A2y+A3y)/2)
            self.femm_wrapper.addnode(RRx,RRy)
            self.femm_wrapper.addnode(0,0)    
            self.femm_wrapper.addnode(RRxrot,RRyrot)
            self.femm_wrapper.addnode((A2xrot+A3xrot)/2,(A2yrot+A3yrot)/2)
            
            self.femm_wrapper.selectnode(A3xrot,A3yrot)
            self.femm_wrapper.selectnode(A4xrot,A4yrot)
            self.femm_wrapper.selectnode(A5xrot,A5yrot)
            self.femm_wrapper.selectnode(A6xrot,A6yrot)
            self.femm_wrapper.selectnode(RL4xrot,RL4yrot)
            self.femm_wrapper.selectnode(RL3xrot,RL3yrot)
            self.femm_wrapper.selectnode(RL2xrot,RL2yrot)
            self.femm_wrapper.selectnode(RL1xrot,RL1yrot)
            self.femm_wrapper.selectnode(RLxrot,RLyrot)
            self.femm_wrapper.selectnode(RPxrot,RPyrot)
            
            self.femm_wrapper.selectlabel(((A5x+A7x)/2)*C-((A2y+A7y)/2)*S,((A5x+A7x)/2)*S+((A2y+A7y)/2)*C)
            
            self.femm_wrapper.deleteselected()
            self.femm_wrapper.clearselected()

        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                         Draw air insinde the rotor
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
        MateriauTubeInterieur='air'
        self.femm_wrapper.clearselected()
        self.femm_wrapper.addblocklabel(-(RRi-TailleMaille)*sin(Angle/2),(RRi-TailleMaille)*cos(Angle/2))
        self.femm_wrapper.selectlabel(-(RRi-TailleMaille)*sin(Angle/2),(RRi-TailleMaille)*cos(Angle/2))
        self.femm_wrapper.setblockprop('air',0,2,0,0,1,1)
        self.femm_wrapper.clearselected() 


class SPM_Model(BaseRotor): 
    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Motor geometric variables definition (BLAC_parametres_geometrie)_SPM
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
    """ Form factor definition: (relative to the exterior stator rayon)"""
    SDe = Variable('SDe', 93.5, '[mm]', 'Exterior Stator diamter')
    SRe = Variable('SRe', SDe.value/2, '[mm]', 'Exterior Stator rayon')
    SRe_ref = Variable('SRe_ref', 120./2, '[mm]', 'Reference Exterior Stator rayon (From Parvex NX310)')
    K = Variable('K', SRe.value/SRe_ref.value, '[mm]', 'Form factor')
    ALo = Variable('ALo', 6, '[mm]', ' Magnet thickness ')
    RRi = Variable('RRi', 27.99, '[mm]', 'Rotor interior radius')
    SRi = Variable('SRi', 39.33, '[mm]', 'Stator interior radius')
    J_den = Variable('J_den', 35.02, '[A/mm²]', 'Current density')
    SEt = Variable('SEt', 175.03, '[mm]', 'Motor Lenght')
    
    Npref = Variable('Npref', 10, '[Magnets]', 'Reference permanent magnet number')
    Np = Variable('Np', 10, '[Magnets]', 'Permanent magnet number')
    KNp = Variable('Knp', Np.value/Npref.value, '[-]', 'Coefficient ratio of the pole number')
    
    """ Definition of the Permanent Magnets geometry"""						  
    ALa = Variable('ALa', 0.3, '[mm]', 'Space between the magnets')
    
    """ Airgap definition"""
    e = Variable('e', ALo.value+1.2, '[mm]', 'Airgap thickness')
     
    """Definition of the geometry which supports the magnets (Rotor)"""
    RRe = Variable('RRe', SRi.value-e.value, '[mm]', 'Rotor exterior radius')
    
    Nsp = Variable('Nsp', 1, '[-]', 'Number of segment')
    
    """ Mesh Definition:"""
    TailleMailleEntrefer = Variable('TailleMailleEntrefer', 1.2/4, '[-]', 'Used for airgap material definition')
    TailleMaille = Variable('TailleMaille', 1.0, '[-]', 'Mesh size')
    TailleMailleJeu = Variable('TailleMailleJeu', 0.25, '[-]', 'Mesh size in the clearence')
    TailleMailleBobine= Variable('TailleMailleBobine', 1, '[-]', 'Mesh size for the winding')


    def __init__(self, motif='10/12', repetition='1', Np=Np, SDe=SDe, SRe=SRe, SRe_ref=SRe_ref, K=K, ALo=ALo, RRi=RRi, SRi=SRi, J_den=J_den, SEt=SEt, ALa=ALa, 
                 e=e, RRe=RRe, Nsp=Nsp, TailleMailleEntrefer=TailleMailleEntrefer, TailleMaille=TailleMaille, 
                 TailleMailleJeu=TailleMailleJeu, TailleMailleBobine=TailleMailleBobine):
        
        super().__init__()

        self.motif = motif
        self.repetition = repetition
        self.parameters[Np.name] = Np
        self.parameters[SDe.name] = SDe 
        self.parameters[SRe.name] = SRe
        self.parameters[SRe_ref.name] = SRe_ref
        self.parameters[K.name] = K
        self.parameters[ALo.name] = ALo
        self.parameters[RRi.name] = RRi
        self.parameters[SRi.name] = SRi
        self.parameters[J_den.name] = J_den
        self.parameters[SEt.name] = SEt
        self.parameters[ALa.name] = ALa
        self.parameters[e.name] = e
        self.parameters[RRe.name] = RRe
        self.parameters[Nsp.name] = Nsp
        self.parameters[TailleMailleEntrefer.name] = TailleMailleEntrefer
        self.parameters[TailleMaille.name] = TailleMaille
        self.parameters[TailleMailleJeu.name] = TailleMailleJeu
        self.parameters[TailleMailleBobine.name] = TailleMailleBobine

class SPM_GeomGeneration(BaseRotor):

    def __init__(self, SPMModel, femm_wrapper):
        
        self.SPMModel =  SPMModel
        self.femm_wrapper = femm_wrapper  

    def get_value(self,name):
        return self.SPMModel.parameters[name].value
        
    def draw(self, stator):        
        
        repetition =self.SPMModel.repetition
        self.parameters['SRe'].value = self.SPMModel.parameters['SDe'].value/2
        SRe = self.SPMModel.parameters['SRe'].value
        RRi = self.SPMModel.parameters['RRi'].value
        K = self.SPMModel.parameters['K'].value
        
        
        self.SPMModel.parameters['Np'].value = float(self.motif.split('/')[0])
        Np = self.SPMModel.parameters['Np'].value
        Nsp = self.SPMModel.parameters['Nsp'].value
        self.SPMModel.parameters['TailleMaille'].value = self.SPMModel.parameters['TailleMaille'].value*K
        TailleMaille = self.SPMModel.parameters['TailleMaille'].value
        ALo = self.SPMModel.parameters['ALo'].value*K
        RRi = self.SPMModel.parameters['RRi'].value*K
        SRi = self.SPMModel.parameters['SRi'].value*K
        ALa = self.SPMModel.parameters['ALa'].value*K
        
        self.SPMModel.parameters['e'].value = ALo + 1.2*K
        e = self.SPMModel.parameters['e'].value
        self.SPMModel.parameters['RRe'].value = SRi-e
        RRe = self.SPMModel.parameters['RRe'].value
        
        self.SPMModel.parameters['TailleMailleEntrefer'].value = self.SPMModel.parameters['TailleMailleEntrefer'].value*K
        TailleMailleEntrefer = self.SPMModel.parameters['TailleMailleEntrefer'].value
        
        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                         Draw Rotor
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
        
        """ CALCULATION OF THE COORDINATES OF THE POINTS USED FOR THE CONSTRUCTION OF THE ROTOR  """
        
        """ calculation of the points defining the geometry of the magnets """
        RAngElec=2*pi/(Np*Nsp)											# angle P O M		
        
        """ draw rotor outer tube """        
        self.femm_wrapper.addnode(RRe,0)
        self.femm_wrapper.addnode(-(RRe),0)
        self.femm_wrapper.addarc(-(RRe),0,(RRe),0,180,0.2)
        self.femm_wrapper.addarc(RRe,0,-(RRe),0,180,0.2)
        
        self.femm_wrapper.selectnode(RRe,0)
        self.femm_wrapper.selectnode(-(RRe),0)
        self.femm_wrapper.setnodeprop('rotor',9)
        self.femm_wrapper.clearselected()
        
        self.femm_wrapper.selectarcsegment(0,RRe)
        self.femm_wrapper.selectarcsegment(0,-(RRe))
        MaxSegDeg=2*asin(TailleMaille/2/(RRe))*180/pi
        self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'rotor',0,9)
        self.femm_wrapper.clearselected()
                
        """ Point definition to build Magnets """
        # Definition of the point H
        RangVOH=(asin(ALa/2/RRe)*2)         				       # angle Ip O H
        RAngHOI=(RAngElec-RangVOH)   						       # angle Ip Origin H
        RAngYOH=(tan(ALa/2/RRe))
        
        # Definition of the point G
        RHx=-RRe*sin(RAngYOH/repetition)
        RHy=RRe*cos(RAngYOH/repetition)      
        
        # Definition of the point H
        RGx=RHx-ALo*sin(RAngYOH/repetition)
        RGy=RHy+ALo*cos(RAngYOH/repetition)
        
        
        # Definition of the point I
        RIx=-RRe*sin(RAngHOI/repetition)
        RIy=RRe*cos(RAngHOI/repetition)
        
        # Definition of the point J
        RJx=-(ALo+RRe)*sin(RAngHOI/repetition)
        RJy=(ALo+RRe)*cos(RAngHOI/repetition)

        # Block label coordinates
        RLabMagx = -(RRe+ALo/2)*sin(RAngElec/(2*repetition)-RangVOH/(2*repetition))
        RLabMagy = (RRe+ALo/2)*cos(RAngElec/(2*repetition)-RangVOH/(2*repetition))
       
        RAngMagDeg = ((tan(RLabMagx/RLabMagy))*180/pi)

        k=0
        for AngleDeg in np.arange(0,(360+Np)/repetition,360/(Np*repetition)):		
            Angle=AngleDeg*pi/180
            S=sin(Angle)
            C=cos(Angle)
            RHxrot = RHx*C-RHy*S
            RHyrot = RHx*S+RHy*C
            RIxrot = RIx*C-RIy*S
            RIyrot = RIx*S+RIy*C
            RGxrot = RGx*C-RGy*S
            RGyrot = RGx*S+RGy*C
            
            RJxrot = RJx*C-RJy*S
            RJyrot = RJx*S+RJy*C
            
            self.femm_wrapper.addnode(RHxrot,RHyrot)
            self.femm_wrapper.addnode(RGxrot,RGyrot)
            self.femm_wrapper.addnode(RIxrot,RIyrot)
            self.femm_wrapper.addnode(RJxrot,RJyrot)
            
            self.femm_wrapper.addsegment(RGxrot,RGyrot,RHxrot,RHyrot)
            self.femm_wrapper.addsegment(RIxrot,RIyrot,RJxrot,RJyrot)
            
            self.femm_wrapper.addarc(RGxrot,RGyrot,RJxrot,RJyrot,RAngHOI/repetition*180/pi,0.1)
            
            self.femm_wrapper.selectnode(RHxrot,RHyrot)
            self.femm_wrapper.selectnode(RGxrot,RGyrot)
            self.femm_wrapper.selectnode(RIxrot,RIyrot)
            self.femm_wrapper.selectnode(RJxrot,RJyrot)
            self.femm_wrapper.setnodeprop('aimants',3)
            self.femm_wrapper.clearselected()
            
            self.femm_wrapper.selectsegment((RGxrot+RHxrot)/2,(RGyrot+RHyrot)/2)
            self.femm_wrapper.selectsegment((RIxrot+RJxrot)/2,(RIyrot+RJyrot)/2)
            self.femm_wrapper.setsegmentprop('aimant',TailleMaille,1,0,3)
            self.femm_wrapper.clearselected()
            
            self.femm_wrapper.selectarcsegment (RHxrot,RHyrot)
            self.femm_wrapper.selectarcsegment (RGxrot,RGyrot)
            MaxSegDeg=2*asin(TailleMaille/2/RRe)*180/pi
            self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'aimant',0,3)
            self.femm_wrapper.clearselected()
        
        for AngleDeg in np.arange(0,360/repetition,360/(Np*repetition)):
            LabAngle=AngleDeg*pi/180
            S=sin(LabAngle)
            C=cos(LabAngle)
            RLabMagxrot = RLabMagx*C-RLabMagy*S
            RLabMagyrot = RLabMagx*S+RLabMagy*C
            
            self.femm_wrapper.addblocklabel(RLabMagxrot,RLabMagyrot)
            self.femm_wrapper.selectlabel(RLabMagxrot,RLabMagyrot)
            self.femm_wrapper.setblockprop('Sm2Co17',0,TailleMaille,0,AngleDeg+90*(-1)**k-RAngMagDeg,3,1)
            self.femm_wrapper.clearselected()
            k=k+1

        self.femm_wrapper.addblocklabel(-((RRe+RRi)/2)*sin(Angle/2),((RRe+RRi)/2)*cos(Angle/2))
        self.femm_wrapper.selectlabel(-((RRe+RRi)/2)*sin(Angle/2),((RRe+RRi)/2)*cos(Angle/2))
        self.femm_wrapper.setblockprop('FeSi 0.35mm',0,TailleMaille,0,0,9,1)
        self.femm_wrapper.clearselected()

        
        """ draw insider tube"""
        self.femm_wrapper.addnode(RRi,0)
        self.femm_wrapper.addnode(-(RRi),0)
        self.femm_wrapper.addarc(-(RRi),0,(RRi),0,180,0.2)
        self.femm_wrapper.addarc(RRi,0,-(RRi),0,180,0.2)
        self.femm_wrapper.selectnode(RRi,0)
        self.femm_wrapper.selectnode(-(RRi),0)
        self.femm_wrapper.setnodeprop('rotor',3)
        self.femm_wrapper.clearselected
        self.femm_wrapper.selectarcsegment(0,RRi)
        self.femm_wrapper.selectarcsegment(0,-(RRi))
        MaxSegDeg=2*asin(TailleMaille/2/(RRi))*180/pi
        self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'rotor',0,3)
        self.femm_wrapper.clearselected()
        """Draw Air gap"""
        self.femm_wrapper.addblocklabel(-(RRe+(ALo+e)/2)*sin(Angle/2),(RRe+(ALo+e)/2)*cos(Angle/2))
        self.femm_wrapper.selectlabel(-(RRe+(ALo+e)/2)*sin(Angle/2),(RRe+(ALo+e)/2)*cos(Angle/2))
        self.femm_wrapper.setblockprop('air',0,TailleMailleEntrefer,0,0,2,1)
        self.femm_wrapper.clearselected()
            

        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                         Draw air insde the Rotor
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
        MateriauTubeInterieur='air'
        self.femm_wrapper.clearselected()
        self.femm_wrapper.addblocklabel(-(RRi-TailleMaille)*sin(Angle/2),(RRi-TailleMaille)*cos(Angle/2))
        self.femm_wrapper.selectlabel(-(RRi-TailleMaille)*sin(Angle/2),(RRi-TailleMaille)*cos(Angle/2))
        self.femm_wrapper.setblockprop('air',0,2,0,0,1,1)
        self.femm_wrapper.clearselected() 

        """ Carrying out the cut """
        if repetition > 1:
            self.femm_wrapper.addnode(0,0)
            self.femm_wrapper.addnode(0,SRe)
            self.femm_wrapper.addnode(-SRe*sin(Angle),SRe*cos(Angle))
            
            self.femm_wrapper.addsegment(0,0,0,SRe)
            self.femm_wrapper.addsegment(0,0,-SRe*sin(Angle),SRe*cos(Angle))
            
            self.femm_wrapper.selectnode(RGxrot,RGyrot)
            self.femm_wrapper.selectnode(RHxrot,RHyrot)
            self.femm_wrapper.selectnode(RIxrot,RIyrot)
            self.femm_wrapper.selectnode(RJxrot,RJyrot)
            
            self.femm_wrapper.deleteselected()
            self.femm_wrapper.clearselected()
            
class Halbach_Model(BaseRotor):
    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Motor geometric variables definition (BLAC_parametres_geometrie)_SPM_HALBACH
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
    """ Form factor definition: (relative to the exterior stator rayon)"""
    SDe = Variable('SDe', 93.5, '[mm]', 'Exterior Stator diamter')
    SRe = Variable('SRe', SDe.value/2, '[mm]', 'Exterior Stator rayon')
    SRe_ref = Variable('SRe_ref', 120./2, '[mm]', 'Reference Exterior Stator rayon (From Parvex NX310)')
    K = Variable('K', SRe.value/SRe_ref.value, '[mm]', 'Form factor')
    ALo = Variable('ALo', 6, '[mm]', ' ')
    RRi = Variable('RRi', 27.99, '[mm]', 'Rotor interior radius')
    SRi = Variable('SRi', 39.33, '[mm]', 'Stator interior radius')
    J_den = Variable('J_den', 35.02, '[A/mm²]', 'Current density')
    SEt = Variable('SEt', 175.03, '[mm]', 'Motor Lenght')
    
    Npref = Variable('Npref', 10, '[Magnets]', 'Reference permanent magnet number')
    Np = Variable('Np', 10, '[Magnets]', 'Permanent magnet number')
    KNp = Variable('Knp', Np.value/Npref.value, '[-]', 'Coefficient ratio of the pole number')
    
    """ Definition of the Permanent Magnets geometry"""						  
    ALa = Variable('ALa', 0.3, '[mm]', 'Space between the magnets')
    
    """ Airgap definition"""
    e = Variable('e', ALo.value+1.2, '[mm]', 'Airgap thickness')
     
    """Definition of the geometry which supports the magnets (Rotor)"""
    RRe = Variable('RRe', SRi.value-e.value, '[mm]', 'Rotor exterior radius')
    
    Nsp = Variable('Nsp', 4, '[-]', 'Number of segment')
    
    """ Mesh Definition:"""
    TailleMailleEntrefer = Variable('TailleMailleEntrefer', 1.2/4, '[-]', 'Used for airgap material definition')
    TailleMaille = Variable('TailleMaille', 1.0, '[-]', 'Mesh size')
    TailleMailleJeu = Variable('TailleMailleJeu', 0.25, '[-]', 'Mesh size in the clearence')
    TailleMailleBobine= Variable('TailleMailleBobine', 1, '[-]', 'Mesh size for the winding')



    def __init__(self, motif='10/12', repetition='1', segmentation='1', Np=Np, SDe=SDe, SRe=SRe, SRe_ref=SRe_ref, K=K, ALo=ALo, RRi=RRi, SRi=SRi, J_den=J_den, SEt=SEt, ALa=ALa, 
                 e=e, RRe=RRe, Nsp=Nsp, TailleMailleEntrefer=TailleMailleEntrefer, TailleMaille=TailleMaille, 
                 TailleMailleJeu=TailleMailleJeu, TailleMailleBobine=TailleMailleBobine):
        
        super().__init__()

        self.motif = motif
        self.repetition = repetition
        self.segmentation = segmentation
        self.parameters[Np.name] = Np
        self.parameters[SDe.name] = SDe 
        self.parameters[SRe.name] = SRe
        self.parameters[SRe_ref.name] = SRe_ref
        self.parameters[K.name] = K
        self.parameters[ALo.name] = ALo
        self.parameters[RRi.name] = RRi
        self.parameters[SRi.name] = SRi
        self.parameters[J_den.name] = J_den
        self.parameters[SEt.name] = SEt
        self.parameters[ALa.name] = ALa
        self.parameters[e.name] = e
        self.parameters[RRe.name] = RRe
        self.parameters[Nsp.name] = Nsp
        self.parameters[TailleMailleEntrefer.name] = TailleMailleEntrefer
        self.parameters[TailleMaille.name] = TailleMaille
        self.parameters[TailleMailleJeu.name] = TailleMailleJeu
        self.parameters[TailleMailleBobine.name] = TailleMailleBobine

class Halbach_GeomGeneration(BaseRotor):

    def __init__(self, HalbachModel, femm_wrapper):
        
        self.HalbachModel =  HalbachModel
        self.femm_wrapper = femm_wrapper  

    def get_value(self,name):
        return self.HalbachModel.parameters[name].value
        
    def draw(self, stator):

        repetition = self.HalbachModel.repetition
        self.HalbachModel.parameters['SRe'].value = self.HalbachModel.parameters['SDe'].value/2
        SRe = self.HalbachModel.parameters['SRe'].value

        K = self.HalbachModel.parameters['K'].value
        
        self.HalbachModel.parameters['Np'].value = float(self.HalbachModel.motif.split('/')[0])
        Np = self.HalbachModel.parameters['Np'].value
        Nsp = self.HalbachModel.parameters['Nsp'].value
        self.HalbachModel.parameters['TailleMaille'].value = self.HalbachModel.parameters['TailleMaille'].value*K
        TailleMaille = self.HalbachModel.parameters['TailleMaille'].value
        ALo = self.HalbachModel.parameters['ALo'].value*K
        RRi = self.HalbachModel.parameters['RRi'].value*K
        SRi = self.HalbachModel.parameters['SRi'].value*K
        ALa = self.HalbachModel.parameters['ALa'].value*K
        
        self.HalbachModel.parameters['e'].value = ALo + 1.2*K
        e = self.HalbachModel.parameters['e'].value
        self.HalbachModel.parameters['RRe'].value = SRi-e
        RRe = self.HalbachModel.parameters['RRe'].value
        Ne = float(self.HalbachModel.motif.split('/')[1])
        self.HalbachModel.parameters['TailleMailleEntrefer'].value = self.HalbachModel.parameters['TailleMailleEntrefer'].value*K
        TailleMailleEntrefer = self.HalbachModel.parameters['TailleMailleEntrefer'].value
        
        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                 Draw Rotor
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """

        """ CALCULATION OF THE COORDINATES OF THE POINTS USED FOR THE CONSTRUCTION OF THE ROTOR """
        
        """ calculation of the points defining the geometry of the magnets """
        RAngElec=2*pi/(Np*Nsp)										# angle P O M		
        
        self.RAngElec=RAngElec
        
        """ Draw rotor outer tube  """
        self.femm_wrapper.addnode(RRe,0)
        self.femm_wrapper.addnode(-(RRe),0)
        self.femm_wrapper.addarc(-(RRe),0,(RRe),0,180,0.2)
        self.femm_wrapper.addarc(RRe,0,-(RRe),0,180,0.2)
        
        self.femm_wrapper.selectnode(RRe,0)
        self.femm_wrapper.selectnode(-(RRe),0)
        self.femm_wrapper.setnodeprop('rotor',9)
        self.femm_wrapper.clearselected()
        
        self.femm_wrapper.selectarcsegment(0,RRe)
        self.femm_wrapper.selectarcsegment(0,-(RRe))
        MaxSegDeg=2*asin(TailleMaille/2/(RRe))*180/pi
        self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'rotor',0,9)
        self.femm_wrapper.clearselected()
        
        """ Definition points for magnet construction """
        RangVOH=asin(ALa/2/RRe)*2								          # angle Ip O H
        RAngHOI=RAngElec-RangVOH									      # angle Ip Origin H
        RAngYOH=(tan(ALa/2/RRe))                                          # Angle Y axis O H  
        
        # Definition of the point G
        RHx=-RRe*sin(RAngYOH/repetition)
        RHy=RRe*cos(RAngYOH/repetition)      
        
        # Definition of the point H
        RGx=RHx-ALo*sin(RAngYOH/repetition)
        RGy=RHy+ALo*cos(RAngYOH/repetition)
        
        
        # Definition of the point I
        RIx=-RRe*sin(RAngHOI/repetition)
        RIy=RRe*cos(RAngHOI/repetition)
        
        # Definition of the point J
        RJx=-(ALo+RRe)*sin(RAngHOI/repetition)
        RJy=(ALo+RRe)*cos(RAngHOI/repetition)

        # Block label coordinates
        RLabMagx = -(RRe+ALo/2)*sin(RAngElec/(2*repetition)-RangVOH/(2*repetition))
        RLabMagy = (RRe+ALo/2)*cos(RAngElec/(2*repetition)-RangVOH/(2*repetition))
        
        RAngMagDeg = ((tan(RLabMagx/RLabMagy))*180/pi)
        
        k=90    
        AngleDep = 180/(Ne*repetition)+RAngMagDeg # Begining angle of the drawing (to align with the notch)
       
        for AngleDeg in np.arange (AngleDep,(360+AngleDep)/repetition,360/(Np*Nsp*repetition)):
            Angle=AngleDeg*pi/180
            S=sin(Angle)
            C=cos(Angle)
            RHxrot = RHx*C-RHy*S
            RHyrot = RHx*S+RHy*C
            RIxrot = RIx*C-RIy*S
            RIyrot = RIx*S+RIy*C
            RGxrot = RGx*C-RGy*S
            RGyrot = RGx*S+RGy*C
            RJxrot = RJx*C-RJy*S
            RJyrot = RJx*S+RJy*C
            
            self.femm_wrapper.addnode(RHxrot,RHyrot)
            self.femm_wrapper.addnode(RGxrot,RGyrot)
            self.femm_wrapper.addnode(RIxrot,RIyrot)
            self.femm_wrapper.addnode(RJxrot,RJyrot)
            
            self.femm_wrapper.addsegment(RGxrot,RGyrot,RHxrot,RHyrot)
            self.femm_wrapper.addsegment(RIxrot,RIyrot,RJxrot,RJyrot)
            
            self.femm_wrapper.addarc(RGxrot,RGyrot,RJxrot,RJyrot,RAngHOI/repetition*180/pi,1)
            
            self.femm_wrapper.selectnode(RHxrot,RHyrot)
            self.femm_wrapper.selectnode(RGxrot,RGyrot)
            self.femm_wrapper.selectnode(RIxrot,RIyrot)
            self.femm_wrapper.selectnode(RJxrot,RJyrot)
            self.femm_wrapper.setnodeprop('aimants',3)
            self.femm_wrapper.clearselected()
            
            self.femm_wrapper.selectsegment((RGxrot+RHxrot)/2,(RGyrot+RHyrot)/2)
            self.femm_wrapper.selectsegment((RIxrot+RJxrot)/2,(RIyrot+RJyrot)/2)

            self.femm_wrapper.setsegmentprop(TailleMaille, 'aimant',1,0,3)
            self.femm_wrapper.clearselected()
            
            self.femm_wrapper.selectarcsegment (RHxrot,RHyrot)
            self.femm_wrapper.selectarcsegment (RGxrot,RGyrot)
            MaxSegDeg=2*asin(TailleMaille/2/RRe)*180/pi
            self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'aimant',0,3)
            self.femm_wrapper.clearselected()
            
            RLabMagxrot = RLabMagx*C-RLabMagy*S
            RLabMagyrot = RLabMagx*S+RLabMagy*C

            self.femm_wrapper.addblocklabel(RLabMagxrot,RLabMagyrot)
            self.femm_wrapper.selectlabel(RLabMagxrot,RLabMagyrot)
            self.femm_wrapper.setblockprop('Sm2Co17',0,TailleMaille,0,AngleDeg+k-RAngMagDeg,3,1) 
            self.femm_wrapper.clearselected()
            
            k=k-45
        

        self.femm_wrapper.addblocklabel(-((RRe+RRi)/2)*sin(Angle/2),((RRe+RRi)/2)*cos(Angle/2))
        self.femm_wrapper.selectlabel(-((RRe+RRi)/2)*sin(Angle/2),((RRe+RRi)/2)*cos(Angle/2))
        self.femm_wrapper.setblockprop('FeSi 0.35mm',0,TailleMaille,0,0,9,1)
        self.femm_wrapper.clearselected()
        """ draw insider tuber"""
        self.femm_wrapper.addnode(RRi,0)
        self.femm_wrapper.addnode(-(RRi),0)
        
        self.femm_wrapper.addarc(-(RRi),0,(RRi),0,180,0.2)
        self.femm_wrapper.addarc(RRi,0,-(RRi),0,180,0.2)
        
        self.femm_wrapper.selectnode(RRi,0)
        self.femm_wrapper.selectnode(-(RRi),0)
        self.femm_wrapper.setnodeprop('rotor',3)
        self.femm_wrapper.clearselected
        self.femm_wrapper.selectarcsegment(0,RRi)
        self.femm_wrapper.selectarcsegment(0,-(RRi))
        MaxSegDeg=2*asin(TailleMaille/2/(RRi))*180/pi
        self.femm_wrapper.setarcsegmentprop(MaxSegDeg,'rotor',0,3)
        self.femm_wrapper.clearselected()
        
        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                         draw air inside the rotor
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
        MateriauTubeInterieur='air'
        self.femm_wrapper.clearselected()
        self.femm_wrapper.addblocklabel(-(RRi-TailleMaille)*sin(Angle/2),(RRi-TailleMaille)*cos(Angle/2))
        self.femm_wrapper.selectlabel(-(RRi-TailleMaille)*sin(Angle/2),(RRi-TailleMaille)*cos(Angle/2))
        self.femm_wrapper.setblockprop('air',0,2,0,0,1,1)
        self.femm_wrapper.clearselected() 
        
        """ Carrying out the cut """ # Drawing the needed segment for the cut
        if repetition > 1:
            self.femm_wrapper.addnode(0,0)
            self.femm_wrapper.addnode(0,SRe)
            self.femm_wrapper.addnode(0,RRe)
            self.femm_wrapper.addnode(0,SRi)
            self.femm_wrapper.addnode(-RRe*sin(360*pi/(repetition*180)),RRe*cos(360*pi/(repetition*180)))
            self.femm_wrapper.addnode(-SRi*sin(360*pi/(repetition*180)),SRi*cos(360*pi/(repetition*180)))
            self.femm_wrapper.addnode(-SRe*sin(360*pi/(repetition*180)),SRe*cos(360*pi/(repetition*180)))
            
            self.femm_wrapper.addsegment(0,0,0,RRe)
            self.femm_wrapper.addsegment(0,SRi,0,SRe)
            
            self.femm_wrapper.addsegment(0,0,-RRe*sin(360*pi/(repetition*180)),RRe*cos(360*pi/(repetition*180)))
            self.femm_wrapper.addsegment(-SRi*sin(360*pi/(repetition*180)),SRi*cos(360*pi/(repetition*180)),-SRe*sin(360*pi/(repetition*180)),SRe*cos(360*pi/(repetition*180)))