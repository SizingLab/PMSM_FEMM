# -*-mode: python; py-indent-offset: 4; tab-width: 8; coding: utf-8 -*-
'''
Created on 8 mars 2022

@author: arthur.piat
'''

from femm import doargs, callfemm
import logging
from .femm_abstract_wrapper import AbstractFEMMWrapper

LOGGER = logging.getLogger()


class ThermalFEMMWrapper(AbstractFEMMWrapper):
    TH_BOUND_NAMES = ["Fixed_temperature", "Heat_flux", "Convection_bound",
                  "Radiation_bound", "Periodic", "Anti_periodic"]
    DENSITY_PLOT_TH = ["temp", "Fmag", "Gmag"]
    TH_BOUND_KEYS = ["Bound_name", "BdryFormat", "Tset", "Qs", "Tinf", "H", "Beta"]
                       
    def __init__(self):
        self.pb_type = self.THERMAL_PROBLEM_TYPE
    
    def addmaterial(self, matname, kx=0, ky=0, qv=0, kt=0):
        """
        adds a new material with called "materialname" with the material properties:
        kx Thermal conductivity in the x- or r-direction.
        ky Thermal conductivity in the y- or z-direction.
        qv Volume heat generation density in units of W/m3
        kt Volumetric heat capacity in units of MJ/(m3*K)
        """
        args = [matname, kx, ky, qv, kt]
        callfemm('hi_addmaterial' + doargs(*args))
    
    def addboundprop(self, Bound_name, BdryFormat="Fixed_temperature", Tset=0, qs=0, Tinf=0, H=0, Beta=0):
        '''
        list of boundaries conditions:
        ["Fixed_temperature", "Heat_flux", "Convection_bound", "Radiation_bound", "Periodic", "Anti_periodic"]
        to get the wanted boundary condition, set BdryFormat to any values above and give the following Keys arguments:

        For a “Fixed Temperature” type boundary condition, set the Tset parameter to the desired temperature.
        For a “Heat Flux” type boundary condition, set qs to be the heat flux density.
        For a convection boundary condition, set h to the desired heat transfer coefficient and Tinf to the desired external temperature.
        For a Radiation boundary condition, set beta equal to the desired emissivity and Tinf to the desired external temperature.
        For a “Periodic” boundary condition, just set BdryFormat to "Periodic"
        For an “Anti-Perodic” boundary condition, s just set BdryFormat to "Anti_Periodic
        '''
        self._steered_run("addboundprop", self.PREPROCES, Bound_name, self.TH_BOUND_NAMES.index(BdryFormat), Tset, qs, Tinf, H, Beta)
        
    def addtkpoint(self, materialname, T, k):
        """
        adds the point (T,k) to the thermal conductivity vs. temperature curve
        for the material specified by "materialname".
        """
        self._steered_run("addtkpoint", self.PREPROCES, materialname, T, k)
    
    def addconductorprop(self, conductorname, Tc=0, qc=0):
        """
        adds a new conductor property with name "conductorname" with either a 
        prescribed temperature or a prescribed total heat flux. 
        """
        if Tc == 0 and qc == 0:
            raise Exception("Tc and qc cannot be both null")
        elif Tc != 0 and qc == 0:
            self._steered_run("addconductorprop", self.PREPROCES, conductorname, Tc, 0, 1)
        elif Tc == 0 and qc != 0:
            self._steered_run("addconductorprop", self.PREPROCES, conductorname, 0, qc, 0)
        else:
            raise Exception("Tc and qc cannot be both given a value")
        
    def showdensityplot(self, upper_B, lower_B, type_plot, legend=True, grey_scale=False):
        super(ThermalFEMMWrapper, self).__init__(upper_B, lower_B, type_plot, legend, grey_scale)
        args = [self.legend_index, self.gscale, self.DENSITY_PLOT_TH.index(type), upper_B, lower_B]
        self._steered_run("showdensityplot", self.POSTPROCES, *args)


    def setnodeprop(self, propname, groupno, inconductor="<None>"):

        """
        Set the selected nodes to have
        the nodal property "propname" and group number groupno. The "inconductor" string
        specifies which conductor the node belongs to. If the node doesn’t belong to a named
        conductor, this parameter can be set to "<None>".
        """

        self._steered_run("setnodeprop", self.PREPROCES, propname, groupno, inconductor)


    def setsegmentprop(self, elementsize, propname, group, inconductor="<None>", hide=False, automesh=1):
        '''
        Set the selected arc segments to:
        Meshed with elements that span at most maxsegdeg degrees per element Boundary property "propname"
        hide: False = not hidden in post-processor, True == hidden in post processor
        A member of group number group
        '''
        if hide:
            hide_index = 1
        else:
            hide_index = 0
        self._steered_run("setsegmentprop", self.PREPROCES, propname, elementsize, automesh, hide_index, group,
                          inconductor)

    def setblockprop(self, blockname, automesh, meshsize, group):
        """
        Set the selected block labels to have
        the properties: Block property "blockname".
        automesh: 0 = mesher defers to mesh size constraint defined in meshsize, 1 = mesher
        automatically chooses the mesh density. meshsize: size constraint on the mesh in the
        block marked by this label. A member of group number group
        """
        self._steered_run("setblockprop", self.PREPROCES, blockname, automesh, meshsize, group)
