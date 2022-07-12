from stator import Concentrated
from rotor import IPM_Model, IPM_GeomGeneration, SPM_Model, SPM_GeomGeneration, Halbach_Model ,Halbach_GeomGeneration
import numpy as np
from computation import compute

import pandas as pd

class PM_motor:

### (Aurélien) Découpage du rotor_type en rotor_model et rotor_geomgeneration pour le draw

    def __init__(self, femm_wrapper, rotor_model, rotor_geomgeneration, stator_type, motif, repetition):
        
        self.motif = motif
        self.repetition = repetition
        ### (Aurélien) Ajout du femm_wrapper en attribut

        self.femm_wrapper = femm_wrapper

#       self.segmentation = segmentation
        
        if rotor_model == 'IPM':
            self.rotor = IPM_Model(motif=self.motif, repetition=self.repetition)
            self.rotor_geomgeneration = IPM_GeomGeneration(self.rotor, self.femm_wrapper)
        elif rotor_model == 'SPM':
            self.rotor = SPM_Model(motif=self.motif, repetition=self.repetition)
            self.rotor_geomgeneration = SPM_GeomGeneration(self.rotor, self.femm_wrapper)
        elif rotor_model == 'Halbach':
            self.rotor = Halbach_Model(motif=self.motif, repetition=self.repetition)
            self.rotor_geomgeneration = Halbach_GeomGeneration(self.rotor, self.femm_wrapper)
        else: 
            raise TypeError('Unknown rotor type')
        
### (Aurélien) Ajout de rotor_model a la place de rotor_type

        if stator_type == 'concentrated':
            self.stator = Concentrated(femm_wrapper=self.femm_wrapper, rotor_model=rotor_model, motif=self.motif, repetition=self.repetition)
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

### (Aurélien) Changement en rotor_geomgeneration
        self.rotor_geomgeneration.draw(stator)
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

