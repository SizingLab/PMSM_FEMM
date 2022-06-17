# -*-mode: python; py-indent-offset: 4; tab-width: 8; coding: utf-8 -*-
'''
Created on 8 mars 2022

@author: arthur.piat
'''

from femm import doargs, callfemm, mi_drawarc, mi_drawline, mi_drawrectangle, mi_addcircprop, openfemm, newdocument, \
    mi_addbhpoint, mi_drawarc, hi_drawarc, closefemm, opendocument
import femm
import logging

LOGGER = logging.getLogger()


class AbstractFEMMWrapper(object):
    PREPROCES = 'preprocessing'
    POSTPROCES = "postprocessing"
    MAGNETIC_PROBLEM_TYPE = "magnetic"
    THERMAL_PROBLEM_TYPE = "heatflow"
    ELECTROSTAT_PROBLEM_TYPE = "electrostatic"
    PROBLEMS_INDEXES = {
        MAGNETIC_PROBLEM_TYPE: {'index': 0, 'suffix': "m"},
        ELECTROSTAT_PROBLEM_TYPE: {'index': 1, 'suffix': 'e'},
        THERMAL_PROBLEM_TYPE: {'index': 2, 'suffix': "h"}}
    AVAILABLE_PB_TYPES = PROBLEMS_INDEXES.keys()

    def __init__(self):
        self.pb_type = None
        raise NotImplementedError()

    def _steered_run(self, func_name, process_phase, *args, **kwargs):
        """
        generic wrapper to execute all femm function
        :param func_name: name of the function to be coded
        :param pb_type: type of FE problem considered
        :param process_phase: current use case : preprocessing or postprocessing
        and associated args and kwargs for function func_name
        """
        suffix = self.PROBLEMS_INDEXES[self.pb_type]['suffix']
        if process_phase == self.PREPROCES:
            suffix += 'i_'
        elif process_phase == self.POSTPROCES:
            suffix += 'o_'
        final_name = suffix + func_name
        return self.__execute(final_name, *args, **kwargs)

    def __execute(self, func_name, *args, **kwargs):
        """Executes a fem function called "func_name" with arguments args & kwargs
        :return: outputs arg & kwargs of used function
        :rtype: various
        """

        method = getattr(femm, func_name)
        try:
            return method(*args, **kwargs)
        except Exception as e:
            LOGGER.error("Failed to execute femm_api function " + str(func_name) +
                         "with arguments " + str(args) + " and kwargs " +
                         str(kwargs))
            LOGGER.error("Recevied message : " + str(e))
            raise

    def open_femm(self, hide=True):
        if hide:
            index_hide = 1
        else:
            index_hide = 0
        openfemm(index_hide)

    def close_femm(self):
        closefemm()

    def open_document(self, file_name):
        opendocument(file_name)

    def new_document(self):
        newdocument(self.PROBLEMS_INDEXES[self.pb_type]['index'])

    def probdef(self, units, type_pb, depth, precision=1e-8, minangle=30):

        """
        probdef changes the problem definition.
    
        -The units parameter specifies the units used for measuring length in the problem domain.
         Valid ’units’ entries are ’inches’, ’millimeters’, ’centimeters’, ’mils’, ’meters’, and ’micrometers’.
        -Set the parameter problemtype to ’planar’ for a 2-D planar problem, or to ’axi’ for an axisymmetric problem.
        -The precision parameter dictates the precision required by the solver. For example, entering 1E-8
        requires the RMS of the residual to be less than 10−8.
        -A fifth parameter, representing the depth of the problem in the into-the-page direction
        for 2-D planar problems. Specify the depth to be zero for axisymmetric problems.
        -The sixth parameter represents the minimum angle constraint sent to the mesh generator – 30 degrees is the usual choice for this parameter.
        """
        self._steered_run("probdef", self.PREPROCES, units, type_pb, precision, depth, minangle)

    def getmaterial(self, materialname):
        self._steered_run("getmaterial", self.PREPROCES, materialname)

    def addmaterial(self):
        raise NotImplementedError()

    def addboundprop(self):
        raise NotImplementedError()

    def drawarc(self, x1, y1, x2, y2, angle, maxseg):
        """
        Adds nodes at (x1,y1) and (x2,y2) and adds an arc of the
        specified angle and discretization connecting the nodes
        pb_type define the problem discipline
        """
        self._steered_run("drawarc", self.PREPROCES, x1, y1, x2, y2, angle, maxseg)

    def addarc(self, x1, y1, x2, y2, angle, maxseg):
        """
        Add a new arc segment from the nearest node to (x1,y1) to the nearest
        node to (x2,y2) with angle ‘angle’ divided into ‘maxseg’ segments
        pb_type define the problem discipline
        """
        self._steered_run("addarc", self.PREPROCES, x1, y1, x2, y2, angle, maxseg)

    def drawrectangle(self, x1, y1, x2, y2):
        """
        Adds nodes at the corners of a rectangle defined by the points (x1,y1) and 
        (x2,y2), then adds segments connecting the corners of the rectangle.
        """
        self._steered_run("drawrectangle", self.PREPROCES, x1, y1, x2, y2)

    def drawline(self, x1, y1, x2, y2):
        """
        Adds nodes at (x1,y1) and (x2,y2) and adds a line between the nodes
        pb_type define the problem discipline
        """
        self._steered_run("drawline", self.PREPROCES, x1, y1, x2, y2)

    def addsegment(self, x1, y1, x2, y2):
        """
        Add a new line segment from node closest to (x1,y1) to node closest to (x2,y2)
        pb_type define the problem discipline
        """
        self._steered_run("addsegment", self.PREPROCES, x1, y1, x2, y2)

    def addblocklabel(self, x, y):
        """
        Add a new block label at (x,y)
        pb_type define the problem discipline
        """
        self._steered_run("addblocklabel", self.PREPROCES, x, y)

    def selectlabel(self, x, y):
        """
        Select the label closet to (x,y). Returns the coordinates of the selected label.
        pb_type define the problem discipline
        """
        return self._steered_run("selectlabel", self.PREPROCES, x, y)

    def setblockprop(self, blockname, automesh=1, meshsize=0, group=0):
        '''Set the selected block labels to have the properties: Block property ’blockname’.
        automesh: 0 = mesher defers to mesh size constraint defined in meshsize, 1 = mesher automatically chooses the mesh density.
        meshsize: size constraint on the mesh in the block marked by this label. A member of group number group
        '''
        self._steered_run("setblockprop", self.PREPROCES, blockname, automesh, meshsize, group)

    def selectarcsegment(self, x, y):
        '''Select the arc segment closest to (x,y)'''
        self._steered_run("selectarcsegment", self.PREPROCES, x, y)

    def selectsegment(self, x, y):
        '''Select the line segment closest to (x,y)'''
        self._steered_run("selectsegment", self.PREPROCES, x, y)

    def selectnode(self, x, y):
        '''Select the node closest to (x,y). Returns the coordinates of the selected node'''
        return self._steered_run("selectnode", self.PREPROCES, x, y)

    def selectrectangle(self, x1, y1, x2, y2, editmode):
        """
        selects objects within a rectangle defined by points (x1,y1) and (x2,y2). If no 
        editmode parameter is supplied, the current edit mode is used. If the editmode 
        parameter is used, 0 denotes nodes, 2 denotes block labels, 2 denotes segments, 
        3 denotes arcs, and 4 specifies that all entity types are to be selected.
        """
        self._steered_run("selectrectangle", self.PREPROCES, x1, y1, x2, y2, editmode)

    def selectcircle(self, x, y, R, editmode):
        """
        selects objects within a circle of radius R centered at (x,y). If only x, y, and R parameters 
        are given, the current edit mode is used. If the editmode parameter is used, 0 denotes nodes, 
        1 denotes block labels, 2 denotes segments, 3 denotes arcs, and 4 specifies that all entity 
        types are to be selected.
        """

        self._steered_run("selectcircle", self.PREPROCES, x, y, R, editmode)

    def setgroup(self, number):
        '''Set the group associated of the selected items to number.'''
        self._steered_run("setgroup", self.PREPROCES, number)

    def setarcsegmentprop(self, maxsegdeg, propname, hide=False, group=0, inductor="<None>"):
        '''
        Set the selected arc segments to:
        Meshed with elements that span at most maxsegdeg degrees per element Boundary property "propname"
        hide: False = not hidden in post-processor, True == hidden in post processor
        A member of group number group
        A member of the conductor specified by the string "inconductor". If the segment is not part
        of a conductor, this parameter can be specified as "<None>" (not to be specified in magnetic problems).
        '''

        if hide:
            hide_index = 1
        else:
            hide_index = 0
        self._steered_run("setarcsegmentprop", self.PREPROCES, maxsegdeg, propname, hide_index, group, inductor)

    def setsegmentprop(self, elementsize, propname, inductor, hide=False, group=0, automesh=0):
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
                          inductor)

    def clearselected(self):
        """Clear all selected nodes, blocks, segments and arc segments"""
        self._steered_run("clearselected", self.PREPROCES)

    def zoomnatural(self, process_phase):
        '''zooms to a “natural” view with sensible extents.'''
        self._steered_run("zoomnatural", process_phase)

    def zoom(self, x1, y1, x2, y2, process_phase):
        """
        Set the display area to be from the bottom left corner specified
        by (x1,y1) to the top right corner specified by (x2,y2).
        """
        self._steered_run("zoom", process_phase, x1, y1, x2, y2)

    def deleteselectedarcsegments(self):
        '''Delete selects arcs'''
        self._steered_run("deleteselectedarcsegments", self.PREPROCES)

    def createradius(self, x, y, r):
        'turns a corner located at (x,y) into a curve of radius r.'
        self._steered_run("createradius", self.PREPROCES, x, y, r)

    def deleteselectednodes(self):
        self._steered_run("deleteselectednodes", self.PREPROCES)

    def selectgroup(self, group_number):
        """
        Select the group number group_number of nodes, segments, arc segments and blocklabels.
        This function will clear all previously selected elements and leave the editmode in 4 (group)
        """
        self._steered_run("selectgroup", self.PREPROCES, group_number)

    def moverotate(self, x0, y0, shiftangle):
        """
        – x0, y0 – base point for rotation
        – shiftangle – angle in degrees by which the selected objects are rotated.
        """
        self._steered_run("moverotate", self.PREPROCES, x0, y0, shiftangle)

    def getconductorproperties(self, circuit):
        return self._steered_run("getconductorproperties", self.POSTPROCES, circuit)

    def modifyconductorprop(self, conductor_name, propnum=1., value=0.):
        """This function allows for modification of a conductor property. 
        The conductor property to be modified is specified by ’ConductorName’. 
        The next parameter is the number of the property to be set. 
        The last number is the value to be applied to the specified property. 
        The various properties that can be modified are listed below:
            propnum Symbol Description
                - 0 ConductorName Name of the conductor property
                - 1 Vc Conductor voltage
                - 2 qc Total conductor charge
                - 3 ConductorType 0 = Prescribed charge, 1 = Prescribed voltage
        """
        self._steered_run('modifyconductorprop', self.PREPROCES, conductor_name, propnum, value)

    def saveas(self, filename):
        """ saves the file with name ’filename’."""
        ext_char = self.PROBLEMS_INDEXES[self.pb_type]['suffix']
        self._steered_run("saveas", self.PREPROCES, filename + '.fe' + ext_char)

    def analyze(self, hide=True):
        """
        runs the solver of the given problem. The flag parameter controls whether the solver window is
        visible or minimized. For a visible window, specify 0. For a minimized window, hide should be set
        to True. If no value is specified for flag, the visibility of the solver is inherited
        from the main window, i.e. if the main window is minimized, the solver runs minimized, too.
        """
        if hide is None:
            self._steered_run("analyze", self.PREPROCES)
        elif hide == True:
            self._steered_run("analyze", self.PREPROCES, 1)
        else:
            self._steered_run("analyze", self.PREPROCES, 0)

    def loadsolution(self):
        """
        loads and displays the solution corresponding to the current geometry
        """
        self._steered_run("loadsolution", self.PREPROCES)

    def groupselectblock(self, group_number=None):
        """
        Selects all the blocks that are labeled by block labels that are members of group n.
         If no number is specified (i.e. groupselectblock() ), all blocks are selected
        """
        if group_number is None:
            self._steered_run("groupselectblock", self.POSTPROCES)
        else:
            self._steered_run("groupselectblock", self.POSTPROCES, group_number)

    def selectblock(self, x, y):
        """Select the block that contains point (x,y)"""
        self._steered_run("selectblock", self.POSTPROCES, x, y)

    def set_group(self, inputs):
        '''function to gather femm element to a group
        :param inputs: python dict with the following format
              inputs ={element_type:{'points': list_point, 'group':nb_group},
                       'Segment':{'points': points_group, 'group':1}}
                        element_type: string, either 'Arc','Segment','Point' or 'Label'
                        list_point: numpy array of n*2 size
                        nb_group: int, group to be given to the elements selected
        :param pb_type: type of femm problem
        '''
        self.clearselected()
        for type_data in inputs:
            skimlist = ['Arc', 'Segment', 'Point', 'Label']
            if not (type_data in skimlist):
                raise InputError(type_data, skimlist)
            elif type_data == 'Arc':
                for point in inputs[type_data]['points']:
                    self.selectarcsegment(*point)
            elif type_data == 'Segment':
                for point in inputs[type_data]['points']:
                    self.selectsegment(*point)
            elif type_data == 'Point':
                for point in inputs[type_data]['points']:
                    self.selectnode(*point)
            elif type_data == 'Label':
                for point in inputs[type_data]['points']:
                    self.selectlabel(*point)
            self.setgroup(inputs[type_data]['group'])
            self.clearselected()

    def set_geom_boundary(self, inputs, **kwargs):
        '''function to set boundaries conditions
        :param inputs: python dict with the following format
              inputs = {'Name_of boundary':{'points': list of point, 'type':type_of segment},
                        'A=0':{'points': points_bound, 'type':'Segment'}}
                        list of point: numpy array of n*2 size
                        type_of segment: string, either 'Arc' or 'Segment'
        :param pb_type: type of femm problem
        :param maxsegdeg: Meshed with elements that span at most maxsegdeg degrees per element
        '''

        self.clearselected()

        for bound in inputs:
            type_data = inputs[bound]['type']
            skimlist = ['Arc', 'Segment']
            if not (type_data in skimlist):
                raise InputError(type_data, skimlist)

            elif type_data == 'Arc':
                dict_input = kwargs.copy()
                dict_input.pop('elementsize', None)
                for point in inputs[bound]['points']:
                    self.selectarcsegment(*point)
                self.setarcsegmentprop(propname=bound, **dict_input)

            elif type_data == 'Segment':
                dict_input = kwargs.copy()
                dict_input.pop('maxsegdeg', None)
                for point in inputs[bound]['points']:
                    self.selectsegment(*point)
                self.setsegmentprop(propname=bound, **dict_input)

            self.clearselected()

    def addconductorprop(self):
        raise NotImplementedError()

    def seteditmode(self, mode, pb_type, process_phase=POSTPROCES):
        """
        Sets the mode of the postprocessor to point, contour, or area mode.
        Valid entries for mode are "point", "contour", and "area".
        """
        self._steered_run("seteditmode", process_phase, mode)

    def addcontour(self, x, y):
        """
        Adds a contour point at (x,y). 
        If this is the first point then it starts a contour, if there are existing points
        the contour runs from the previous point to this point. 
        The addcontour command has the same functionality as a right-button-click contour 
        point addition when the program is running in interactive mode.
        """
        self._steered_run("addcontour", self.POSTPROCES, x, y)

    def makeplot(self, PlotType, NumPoints, Filename, FileFormat):
        self._steered_run("makeplot", self.POSTPROCES, PlotType, NumPoints, Filename, FileFormat)

    def clearblock(self):
        "Clear block selection"
        return self._steered_run("clearblock", self.POSTPROCES)

    def makeABC(self, n, R, x, y, bc):
        """
        creates a series of circular shells that emulate the impedance of an unbounded domain 
        (i.e. an Improvised Asymptotic Boundary Condition). The n parameter contains the number
         of shells to be used (should be between 1 and 10), R is the radius of the solution domain, 
         and (x,y) denotes the center of the solution domain. The bc parameter should be specified 
         as 0 for a Dirichlet outer edge or 1 for a Neumann outer edge. If the function is called 
         without all the parameters, the function makes up reasonable values for the missing parameters.
        """
        self._steered_run("makeABC", self.PREPROCES, n, R, x, y, bc)

    def makeABC_auto(self):
        """
        called without all the parameters, the function makes up reasonable values for the missing parameters
        """
        self._steered_run("makeABC", self.PREPROCES)

    def getpointvalues(self, x, y):
        """Gets the values associated with the point at (x,y). The function returns an array of results
        """
        return self._steered_run("getpointvalues", self.POSTPROCES, x, y)

    def movetranslate(self, dx, dy, editaction):
        """dx,dy,(editaction)) dx,dy – distance by which the selected objects are shifted. editaction 0 –nodes, 
        1 – lines (segments), 2 –block labels, 3 – arc segments, 4- group"""
        self._steered_run("movetranslate", self.PREPROCES, dx, dy, editaction)

    def blockintegral(self, integral_type):
        return self._steered_run("blockintegral", self.POSTPROCES, integral_type)

    def showdensityplot(self, upper_B, lower_B, type_plot, legend=True, grey_scale=False):
        if legend:
            self.legend_index = 1
        else:
            self.legend_index = 0

        if grey_scale:
            self.gscale = 1
        else:
            self.gscale = 0

        self.upper_B = upper_B
        self.lower_B = lower_B
        self.type_plot = type_plot

    ### New functions for the project :

    def addnode(self, x, y):
        """
        Add a new node at x,y 
        """
        self._steered_run("addnode", self.PREPROCES, x, y)

    def createmesh(self):
        """
        Runs triangle to create a mesh. Note that this is not a necessary precursor of
        performing an analysis, as mi_analyze or ei_analyze or hi_analyze will make sure the mesh is up to date before running an
        analysis. The number of elements in the mesh is pushed back onto the lua stack.
        """
        self._steered_run("createmesh", self.PREPROCES)

    def smooth(self, flag):
        """
        This function controls whether or not smoothing is applied to the B and H fields (m) or D and E fields (e) or F and G fields (h),
        which are naturally piece-wise constant over each element. Setting flag equal to ’on’ turns on
        smoothing and setting flag to ’off’ turns off smoothing.
        """
        self._steered_run("smooth", self.POSTPROCES, flag)

    def clearcontour(self):
        """
        Clear a prevously defined contour
        """
        self._steered_run("clearcontour", self.PREPROCES)

    def getb(self, x, y):
        """
        Get the magnetic flux density associated with the point at (x,y). The return
        value is a list with two elements representing Bx and By for planar problems and Br and Bz for
        axisymmetric problems.
        """
        self._steered_run("getb", self.POSTPROCES, x, y)

    def addbhpoint(self, blockname, b, h):
        """
        Adds a B-H data point the the material specified by the
        string ’blockname’. The point to be added has a flux density of b in units of Teslas and a field
        intensity of h in units of Amps/Meter.  
        """
        self._steered_run("addbhpoint", self.PREPROCES, blockname, b, h)

    def deleteselectedsegments(self):
        """
        Delete selected segments.
        """
        self._steered_run("deleteselectedsegments", self.PREPROCES)

    def purgemesh(self):
        """
        Clears the mesh out of both the screen and memory.
        """
        self._steered_run("purgemesh", self.PREPROCES)

    def setnodeprop(self, propname, groupno, inconductor):
        """
        Set the selected nodes to have the
        nodal property "propname" and group number groupno. The "inconductor" string specifies
        which conductor the node belongs to. If the node doesn’t belong to a named conductor, this
        parameter can be set to "<None>
        """
        self._steered_run("setnodeprop", self.PREPROCES, propname, groupno, inconductor)

    def copyrotate(self, bx, by, angle, copies):
        """
        – bx, by – base point for rotation
        – angle – angle by which the selected objects are incrementally shifted to make each copy.
        angle is measured in degrees.
        – copies – number of copies to be produced from the selected objects.
        """
        self._steered_run("copyrotate", self.PREPROCES, bx, by, angle, copies)


class TypeProblemError(Exception):

    def __init__(self, input_pb, pb_type):
        self.input_pb = input_pb
        self.pb_type = pb_type

    def __str__(self):
        text = "'" + self.input_pb + \
               "' is not a valid problem type for this function. Valid problem: " + \
               repr(self.pb_type)
        return text


class InputError(Exception):

    def __init__(self, value, keys):
        self.value = value
        self.keys = keys

    def __str__(self):
        text = "'" + self.value + \
               "' is not a valid input argument. Valid arguments: " + \
               repr(self.keys)
        return text
