import femm
from math import pi, cos, sin, sqrt
import numpy as np
import time
start=time.time()
import motor

def compute(motor):
    # Stator variables
    K = motor.rotor.parameters['K'].value
    SRfe = motor.stator.parameters['SRfe'].value
    SEp = motor.stator.parameters['SEp'].value*K
    ACwind = motor.stator.parameters['ACwind'].value
    SPx = motor.stator.SPx
    SPy = motor.stator.SPy
    NbDemiEncoche = motor.stator.parameters['NbDemiEncoche'].value
    SK2Ix = motor.stator.SK2Ix
    SK2Iy = motor.stator.SK2Iy
    SAngElec = motor.stator.parameters['SAngElec']
    SUx = motor.stator.SUx
    SUy = motor.stator.SUy
    LRe = motor.rotor.parameters['SRe'].value*1.5
    Ne = motor.stator.parameters['Ne'].value
    k_w = motor.stator.parameters['k_w'].value
    SE_totale = motor.stator.SE_totale
    # Rotor variables
    SRe = motor.rotor.parameters['SRe'].value
    J_den = motor.rotor.parameters['J_den'].value
    Np = motor.rotor.parameters['Np'].value
    SRi = motor.rotor.parameters['SRi'].value*K
    SEt = motor.rotor.parameters['SEt'].value*K
    repetition = motor.rotor.repetition

    
    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            PROBLEM LIMIT MODELING (air around the motor) trace_LIMIT_PROBLEM
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
        
