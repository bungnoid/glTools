import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import data
import glTools.utils.surface
import glTools.utils.progressBar

class NurbsSurfaceData( data.Data ):
	'''
	NurbsSurfaceData class object.
	Contains functions to save, load and rebuild maya NURBS surface data.
	'''
	def __init__(self,surface=''):
		'''
		NurbsSurfaceData class initializer.
		'''
		# Execute Super Class Initilizer
		super(NurbsSurfaceData, self).__init__()

		# Initialize Default Class Data Members
		self._data['name'] = ''
		self._data['cv'] = []
		self._data['knotsU'] = []
		self._data['knotsV'] = []
		self._data['degreeU'] = 0
		self._data['degreeV'] = 0
		self._data['formU'] = 0
		self._data['formV'] = 0
		self._data['rational'] = True
		# Build Data
		if surface: self.buildData(surface)

	def buildData(self,surface,worldSpace=False):
		'''
		Build NurbsSurfaceData class.
		@param surface: Surface to build data from
		@type surface: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check Surface
		if not glTools.utils.surface.isSurface(surface):
			raise Exception('Object "'+surface+'" is not a vaild NURBS surface node!')
		
		# World Space
		space = OpenMaya.MSpace.kObject
		if worldSpace: space = OpenMaya.MSpace.kWorld
		
		# ==============
		# - Build Data -
		# ==============
		
		# Start timer
		timer = mc.timerX()
		
		# Get basic surface info
		self._data['name'] = surface

		# Get Surface Function Class
		surfaceFn = glTools.utils.surface.getSurfaceFn(surface)
		
		# Get Surface Degree and Form
		self._data['degreeU'] = surfaceFn.degreeU()
		self._data['degreeV'] = surfaceFn.degreeV()
		self._data['formU'] = int(surfaceFn.formInU())
		self._data['formV'] = int(surfaceFn.formInV())
		
		# Get Surface Knots
		knotsUarray = OpenMaya.MDoubleArray()
		knotsVarray = OpenMaya.MDoubleArray()
		surfaceFn.getKnotsInU(knotsUarray)
		surfaceFn.getKnotsInV(knotsVarray)
		self._data['knotsU'] = list(knotsUarray)
		self._data['knotsV'] = list(knotsVarray)

		# Get Control Vertices
		cvArray = OpenMaya.MPointArray()
		surfaceFn.getCVs(cvArray,space)
		self._data['cv'] = [(cvArray[i].x,cvArray[i].y,cvArray[i].z) for i in range(cvArray.length())]
		
		# =================
		# - Return Result -
		# =================
		
		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('NurbsSurfaceData: Data build time for surface "'+surface+'": '+str(buildTime))
		
		return self._data['name']

	def rebuild(self):
		'''
		'''
		# Start timer
		timer = mc.timerX()

		# ========================
		# - Rebuild Surface Data -
		# ========================
		
		# Rebuild Control Vertices
		numCVs = len(self._data['cv'])
		cvArray = OpenMaya.MPointArray(numCVs,OpenMaya.MPoint.origin)
		for i in range(numCVs):
			cvArray.set(OpenMaya.MPoint(self._data['cv'][i][0],self._data['cv'][i][1],self._data['cv'][i][2],1.0),i)
		
		# Rebuild Surface Knot Arrays
		numKnotsU = len(self._data['knotsU'])
		numKnotsV = len(self._data['knotsV'])
		knotsU = OpenMaya.MDoubleArray(numKnotsU,0)
		knotsV = OpenMaya.MDoubleArray(numKnotsV,0)
		for i in range(numKnotsU): knotsU.set(self._data['knotsU'][i],i)
		for i in range(numKnotsV): knotsV.set(self._data['knotsV'][i],i)

		# Rebuild Surface
		surfaceFn = OpenMaya.MFnMesh()
		surfaceData = OpenMaya.MFnNurbsSurfaceData().create()
		surfaceObj = surfaceFn.create(	cvArray,
										knotsU,
										knotsV,
										self._data['degreeU'],
										self._data['degreeV'],
										self._data['formU'],
										self._data['formV'],
										self._data['rational'],
										surfaceData	)
		surfaceObjHandle = OpenMaya.MObjectHandle(surfaceObj)

		# =================
		# - Return Result -
		# =================
		
		# Print Timed Result
		buildTime = mc.timerX(st=timer)
		print('NurbsSurfaceData: Data rebuild time for surface "'+self._data['name']+'": '+str(buildTime))
		
		return surfaceObjHandle

	def rebuildSurface(self):
		'''
		'''
		# Start timer
		timer = mc.timerX()
		
		# ========================
		# - Rebuild Surface Data -
		# ========================
		
		# Rebuild Control Vertices
		numCVs = len(self._data['cv'])
		cvArray = OpenMaya.MPointArray(numCVs,OpenMaya.MPoint.origin)
		for i in range(numCVs):
			cvArray.set(OpenMaya.MPoint(self._data['cv'][i][0],self._data['cv'][i][1],self._data['cv'][i][2],1.0),i)
		
		# Rebuild Surface Knot Arrays
		numKnotsU = len(self._data['knotsU'])
		numKnotsV = len(self._data['knotsV'])
		knotsU = OpenMaya.MDoubleArray(numKnotsU,0)
		knotsV = OpenMaya.MDoubleArray(numKnotsV,0)
		for i in range(numKnotsU): knotsU.set(self._data['knotsU'][i],i)
		for i in range(numKnotsV): knotsV.set(self._data['knotsV'][i],i)

		# Rebuild Surface
		surfaceFn = OpenMaya.MFnMesh()
		surfaceData = OpenMaya.MObject()
		surfaceObj = surfaceFn.create(	cvArray,
										knotsU,
										knotsV,
										self._data['degreeU'],
										self._data['degreeV'],
										self._data['formU'],
										self._data['formV'],
										self._data['rational'],
										surfaceData	)

		# Rename Surface
		surface = OpenMaya.MFnDependencyNode(surfaceObj).setName(self._data['name'])
		surfaceShape = mc.listRelatives(surface,s=True,ni=True,pa=True)[0]

		# Assign Initial Shading Group
		mc.sets(surfaceShape,fe='initialShadingGroup')

		# =================
		# - Return Result -
		# =================
		
		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('NurbsSurfaceData: Geometry rebuild time for surface "'+surface+'": '+str(buildTime))
		
		return surface
