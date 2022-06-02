from stator import Concentrated
from rotor import IPM, SPM, Halbach
import numpy as np
from computation import compute

import pandas as pd

### (Aurélien) Rajouter une focntion execute_model pour le openfemm etc...
### Pour générer un modèle magnétique -> à utiliser dans le main

class PM_motor:
    
    def __init__(self, femm_wrapper, rotor_type, stator_type, motif, repetition):
        
        self.motif = motif
        self.repetition = repetition
        ### Ajout du femm_wrapper en attribut

        self.femm_wrapper = femm_wrapper

#        self.segmentation = segmentation
        
        if rotor_type == 'IPM':
            self.rotor = IPM(femm_wrapper=self.femm_wrapper, motif=self.motif, repetition=self.repetition)
        elif rotor_type == 'SPM':
            self.rotor = SPM(femm_wrapper=self.femm_wrapper, motif=self.motif, repetition=self.repetition)
        elif rotor_type == 'Halbach':
            self.rotor = Halbach(femm_wrapper=self.femm_wrapper, motif=self.motif, repetition=self.repetition)
        else: 
            raise TypeError('Unknown rotor type')
                
        if stator_type == 'concentrated':
            self.stator = Concentrated(femm_wrapper=self.femm_wrapper, rotor_type=rotor_type, motif=self.motif, repetition=self.repetition)
        else: 
            raise TypeError('Unknown stator type')

        self.data_frame = pd.DataFrame()
        
    def get_rotor(self):
        return self.rotor
        
    def get_stator(self):
        return self.stator
    
    def get_motif(self):
        return self.motif
    
    def get_repetition(self):
        return self.repetition
    
    def draw(self):
        stator=self.stator
        self.stator.draw_preliminary()
        self.rotor.draw(stator)
        self.stator.draw()
        
    def compute(self):
        MatCouple, B_max, P_Joule, P_fer_femm, Mtot, computation_time = compute(self)

        n = self.get_repetition()
        
        self.Torque  = n*MatCouple
        self.B_max = np.max(n*B_max)
        self.P_Joule = n*P_Joule
        self.P_fer_femm = n*P_fer_femm
        self.Mtot = n*Mtot
        self.computation_time = computation_time


    def print(self):
        print('Torque:', self.Torque)
        print('Bmax:', self.B_max)
        print('Joule Losses:', self.P_Joule)
        print('Iron Losses:', self.P_fer_femm)
        print('Mass:', self.Mtot)
        print('Computation time:\n', self.computation_time, ' s')

    def __str__(self):
        s = ''
        s = 'Parameters of the motor: \n'
        s += self.rotor.__str__()
        s += self.stator.__str__()
        return s

    def print_variables(self):

        self.data_frame.append(self.rotor.data_frame)
        self.data_frame.append(self.stator.data_frame)

