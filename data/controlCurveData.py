import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import cPickle
import os.path

import glTools.utils.curve

class ControlCurveData( object ):
	'''
	Control Curve Data Class Object.
	Contains functions to save, load and rebuild basic curve shapes.
	'''
	def __init__(self):
		'''
		ControlCurveData class initializer
		'''
		self.cvList = {}
	
	def build(self,ctrls=[]):
		'''
		Build Data
		@param ctrls: List of controls to save curve shape data for. If empty selects controls based on "ctrlLod" attr.
		@type ctrls: list
		'''
		# Get control curve shapes
		if not ctrls: ctrls = mc.ls('*.ctrlLod',o=True)
		if not ctrls: raise Exception('No control curves specified!')
		ctrlShapes = mc.listRelatives(ctrls,s=True,pa=True)
		ctrlCurves = mc.ls(ctrlShapes,type='nurbsCurve')
		if not ctrlCurves: return
		
		# For each shape
		for ctrlCurve in ctrlCurves:
			
			# Get curve point list
			curveFn = glTools.utils.curve.getCurveFn(ctrlCurve)
			ptArray = OpenMaya.MPointArray()
			curveFn.getCVs(ptArray,OpenMaya.MSpace.kObject)
			
			# Build CV array
			cvArray = []
			for i in range(ptArray.length()):
				cvArray.append([ptArray[i].x,ptArray[i].y,ptArray[i].z])
			
			# Store cvArray
			self.cvList[ctrlCurve] = cvArray
	
	def rebuild(self,ctrls=[]):
		'''
		Build Data
		@param ctrls: List of controls curve shape to rebuild. If empty selects controls based on "ctrlLod" attr.
		@type ctrls: list
		'''
		# Get Control List
		data_keys = self.cvList.keys()
		if not data_keys: return
		if not ctrls: ctrls = data_keys
		
		# Rebuild Shapes
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
			for cv in self.cvList[ctrl]:
				ptArray.append(OpenMaya.MPoint(cv[0],cv[1],cv[2],1.0))
			
			# Set CV Positions
			curveFn = glTools.utils.curve.getCurveFn(ctrl)
			curveFn.setCVs(ptArray,OpenMaya.MSpace.kObject)
			curveFn.updateCurve()

	def save(self,filePath):
		'''
		Save control curve data object to file.
		@param filePath: Target file path
		@type filePath: str
		'''
		# Check filePath
		dirpath = filePath.replace(filePath.split('/')[-1],'')
		if not os.path.isdir(dirpath): os.makedirs(dirpath)
		
		# Export data to file
		fileOut = open(filePath,'wb')
		cPickle.dump(self,fileOut)
		fileOut.close()
		
		# Return result
		return filePath
		
	def load(self,filePath):
		'''
		Load control curve data object from file.
		@param filePath: Target file path
		@type filePath: str
		'''
		# Check filePath
		if not os.path.isfile(filePath):
			raise Exception('Invalid path "'+filePath+'"!')
		
		# Load file data
		fileIn = open(filePath,'rb')
		return cPickle.load(fileIn)
