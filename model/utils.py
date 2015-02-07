import maya.cmds as mc

import glTools.tools.bestFitPlane

import glTools.utils.base
import glTools.utils.shape
import glTools.utils.namespace
import glTools.utils.matrix
import glTools.utils.mesh
import glTools.utils.reference
import glTools.utils.stringUtils

def setVerticalPlacement(obj,freezeTransform=False):
	'''
	Align the base of a specified object with the ground plane based on the geometry bounding box.
	@param obj: The object to align with the ground plane
	@type obj: str
	@param freezeTransform: Freeze object transforms after move
	@type freezeTransform: bool
	'''
	# Checks
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!!')
	
	# Get Bounding Box Base
	bbox = glTools.utils.base.getMBoundingBox(obj)
	base = bbox.min().y
	
	# Set position
	mc.move(0,-base,0,obj,ws=True,r=True)
	
	# Freeze Transforms
	if freezeTransform: mc.makeIdentity()

def alignControlPoints(controlPointList,axis,localAxis=True):
	'''
	Align a list of control points to a specified axis or best fit plane.
	@param controlPointList: List of control points to align
	@type controlPointList: list
	@param axis: Axis to align control points to. Accepted values are "+x", "-x", "+y", "-y", "+z", "-z" and "bestFitPlane".
	@type axis: str
	@param localAxis: Specify if the align axis is in local or world relative. 
	@type localAxis: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Control Point List
	if not controlPointList:
		raise Exception('Invalid control points list specified!')
	# Axis
	axisList = ['+x','-x','+y','-y','+z','-z','bestFitPlane']
	if not axisList.count(axis):
		raise Exception('Invalid axis value specified! ("'+axis+'")')
	
	# Filter Control Point List
	controlPointList = mc.filterExpand(controlPointList,sm=[28,31,46])
	
	# Local Axis
	if axis == 'bestFitPlane': localAxis = False
	
	# ========================
	# - Align Control Points -
	# ========================
	
	# Get Control Point Position List
	ptList = []
	for cp in controlPointList:
		ptList.append(mc.pointPosition(cp,w=not(localAxis),l=localAxis))
	
	# Align Positions
	minVal = 99999.9
	maxVal = -99999.9
	if axis == '+x':
		for i in range(len(ptList)):
			if ptList[i][0] > maxVal: maxVal = ptList[i][0]
		ptList = [(maxVal,pt[1],pt[2]) for pt in ptList]
	
	elif axis == '-x':
		for i in range(len(ptList)):
			if ptList[i][0] < minVal: minVal = ptList[i][0]
		ptList = [(minVal,pt[1],pt[2]) for pt in ptList]
	
	elif axis == '+y':
		for i in range(len(ptList)):
			if ptList[i][1] > maxVal: maxVal = ptList[i][1]
		ptList = [(pt[0],maxVal,pt[2]) for pt in ptList]
	
	elif axis == '-y':
		for i in range(len(ptList)):
			if ptList[i][1] < minVal: minVal = ptList[i][1]
		ptList = [(pt[0],minVal,pt[2]) for pt in ptList]
	
	elif axis == '+z':
		for i in range(len(ptList)):
			if ptList[i][2] > maxVal: maxVal = ptList[i][2]
		ptList = [(pt[0],pt[1],maxVal) for pt in ptList]
	
	elif axis == '-z':
		for i in range(len(ptList)):
			if ptList[i][2] < minVal: minVal = ptList[i][2]
		ptList = [(pt[0],pt[1],minVal) for pt in ptList]
	
	elif axis == 'bestFitPlane':
		
		# Get Best Fit Plane Matrix
		mat = glTools.tools.bestFitPlane.bestFitPlaneMatrix(ptList)
		
		print('Got best fit plane')
		
		for i in range(len(ptList)):
			
			print(controlPointList[i])
			
			# Get Best Fit Plane Position 
			pPt = glTools.utils.matrix.vectorMatrixMultiply(	vector = ptList[i],
															matrix = mat,
															transformAsPoint = True,
															invertMatrix = True)
			
			# Project to Best Fit Plane
			pPt = (pPt[0],0.0,pPt[2])
			
			# Get World Space Position
			ptList[i] = glTools.utils.matrix.vectorMatrixMultiply(	vector = pPt,
																	matrix = mat,
																	transformAsPoint = True,
																	invertMatrix = False)
	
	else:
		raise Exception('Invalid axis value! ("'+axis+'")')
	
	print('Aligned!')
	
	# ===============================
	# - Set Control Point Positions -
	# ===============================
	
	for i in range(len(ptList)):
		print i
		mc.move(ptList[i][0],ptList[i][1],ptList[i][2],controlPointList[i],a=True,ws=not(localAxis),os=localAxis)

def loadIkaRigTools():
	'''
	Load glToolsTools plugin.
	'''
	# Check if plugin is loaded
	if not mc.pluginInfo('glToolsTools',q=True,l=True):
		
		# Load Plugin
		try: mc.loadPlugin('glToolsTools')
		except: raise Exception('Unable to load glToolsTools plugin!')
	
	# Return Result
	return 1

def slideDeformer(geo):
	'''
	Create a slide deformer for the specifed geometry.
	@param geo: The geometry to create the slide deformer for
	@type geo: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(geo):
		raise Exception('Object "'+geo+'" does not exist!!')
	
	# Mesh Shape
	if not glTools.utils.mesh.isMesh(geo):
		raise Exception('Object "'+geo+'" is not a valid mesh!!')
	shape = mc.listRelatives(geo,s=True,ni=True)
	if not shape:
		raise Exception('Object "'+geo+'" has no deformable geometry!!')
	
	# Load Plugin
	loadIkaRigTools()
	
	# Get Prefix
	prefix = geo.split(':')[-1]
	
	# ===================
	# - Create Deformer -
	# ===================
	
	slideDeformer = mc.deformer(geo,type='slideDeformer',n=prefix+'_slideDeformer')[0]
	
	# Connect Ref Mesh Shape
	inputMesh = None
	try: inputMesh = glTools.utils.shape.findInputShape(shape[0],recursive=True)
	except: pass
	if inputMesh: mc.connectAttr(inputMesh+'.outMesh',slideDeformer+'.referenceMesh',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return slideDeformer

def strainRelaxer(geo):
	'''
	Create a slide deformer for the specifed geometry.
	@param geo: The geometry to create the slide deformer for
	@type geo: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(geo):
		raise Exception('Object "'+geo+'" does not exist!!')
	
	# Mesh Shape
	if not glTools.utils.mesh.isMesh(geo):
		raise Exception('Object "'+geo+'" is not a valid mesh!!')
	shape = mc.listRelatives(geo,s=True,ni=True)
	if not shape:
		raise Exception('Object "'+geo+'" has no deformable geometry!!')\
	
	# Load Plugin
	loadIkaRigTools()
	
	# Get Prefix
	prefix = geo.split(':')[-1]
	
	# ===================
	# - Create Deformer -
	# ===================
	
	strainRelaxer = mc.deformer(geo,type='strainRelaxer',n=prefix+'_strainRelaxer')[0]
	
	# Connect Ref Mesh Shape
	inputMesh = ''
	try: inputMesh = glTools.utils.shape.findInputShape(shape[0],recursive=True)
	except: pass
	if inputMesh: mc.connectAttr(inputMesh+'.outMesh',strainRelaxer+'.refMesh',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return strainRelaxer

def directionalSmooth(geo):
	'''
	Create a directionalSmooth for the specifed geometry.
	@param geo: The geometry to create the directionalSmooth deformer for
	@type geo: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(geo):
		raise Exception('Object "'+geo+'" does not exist!!')
	
	# Mesh Shape
	if not glTools.utils.mesh.isMesh(geo):
		raise Exception('Object "'+geo+'" is not a valid mesh!!')
	shape = mc.listRelatives(geo,s=True,ni=True)
	if not shape:
		raise Exception('Object "'+geo+'" has no deformable geometry!!')
	
	# Load Plugin
	loadIkaRigTools()
	
	# Get Prefix
	prefix = geo.split(':')[-1]
	
	# ===================
	# - Create Deformer -
	# ===================
	
	directionalSmooth = mc.deformer(geo,type='directionalSmooth',n=prefix+'_directionalSmooth')[0]
	
	# Connect Ref Mesh Shape
	inputMesh = ''
	try: inputMesh = glTools.utils.shape.findInputShape(shape[0],recursive=True)
	except: pass
	if inputMesh: mc.connectAttr(inputMesh+'.outMesh',directionalSmooth+'.referenceMesh',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return directionalSmooth

def deltaMush(geo):
	'''
	Create a deltaMush deformer for the specifed geometry.
	@param geo: The geometry to create the deltaMush deformer for
	@type geo: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Geometry
	if not mc.objExists(geo):
		raise Exception('Object "'+geo+'" does not exist!!')
	
	# Mesh Shape
	if not glTools.utils.mesh.isMesh(geo):
		raise Exception('Object "'+geo+'" is not a valid mesh!!')
	shape = mc.listRelatives(geo,s=True,ni=True)
	if not shape:
		raise Exception('Object "'+geo+'" has no deformable geometry!!')
	
	# Load Plugin
	if not mc.pluginInfo('deltaMush',q=True,l=True):
		
		# Load Plugin
		try: mc.loadPlugin('deltaMush')
		except: raise Exception('Unable to load glToolsTools plugin!')
	
	# Get Prefix
	prefix = geo.split(':')[-1]
	
	# ===================
	# - Create Deformer -
	# ===================
	
	deltaMush = mc.deformer(geo,type='deltaMush',n=prefix+'_deltaMush')[0]
	
	# Connect Ref Mesh Shape
	inputMesh = None
	try: inputMesh = glTools.utils.shape.findInputShape(shape[0],recursive=True)
	except: pass
	if inputMesh: mc.connectAttr(inputMesh+'.outMesh',deltaMush+'.referenceMesh',f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return deltaMush
