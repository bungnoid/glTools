import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.curve

import data

class ControlCurveData( data.Data ):
	'''
	Control Curve Data Class Object.
	Contains functions to save, load and rebuild basic curve shapes.
	'''
	def __init__(self):
		'''
		ControlCurveData class initializer
		'''
		# Execute Super Class Initilizer
		super(ControlCurveData, self).__init__()
		
		self.setWorldSpace = False
	
	def buildData(self,ctrls=[]):
		'''
		Build Data
		@param ctrls: List of controls to save curve shape data for. If empty selects controls based on "ctrlLod" attr.
		@type ctrls: list
		'''
		# ============================
		# - Get Control Curve Shapes -
		# ============================
		
		if not ctrls: ctrls = mc.ls('*.ctrlLod',o=True)
		#if not ctrls: ctrls = mc.ls(type='nurbsCurve',o=True)
		if not ctrls: raise Exception('No control curves specified!')
		ctrlShapes = mc.listRelatives(ctrls,s=True,pa=True) or []
		ctrlCurves = mc.ls(ctrlShapes,type='nurbsCurve')
		ctrlCurves += mc.ls(ctrls, type='nurbsCurve') or []
		if not ctrlCurves: return
		
		# =============================
		# - Record Control Curve Data -
		# =============================
		
		# Reset Data
		self.reset()
		
		# Record Curve Data
		for ctrlCurve in ctrlCurves:
			
			# Get curve point list
			curveFn = glTools.utils.curve.getCurveFn(ctrlCurve)
			ptArray = OpenMaya.MPointArray()
			worldPtArray = OpenMaya.MPointArray()
			curveFn.getCVs(ptArray,OpenMaya.MSpace.kObject)
			curveFn.getCVs(worldPtArray,OpenMaya.MSpace.kWorld)
			
			# Build CV array
			cvArray = []
			worldCvArray = []
			for i in range(ptArray.length()):
				cvArray.append([ptArray[i].x,ptArray[i].y,ptArray[i].z])
				worldCvArray.append([worldPtArray[i].x,worldPtArray[i].y,worldPtArray[i].z])
			
			# Store cvArray
			self._data[ctrlCurve] = [ cvArray, worldCvArray ]
			
		# =================
		# - Return Result -
		# =================
		
		return ctrls
	
	def rebuild(self,ctrls=[]):
		'''
		Build Data
		@param ctrls: List of controls curve shape to rebuild. If empty selects controls based on "ctrlLod" attr.
		@type ctrls: list
		'''
		# ====================
		# - Get Control List -
		# ====================
		
		data_keys = self._data.keys()
		if not data_keys: return
		if not ctrls: ctrls = data_keys
		
		# ==========================
		# - Rebuild Control Shapes -
		# ==========================
		
		for ctrl in ctrls:
			
			# Check ctrl
			if not mc.objExists(ctrl):
				print ('ControlCurveData: Control Shape "'+ctrl+'" does not exist!')
				continue
			if not data_keys.count(ctrl):
				print ('ControlCurveData: No Data for Control Shape "'+ctrl+'"!')
				continue
			
			# Build Point Array
			ptArray = OpenMaya.MPointArray()
			
			if self.setWorldSpace:
				ctrlCrv = self._data[ctrl][1]
			else:
				ctrlCrv = self._data[ctrl][0]
				
			for cv in ctrlCrv:
				ptArray.append(OpenMaya.MPoint(cv[0],cv[1],cv[2],1.0))
			
			# Set CV Positions
			curveFn = glTools.utils.curve.getCurveFn(ctrl)
			if self.setWorldSpace:
				curveFn.setCVs(ptArray,OpenMaya.MSpace.kWorld)
			else:
				curveFn.setCVs(ptArray,OpenMaya.MSpace.kObject)
				
			curveFn.updateCurve()
		
		# =================
		# - Return Result -
		# =================
		
		return ctrls