#    femm.mi_addboundprop('Mixed',0,0,0,0,0,0,1/(4*pi*1e-7)/100,0,8)
    femm.mi_addboundprop('Exterieur',0,0,0,0,0,0,0,0,0)
    femm.mi_addnode(LRe,0)		
    femm.mi_addnode(-LRe,0)
    femm.mi_addarc(LRe,0,-LRe,0,180,2)
    femm.mi_addarc(-LRe,0,LRe,0,180,2)
    femm.mi_addblocklabel((LRe+SRe)/2,0)
    femm.mi_selectlabel((LRe+SRe)/2,0)
    femm.mi_setblockprop('air',0,2,0,0,8,1)
    femm.mi_clearselected()
    femm.mi_selectarcsegment(0,LRe)
    femm.mi_selectarcsegment(0,-LRe)
    femm.mi_setarcsegmentprop(1,'Exterieur',1,8)
    femm.mi_clearselected()
    
    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                    Zoom + saving + troque caluclation
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
    
    femm.mi_zoomnatural()
    femm.mi_zoom(-SRe,-SRe,SRe,SRe)
    femm.mi_saveas('Moteur_BLAC.fem')
    femm.mi_seteditmode('group')
    femm.mi_createmesh()
    femm.mi_zoom(-1.05*SRe,-1.05*SRe,1.05*SRe,1.05*SRe)
    femm.mi_saveas('Moteur_BLAC.fem')  
    femm.mi_analyze(0)
    femm.mi_loadsolution()
    femm.mo_smooth('on')
    femm.mo_groupselectblock(1)
    femm.mo_groupselectblock(3)
    femm.mo_groupselectblock(9)
    torque22 = femm.mo_blockintegral(22)
    MatCouple=torque22
    #        print('Torque:',MatCouple)
    femm.mo_clearblock()
    femm.mo_clearcontour()
    
    
    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                        Iron losses calculation
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """ 
    """ Calcul des pertes Fer dans le moteur """
    
    omega=8400   # rpm 
    
    """ Calcul des aires de mesure de B """
    
    femm.mo_groupselectblock(5)
    S1=femm.mo_blockintegral(5)   # tooth area
    femm.mo_clearblock()
    
    femm.mo_groupselectblock(4)
    S2=femm.mo_blockintegral(5)   # breech area
    femm.mo_clearblock()
    
    P1x=0
    P1y=SRi+(SRfe-SRi)/2
    P2x=-(SRfe+SEp/2)*sin(SAngElec/(2*repetition))
    P2y=(SRfe+SEp/2)*cos(SAngElec/(2*repetition))
#    self.P1x = P1x
#    self.P1y = P1y
    A=0
    massevolumiquefer=7650    
    B_max=np.zeros(Ne)   # Calcul B max between B_breech and B_tooth; width vector=Ne; 
    u=0
    """ Measurement of B in each area around the engine """
    for AngleDeg in np.arange (0,360*repetition,360*repetition/Ne):
        Angle=AngleDeg*pi/180
        S=sin(Angle)
        C=cos(Angle)
            
        P1xrot=P1x*C-P1y*S
        P1yrot=P1x*S+P1y*C
        P2xrot=P2x*C-P2y*S
        P2yrot=P2x*S+P2y*C 
    
            
        femm.mi_addnode(P1xrot,P1yrot)
        femm.mi_addnode(P2xrot,P2yrot)
            
        femm.mi_selectnode(P1xrot,P1yrot)
        valeur1=femm.mo_getb(P1xrot,P1yrot)
        B1=(valeur1[0]**2+valeur1[1]**2)**.5
            
        femm.mi_selectnode(P2xrot,P2yrot);
        valeur2=femm.mo_getb(P2xrot,P2yrot);
        B2=(valeur2[0]**2+valeur2[1]**2)**.5
        Bm=max(B1,B2)
        B_max[u]=Bm
        u=u+1
        if (u < Ne+2):              #% (u < Ne+2) pour Ne different de 12
            k_adt=1                   # coeff tooth iron losses
            k_ady=1;                  # coeff breech iron losses
            A=A+(SEt*10**-3)*massevolumiquefer*(k_adt*B1**2*S1+k_ady*B2**2*S2)          
    
    #        print('Bmax:',np.max(B_max))
    
    m_ref_1=(SEt*10**-3)*massevolumiquefer*S1
    m_ref_2=(SEt*10**-3)*massevolumiquefer*S2
        
    """ ---------------Joule losses------------------ """
    
    BResistivite = 1.7241*1e-8         # [Ohm*m] 
    BS_cu= SE_totale* k_w              # surface Copper
    SE_slot=SE_totale
    
    S=sin(2*pi/Ne)
    C=cos(2*pi/Ne)
                
    if (ACwind == 1):
        P= sqrt(SPx**2+SPy**2)
        U= sqrt(SUx**2+SUy**2)
        SRslot_m= (P+U)/2
        L_end=2*pi*SRslot_m/Np                                               # Traction length inactive
        BVol_end= 2*BS_cu*L_end                                              # Winding volume inactive
        BVol_slot=SEt*BS_cu                                                  # Winding volume active
        BVol_tot = BVol_slot + BVol_end                                      # Winding volume [mm^3]                                      
            #P_Joule(1,Nind)  = 3*Ne/3*BResistivite*(BVol_tot*1e-9)*(J_den*(1/1e-6))^2
        P_Joule= 3*Ne/3*BResistivite*(BVol_tot*1e-9)*(J_den*(1/1e-6))**2
    #            print('Joule Losses:', P_Joule)
    elif (NbDemiEncoche == 0 ):
        SPxrot=SPx*C-SPy*S
        SPyrot=SPx*S+SPy*C
        SUxrot=SUx*C-SUy*S
        SUyrot=SUx*S+SUy*C
        SRslot_m=sqrt(SUxrot**2+SUyrot**2)
        BR_chignon=(SRslot_m*sin(pi/Ne))                                #R_Toroide
        Br_chignon=sqrt(BS_cu/pi)                                       #r-Toroide
        BVol_end=2*pi**2*BR_chignon*Br_chignon**2                       #Winding volume inactive
        BVol_slot=2*SEt*BS_cu                                           #Winding volume active
        BVol_tot = BVol_slot + BVol_end                                 #Winding volume [mm^3]
        P_Joule=3/2*Ne/3*BResistivite*(BVol_tot*1e-9)*(J_den*(1/1e-6))**2
    #            print('Joule Losses:', P_Joule)
    elif (NbDemiEncoche == 2):
        SRslot_m=sqrt(SK2Ix**2+SK2Iy**2)                             
        BR_chignon=(SRslot_m*sin(pi/Ne))                              #R_Toroide
        Br_chignon=sqrt(BS_cu/pi)                                     #r-Toroide
        BVol_end=2*pi**2*BR_chignon*Br_chignon**2                     #Winding volume inactive
        BVol_slot=2*SEt*BS_cu                                         #Winding volume active
        BVol_tot = BVol_slot + BVol_end                               #Winding volume [mm^3]
        #P_Joule(1,Nind)  = 3/2*Ne/3*BResistivite*(BVol_tot*1e-9)*(J_den*(1/1e-6))^2
        P_Joule=3/2*Ne/3*BResistivite*(BVol_tot*1e-9)*(J_den*(1/1e-6))**2
    #            print('Joule Losses:', P_Joule)
        
    """ ------------------------------------------- """
    
    """  Calcul fréquence rotation """
    freq_rot=omega/60                                                 # Hz
    freq_rot_rad=freq_rot*2*pi                                        #rad/s
    freq_mag=freq_rot*Np/2                                            # freq_mag=freq_rot*nb_paires_poles
    
    P_fer_50_1=1.25                                                   # Normelized Iron losses at 50Hz and 1 Tesla
    P_fer_femm=P_fer_50_1*(freq_mag/50)**1.5*A                        # calculated Iron losses   --- iron losses
    #        print('Iron Losses:', P_fer_femm)
    """ real torque [AK] """
    MatCouple_real=MatCouple - P_fer_femm/freq_rot_rad
    
    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                        Mass Calculation
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
        
    femm.mo_clearblock()
    
    """ masse cuivre """
    mv_Cu=8930                                  # Copper density mass [Kg/m3]
    femm.mo_groupselectblock(7)
    VCu_active = femm.mo_blockintegral(10)*k_w  # Volume activ part
    VCu_end = BVol_end*1e-9;                    # volume toroid
    if (ACwind == 1):
        VCu = VCu_active + Ne*VCu_end
    else:
        VCu = VCu_active + Ne/2*VCu_end
    
    # MCu(1,Nind)= VCu*mv_Cu                    # Copper Mass
    MCu= VCu*mv_Cu                              # Copper Mass
    femm.mo_clearblock()
    
    """ masse ferre """
    mv_Fe=7650;                                 # Iron density mass [Kg/m3]
    femm.mo_groupselectblock(9)
    femm.mo_groupselectblock(6)
    femm.mo_groupselectblock(4)
    femm.mo_groupselectblock(5)
    VFe = femm.mo_blockintegral(10)             # Iron volume
    # MFe(1,Nind)= VFe*mv_Fe      # masse fer
    MFe= VFe*mv_Fe                              # Iron Mass
    femm.mo_clearblock()
    
    """ masse aimants """
    mv_Sm=8300                                  # Magnets density mass [Kg/m3]
    femm.mo_groupselectblock(3)
    VSm = femm.mo_blockintegral(10)             # Magnets volume
    #MSm(1,Nind)= VSm*mv_Sm                     # Magnets mass
    MSm= VSm*mv_Sm                              # Magnets mass
    femm.mo_clearblock()
    
    """ masse resine """
    mv_Re=1200                 # Resin density mass [Kg/m3]
    VRe = VCu*(1-k_w)          # Resin volume
    MRe= VRe*mv_Re             # Resin mass
    
    #    M_Cu=8400*12*(SE_slot*k_w*SEt+pi**2*0.5754*SDe/2*sin(pi/12)*SE_slot/pi)     # Copper Mass [kg]
    #    MFe_S=7650*(pi*((SDe/2)**2-SRi**2)-12*SE_slot)*SEt                          # Iron stator mass [kg]
    #    MFe_R=7650*(pi*(RRe**2-RRi**2)-10*(RRe-RRi)*ALa)*SEt                        # Iron rotor mass [kg]
    #    MPM=8300*ALa*10*(0.88*RRe-RRi)*SEt                                          # Magnets mass [kg]
    #    M_mot=MCu+MFe_S+MFe_R+MPM                                                   # Motor Mass [kg]
    
    Mtot= MCu+MFe+MSm+MRe                                                            # Motor Mass
    #        print('Mass:',Mtot)
            
    end=time.time()
    computation_time = end - start
    #        print('Computation time:\n',Computation,'s')
    
    return MatCouple, B_max, P_Joule, P_fer_femm, Mtot, computation_time