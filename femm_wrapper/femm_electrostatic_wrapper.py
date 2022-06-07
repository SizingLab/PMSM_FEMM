# -*-mode: python; py-indent-offset: 4; tab-width: 8; coding: utf-8 -*-
'''
Created on 8 mars 2022

@author: arthur.piat
'''

from femm import doargs, callfemm
import logging
from femm_abstract_wrapper import AbstractFEMMWrapper

LOGGER = logging.getLogger()


class ElectroFEMMWrapper(AbstractFEMMWrapper):
    ES_BOUND_NAMES = ["Fixed_Voltage", "Mixed", "Surface_Charge_Density"]
    ES_BOUND_KEYS = ["Bound_name", "BdryFormat", "Vs", "qs", "c0", "c1"]
        
    def __init__(self):
        self.pb_type = self.ELECTROSTAT_PROBLEM_TYPE
    
    def addmaterial(self, matname, qv = 0, ex = 0, ey = 0):
        args = [matname, ex, ey, qv]
        callfemm('ei_addmaterial' + doargs(*args))
    
    def addboundprop(self, Bound_name, BdryFormat = "Fixed_Voltage", Vs = 0, qs = 0, c0 = 0, c1 = 0):
        self._steered_run("addboundprop", self.PREPROCES, Bound_name, Vs, qs, c0, c1, self.ES_BOUND_NAMES.index(BdryFormat))
        
    def addconductorprop(self, conductorname, Vc = 0, qc = 0):
        """
        adds a new conductor property with name ’conductorname’ with 
        either a prescribed voltage or a prescribed total charge
        """
        
        if Vc == 0 and qc == 0:
            self._steered_run("addconductorprop", self.PREPROCES,
                          conductorname, 0, 0, 1)
        elif Vc != 0 and qc == 0:
            self._steered_run("addconductorprop", self.PREPROCES, conductorname, Vc, 0, 1)
        elif Vc == 0 and qc != 0:
            self._steered_run("addconductorprop", self.PREPROCES, conductorname, 0, qc, 0)
        else:
            raise Exception("Vc and qc cannot be both given a value")
    
    def movetranslate(self, dx, dy):
        """distance by which the selected objects are shifted."""
        self._steered_run("movetranslate", self.PREPROCES, dx, dy)
        
    def movetranslate2(self, dx, dy, editaction):
        self._steered_run("movetranslate2", self.PREPROCES, dx, dy, editaction)

