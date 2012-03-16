import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.common.connectionUtilities
import glTools.utils.curve

import multiInfluenceDeformerData

# Create exception class
class UserInputError(Exception): pass

###############################################################
#<OPEN>
#<CLASS NAME>
#		WireData
#</CLASS NAME>
#
#<DESCRIPTION>
#		Data Class for wire deformer data.
#</DESCRIPTION>
#
#<USAGE>
#		wire1Data = DeformerData('wire1')
#		wire1Data.save('/home/g/$USER/wire1.pkl')
#		newWireData = DeformerData.load('/home/g/$USER/wire1.pkl')
#</USAGE>
#
#<CLOSE>
#############################################################

class WireData( multiInfluenceDeformerData.MultiInfluenceDeformerData ):
	'''
	WireData class object.
	'''
	# INIT
	def __init__(self,wire=''):
		
		# Escape
		if not wire: return
		
		# Verify node
		if not mc.objExists(wire):
			raise UserInputError('Wire deformer '+wire+' does not exists! No influence data recorded!!')
		objType = mc.objectType(wire)
		if objType != 'wire':
			raise UserInputError('Object '+wire+' is not a vaild wire deformer! Incorrect class for node type '+objType+'!!')
		
		# Execute super class initilizer
		super(WireData, self).__init__(wire)
		
		# Connection Utility Class
		self.connectionUtils = glTools.common.connectionUtilities.ConnectionUtilities()
		
		#===================
		# Get Deformer Data
		self.crossingEffect = mc.getAttr(wire+'.crossingEffect')
		self.tension = mc.getAttr(wire+'.tension')
		self.localInfluence = mc.getAttr(wire+'.localInfluence')
		self.rotation = mc.getAttr(wire+'.rotation')
		
		#====================
		# Get Influence Data
		self.influenceData = {}
		
		# Get Influence List
		influenceList = self.connectionUtils.connectionListToAttr(wire,'deformedWire')
		for influence in influenceList.keys():
			influenceShape = influence
			influence = mc.listRelatives(influenceShape,p=True)[0]
			# Get MFnNurbsCurve function class
			curveFn = glTools.utils.curve.getCurveFn(influence)
			knots = OpenMaya.MDoubleArray()
			curveFn.getKnots(knots)
			# Initialize influence data dictionary
			self.influenceData[influence] = {}
			# Build influence data
			infIndex = influenceList[influenceShape][1]
			self.influenceData[influence]['index'] = infIndex
			self.influenceData[influence]['dropoff'] = mc.getAttr(wire+'.dropoffDistance['+str(infIndex)+']')
			self.influenceData[influence]['scale'] = mc.getAttr(wire+'.scale['+str(infIndex)+']')
			self.influenceData[influence]['degree'] = mc.getAttr(influence+'.degree')
			self.influenceData[influence]['knots'] = tuple(knots)
			self.influenceData[influence]['cvList'] = []
			for i in range(curveFn.numCVs()):
				self.influenceData[influence]['cvList'].append(tuple(mc.pointPosition(influence+'.cv['+str(i)+']')))
		
		#=========================
		# Get Influence Base Data
		self.influenceBaseData = {}
		
		# Get Influence Base List
		influenceBaseList = self.connectionUtils.connectionListToAttr(wire,'baseWire')
		for influenceBase in influenceBaseList.keys():
			influenceShape = influenceBase
			influenceBase = mc.listRelatives(influenceShape,p=True)[0]
			# Get MFnNurbsCurve function class
			curveFn = glTools.utils.curve.getCurveFn(influenceBase)
			knots = OpenMaya.MDoubleArray()
			curveFn.getKnots(knots)
			# Initialize influence base data dictionary
			self.influenceBaseData[influenceBase] = {}
			# Build influence data
			infIndex = influenceBaseList[influenceShape][1]
			self.influenceBaseData[influenceBase]['index'] = infIndex
			self.influenceBaseData[influenceBase]['degree'] = mc.getAttr(influence+'.degree')
			self.influenceBaseData[influenceBase]['knots'] = tuple(knots)
			self.influenceBaseData[influenceBase]['cvList'] = []
			for i in range(curveFn.numCVs()):
				self.influenceBaseData[influenceBase]['cvList'].append(tuple(mc.pointPosition(influenceBase+'.cv['+str(i)+']')))
		
		#==========================
		# Get Dropoff Locator Data
		self.dropoffLocatorData = {}
		
		# Get Dropoff Locator List
		dropoffLocatorList = self.connectionUtils.connectionListToAttr(wire,'wireLocatorParameter')
		for locator in dropoffLocatorList.keys():
			# Initialize dropoff locator data dictionary
			self.dropoffLocatorData[locator] = {}
			# Build dropoff locator data
			locIndex = dropoffLocatorList[locator][1]
			self.dropoffLocatorData[locator]['index'] = locIndex
			self.dropoffLocatorData[locator]['envelope'] = mc.getAttr(wire+'.wireLocatorEnvelope['+str(locIndex)+']')
			self.dropoffLocatorData[locator]['twist'] = mc.getAttr(wire+'.wireLocatorTwist['+str(locIndex)+']')
			self.dropoffLocatorData[locator]['percent'] = mc.getAttr(locator+'.percent')
			self.dropoffLocatorData[locator]['parameter'] = mc.getAttr(locator+'.param')
			# Get wire curve parent
			locParent = mc.listRelatives(locator,p=True)[0]
			crvParent = mc.listRelatives(locParent,p=True)[0]
			self.dropoffLocatorData[locator]['parent'] = crvParent
		
	def rebuild(self):
		'''
		Rebuild the wire deformer from the recorded deformerData
		'''
		# Rebuild deformer
		wire = super(WireData, self).rebuild()
		
		# Check Wire Curves
		for curve in self.influenceData.iterkeys():
			if not mc.objExists(curve):
				pts = self.influenceData[curve]['cvList']
				knots = self.influenceData[curve]['knots']
				degree = self.influenceData[curve]['degree']
				mc.curve(p=pts,k=knots,d=degree,n=curve)
		
		# Check Base Curves
		for curve in self.influenceBaseData.iterkeys():
			if not mc.objExists(curve):
				pts = self.influenceBaseData[curve]['cvList']
				knots = self.influenceBaseData[curve]['knots']
				degree = self.influenceBaseData[curve]['degree']
				curve = mc.curve(p=pts,k=knots,d=degree,n=curve)
				mc.setAttr(curve+'.v',0)
		
		# Check Dropoff Locators
		for locator in self.dropoffLocatorData.iterkeys():
			if mc.objExists(self.dropoffLocatorData[locator]['parent']):
				mc.delete(self.dropoffLocatorData[locator]['parent'])
		
		# Set Deformer Attributes
		mc.setAttr(wire+'.crossingEffect',self.crossingEffect)
		mc.setAttr(wire+'.tension',self.tension)
		mc.setAttr(wire+'.localInfluence',self.localInfluence)
		mc.setAttr(wire+'.rotation',self.rotation)
		
		# Connect wire curves
		for curve in self.influenceData.iterkeys():
			mc.connectAttr(curve+'.worldSpace[0]',wire+'.deformedWire['+str(self.influenceData[curve]['index'])+']',f=True)
		# Connect base curves
		for curve in self.influenceBaseData.iterkeys():
			mc.connectAttr(curve+'.worldSpace[0]',wire+'.baseWire['+str(self.influenceBaseData[curve]['index'])+']',f=True)
		
		# Set Influence Attributes
		for influence in self.influenceData.iterkeys():
			infIndex = self.influenceData[influence]['index']
			mc.setAttr(wire+'.dropoffDistance['+str(infIndex)+']',self.influenceData[influence]['dropoff'])
			mc.setAttr(wire+'.scale['+str(infIndex)+']',self.influenceData[influence]['scale'])
		
		# Recreate Dropoff Locators
		for locator in self.dropoffLocatorData.iterkeys():
			locIndex = self.dropoffLocatorData[locator]['index']
			param = self.dropoffLocatorData[locator]['parameter']
			parent = self.dropoffLocatorData[locator]['parent']
			env = self.dropoffLocatorData[locator]['envelope']
			percent = self.dropoffLocatorData[locator]['percent']
			mc.select(parent+'.u['+str(param)+']')
			newLoc = mc.dropoffLocator(env,percent,wire)
			mc.setAttr(wire+'.wireLocatorTwist['+str(locIndex)+']',self.dropoffLocatorData[locator]['twist'])
			if parent != newLoc: newLoc = mc.rename(newLoc,parent)
			locShape = mc.listRelatives(newLoc,s=True,ni=True)[0]
			if locator != locShape: locator = mc.rename(locShape,locator)
		
		# Return result
		return wire
