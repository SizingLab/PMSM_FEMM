# -*-mode: python; py-indent-offset: 4; tab-width: 8; coding: utf-8 -*-
'''
Created on 8 mars 2022

@author: arthur.piat
'''

from femm import doargs, callfemm, mi_addcircprop
import logging
from .femm_abstract_wrapper import AbstractFEMMWrapper

LOGGER = logging.getLogger()


class MagneticFEMMWrapper(AbstractFEMMWrapper):
    MAG_BOUND_NAMES = ["Prescribed_a", "Small_skin_depth", "Mixed", "Strategic_dual_image",
                   "Periodic", "Anti_periodic", "Periodic_air_gap", "Anti_periodic_air_gap"]
    DENSITY_PLOT_MAG = ["mag", "real", "imag", "jreal", "jmag"]
    MAG_BOUND_KEYS = ["Bound_name", "A0", "A1", "A2", "Phi", "Mu", "Sig", "C0", "C1",
                  "BdryFormat", "Ia", "Oa"]
    MAG_BOUND_NAMES = ["Prescribed_a", "Small_skin_depth", "Mixed", "Strategic_dual_image",
                   "Periodic", "Anti_periodic", "Periodic_air_gap", "Anti_periodic_air_gap"]
    
    def __init__(self):
        self.pb_type = self.MAGNETIC_PROBLEM_TYPE

    def addcircprop(self, circuit_name, current, circuit_type):
        """
        addcircprop(’circuitname’, current, circuit_type) adds a new circuit property with name ’circuitname’
        with the given current.
        The circuittype parameter is 0 for a parallel-connected circuit and 1 for a series-connected circuit.
        """
        mi_addcircprop(circuit_name, current, circuit_type)
        
    def probdef(self, units, type_pb, depth, precision = 1.e-7, minangle = 30, freq = 0, acsolver = None):
        
        """
        -The acsolver parameter specifies which solver is to be used for AC problems: 0 for successive approximation, 1 for Newton.
        -Set freq to the desired frequency in Hertz. (only for magnetical problems)
        """
        args = [freq, units, type_pb, precision, depth, minangle]
        if acsolver is not None:
            args.append(acsolver)
        callfemm('mi_probdef' + doargs(*args))

    def setprevious(self, filename, type_previous):
    
        """
        filename,prevtype) defines the previous solution to be used as the basis for an AC incremental 
        permeability or frozen permeability solution. The prevtype field is an integer that 
        specifies whether the solution is to be incremental permeability (1) or frozen permeability (2)
        . The filename should include the .ans extension, e.g. mi_setprevious(’mymodel.ans’,1)
        """
        if filename.endswith(".ans"):
            self._steered_run("setprevious", self.PREPROCES, filename, type_previous)
        else:
            raise IOError('filename arg must end with ".ans"')

    def setcurrent(self, circuit_name, current):
        self._steered_run("setcurrent", self.PREPROCES, circuit_name, current)
    
    def addmaterial(self, matname, mu_x = 0, mu_y = 0, Hc = 0, J = 0, Cduct = 0, Lam_d = 0, Phi_hmax = 0, lam_fill = 1.,
                LamType = 0, Phi_hx = 0, Phi_hy = 0, nstr = None, dwire = None):
        """
        mi_addmaterial(’matname’, mu x, mu y, H c, J, Cduct, Lam d, Phi hmax, lam fill, LamType, Phi hx, Phi hy, nstr, dwire) adds a 
        new material with called ’matname’ with the material properties:
        - mu x Relative permeability in the x- or r-direction.
        – mu y Relative permeability in the y- or z-direction.
        – H c Permanent magnet coercivity in Amps/Meter.
        – J Applied source current density in Amps/mm2.
        – Cduct Electrical conductivity of the material in MS/m.
        – Lam d Lamination thickness in millimeters.
        – Phi hmax Hysteresis lag angle in degrees, used for nonlinear BH curves.
        10
        – Lam fill Fraction of the volume occupied per lamination that is actually filled with iron (Note that this parameter defaults to 1 in the femm_api preprocessor dialog box because, by default, iron completely fills the volume)
        – Lamtype Set to
                            ∗ 0 – Not laminated or laminated in plane
                            ∗ 1 – laminated x or r
                            ∗ 2 – laminated y or z
                            ∗ 3 – magnet wire
                            ∗ 4 – plain stranded wire
                            ∗ 5 – Litz wire
                            ∗ 6 – square wire
        – Phi hx Hysteresis lag in degrees in the x-direction for linear problems.
        – Phi hy Hysteresis lag in degrees in the y-direction for linear problems.
        – nstr Number of strands in the wire build. Should be 1 for Magnet or Square wire.
        – dwire Diameter of each of the wire’s constituent strand in millimeters.
        """
        args = [matname, mu_x, mu_y, Hc, J, Cduct, Lam_d, Phi_hmax, lam_fill, LamType, Phi_hx, Phi_hy]
        if nstr is not None:
            args.append(nstr)
        elif (nstr is None) and (dwire is not None):
            args.append(1)
            args.append(dwire)
        elif (nstr is not None) and (dwire is not None):
            args.append(nstr)
            args.append(dwire)
        callfemm('mi_addmaterial' + doargs(*args))
        
    def addbhpoint(self, matname, bpoint, hpoint):
        
        self._steered_run("addbhpoint", self.PREPROCES, matname, bpoint, hpoint)
        
    def addboundprop(self, Bound_name, BdryFormat = "Prescribed_a", A0 = 0, A1 = 0,
                         A2 = 0, Phi = 0, Mu = 0, Sig = 0, C0 = 0, C1 = 0, Ia = 0, Oa = 0):
        '''
        list of boundaries conditions:
        ["Prescribed_a", "Small_skin_depth", "Mixed", "Strategic_dual_image", "Periodic" , "Anti_periodic", "Periodic_air_gap", "Anti_periodic_air_gap"]
        to get the wanted boundary condition, set BdryFormat to any values above and give the following Keys arguments:
                       
        For a “Prescribed A” type boundary condition, set the A0, A1, A2 and Phi parameters as required.
        For a “Small Skin Depth” type boundary condition, set the Mu to the desired relative permeability and Sig to the desired conductivity in MS/m.
        For a “Mixed” type boundary condition, set C1 and C0 as required.
        For a “Strategic dual image” , just set BdryFormat to "Strategic_dual_image"
        For a “Periodic”, just set BdryFormat to "Periodic"
        For an “Anti-Periodic”,  just set BdryFormat to ""Anti_Periodic"
        For a “Periodic Air Gap”, specify ia and oa, respectively the inner and outer boundary angles.
        For an “Anti-periodic Air Gap”,the same ia and oa parameters also apply here.”
        '''            
        self._steered_run("addboundprop", self.PREPROCES, Bound_name, A0, A1, A2, Phi, Mu, Sig, C0,
                          C1, self.MAG_BOUND_NAMES.index(BdryFormat), Ia, Oa)
                       
    def setblockprop(self, blockname, automesh, meshsize, incircuit, magdir, group, turns):
        '''Set the selected block labels to have the properties: Block property ’blockname’.
        automesh: 0 = mesher defers to mesh size constraint defined in meshsize, 1 = mesher automatically chooses the mesh density.
        meshsize: size constraint on the mesh in the block marked by this label. A member of group number group
        blockname is a member of the circuit named ’incircuit’
        The magnetization is directed along an angle in measured in degrees denoted by the parameter magdir
        The number of turns associated with this label is denoted by turns.
        '''
        self._steered_run("setblockprop", self.PREPROCES, blockname, automesh, meshsize, incircuit, magdir, group, turns)
    
    def setarcsegmentprop(self, maxsegdeg, propname, group, hide = False):
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
        self._steered_run("setarcsegmentprop", self.PREPROCES, maxsegdeg, propname, hide_index, group)
    
    def setsegmentprop(self, elementsize, propname, group, hide = False, automesh = 1):
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
        self._steered_run("setsegmentprop", self.PREPROCES, propname, elementsize, automesh, hide_index, group)
            
    def getcircuitproperties(self, circuit):
        """
        Used primarily to obtain impedance information associated with circuit properties. Properties are returned
        for the circuit property named ’circuit’. Six values are returned by the function. In order, these parameters are:
        – current Current carried by the circuit.
        – volts Voltage drop across the circuit in the circuit.
        – flux Circuit’s flux linkage
        """
        results = self._steered_run("getcircuitproperties", self.POSTPROCES, circuit)
        output = {'current': results[0], 'vdrop': results[1], 'flux_linkage': results[2],
                                   'power': results[1] * results[0]}
        return output

    def showdensityplot(self, upper_B, lower_B, type_plot, legend = True, grey_scale = False):
        super(MagneticFEMMWrapper, self).__init__(upper_B, lower_B, type_plot, legend, grey_scale)
        args = [self.legend_index, self.gscale, self.upper_B, self.lower_B, self.DENSITY_PLOT_MAG.index(self.type_plot)]
        self._steered_run("showdensityplot", self.POSTPROCES, *args)
        
    def movetranslate(self, dx, dy):
        """distance by which the selected objects are shifted."""
        self._steered_run("movetranslate", self.PREPROCES, dx, dy)
        
    def movetranslate2(self, dx, dy, editaction):
        self._steered_run("movetranslate2", self.PREPROCES, dx, dy, editaction)

    ### Nouvelle fonction à aussi rajouter dans les autres wrapper (pb avec l'abstract)

    def setnodeprop(self, propname, groupno):
        """
        Set the selected nodes to have the nodal
        property "propname" and group number groupno.
        """
        self._steered_run("setnodeprop", self.PREPROCES, 'propname', groupno)

    def getb(self, x, y):
        """
        Get the magnetic flux density associated with the point at (x,y). The return
        value is a list with two elements representing Bx and By for planar problems and Br and Bz for
        axisymmetric problems.
        """
        self._steered_run("getb", self.POSTPROCES, x, y)