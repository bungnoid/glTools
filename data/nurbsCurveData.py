import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import data
import glTools.utils.curve
import glTools.utils.progressBar

class NurbsCurveData( data.Data ):
	'''
	NurbsCurveData class object.
	Contains functions to save, load and rebuild maya NURBS curve data.
	'''
	def __init__(self,curve=''):
		'''
		NurbsCurveData class initializer.
		'''
		# Execute Super Class Initilizer
		super(NurbsCurveData, self).__init__()

		# Initialize Default Class Data Members
		self._data['name'] = ''
		self._data['cv'] = []
		self._data['editPt'] = []
		self._data['knots'] = []
		self._data['degree'] = 0
		self._data['form'] = 0
		self._data['2d'] = False
		self._data['rational'] = True

		# Build Data
		if curve: self.buildData(curve)

	def buildData(self,curve,worldSpace=False):
		'''
		Build NurbsCurveData class.
		@param curve: Curve to build data from
		@type curve: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Check Curve
		if not glTools.utils.curve.isCurve(curve):
			raise Exception('Object "'+curve+'" is not a vaild NURBS curve node!')
		
		# World Space
		space = OpenMaya.MSpace.kObject
		if worldSpace: space = OpenMaya.MSpace.kWorld
		
		# ==============
		# - Build Data -
		# ==============
		
		# Start timer
		timer = mc.timerX()
		
		# Get basic curve info
		self._data['name'] = curve

		# Get Curve Function Class
		curveFn = glTools.utils.curve.getCurveFn(curve)
		
		# Get Curve Degree and Form
		self._data['degree'] = curveFn.degreeU()
		self._data['form'] = int(curveFn.formInU())
		
		# Get Curve Knots
		knotArray = OpenMaya.MDoubleArray()
		curveFn.getKnotsInU(knotArray)
		self._data['knots'] = list(knotArray)
		
		# Get Control Vertices
		cvArray = OpenMaya.MPointArray()
		curveFn.getCVs(cvArray,space)
		self._data['cv'] = [(cvArray[i].x,cvArray[i].y,cvArray[i].z) for i in range(cvArray.length())]
		
		# Get Edit Points
		editPt = OPenMaya.MPoint()
		for u in self._data['knots']:
			curveFn.getPointAtParam(u,editPt,space)
			self._data['editPt'].append((editPt.x,editPt.y,editPt.z))
		
		# =================
		# - Return Result -
		# =================
		
		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('NurbsCurveData: Data build time for curve "'+curve+'": '+str(buildTime))
		
		return self._data['name']

	def rebuild(self):
		'''
		'''
		# Start timer
		timer = mc.timerX()

		# ========================
		# - Rebuild Curve Data -
		# ========================
		
		# Rebuild Control Vertices
		numCVs = len(self._data['cv'])
		cvArray = OpenMaya.MPointArray(numCVs,OpenMaya.MPoint.origin)
		for i in range(numCVs):
			cvArray.set(OpenMaya.MPoint(self._data['cv'][i][0],self._data['cv'][i][1],self._data['cv'][i][2],1.0),i)
		
		# Rebuild Curve Knot Arrays
		numKnots = len(self._data['knots'])
		knots = OpenMaya.MDoubleArray(numKnots,0)
		for i in range(numKnotsV): knots.set(self._data['knots'][i],i)

		# Rebuild Curve
		curveFn = OpenMaya.MFnNurbsCurve()
		curveData = OpenMaya.MFnNurbsCurveData().create()
		curveObj = curveFn.create(	cvArray,
									knots,
									self._data['degree'],
									self._data['form'],
									self._data['2d'],
									self._data['rational'],
									curveData	)
		curveObjHandle = OpenMaya.MObjectHandle(curveObj)

		# =================
		# - Return Result -
		# =================
		
		# Print Timed Result
		buildTime = mc.timerX(st=timer)
		print('NurbsCurveData: Data rebuild time for curve "'+self._data['name']+'": '+str(buildTime))
		
		return curveObjHandle

	def rebuildCurve(self):
		'''
		'''
		# Start timer
		timer = mc.timerX()
		
		# ========================
		# - Rebuild Curve Data -
		# ========================
		
		# Rebuild Control Vertices
		numCVs = len(self._data['cv'])
		cvArray = OpenMaya.MPointArray(numCVs,OpenMaya.MPoint.origin)
		for i in range(numCVs):
			cvArray.set(OpenMaya.MPoint(self._data['cv'][i][0],self._data['cv'][i][1],self._data['cv'][i][2],1.0),i)
		
		# Rebuild Curve Knot Arrays
		numKnots = len(self._data['knots'])
		knots = OpenMaya.MDoubleArray(numKnots,0)
		for i in range(numKnots): knots.set(self._data['knots'][i],i)
		
		# Rebuild Curve
		curveFn = OpenMaya.MFnMesh()
		curveData = OpenMaya.MObject()
		curveObj = curveFn.create(	cvArray,
									knots,
									self._data['degree'],
									self._data['form'],
									self._data['rational'],
									self._data['2d'],
									curveData	)

		# Rename Curve
		curve = OpenMaya.MFnDependencyNode(curveObj).setName(self._data['name'])
		
		# =================
		# - Return Result -
		# =================
		
		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('NurbsCurveData: Geometry rebuild time for mesh "'+curve+'": '+str(buildTime))
		
		return curve
