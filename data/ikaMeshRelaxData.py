import maya.cmds as mc
import deformerData

class IkaMeshRelaxData( deformerData.DeformerData ):
	'''
	IkaMeshRelaxData class object.
	'''
	# INIT
	def __init__(self,meshRelax=''):
		'''
		IkaMeshRelaxData class initilizer.
		'''
		# Escape
		if not meshRelax: return
		
		# Verify node
		if not mc.objExists(meshRelax):
			raise UserInputError('IkaMeshRelax '+meshRelax+' does not exists! No influence data recorded!!')
		objType = mc.objectType(meshRelax)
		if objType != 'ikaMeshRelax':
			raise UserInputError('Object '+meshRelax+' is not a vaild ikaMeshRelax node! Incorrect class for node type '+objType+'!!')
		
		# Execute super class initilizer
		super(IkaMeshRelaxData, self).__init__(meshRelax)
		
		#===================
		# Get Deformer Data
		self.frequencyCutoff = mc.getAttr(meshRelax+'.frequencyCutoff')
		self.iterations = mc.getAttr(meshRelax+'.iterations')
		self.maintainBoundary = mc.getAttr(meshRelax+'.maintainBoundary')
		self.smoothFactor = mc.getAttr(meshRelax+'.smoothFactor')
		self.peak = mc.getAttr(meshRelax+'.peak')
	
	def rebuild(self):
		'''
		Rebuild surfaceSkin deformer from saved deformer data
		'''
		#=========
		# CHECKS
		
		# Check ikaMeshRelax
		meshRelax = self.deformerName
		if mc.objExists(meshRelax): raise UserInputError('IkaMeshRelax '+meshRelax+' already exists!')
		# Check geometry
		for geometry in self.deformerData.iterkeys():
			if not mc.objExists(geometry): raise UserInputError('Target geometry '+geometry+' does not exist!')
		
		#=====================
		# Rebuild surfaceSkin
		meshRelax = super(IkaMeshRelaxData, self).rebuild()
		
		# Set deformer attribute values
		mc.setAttr(meshRelax+'.frequencyCutoff',self.frequencyCutoff)
		mc.setAttr(meshRelax+'.iterations',self.iterations)
		mc.setAttr(meshRelax+'.maintainBoundary',self.maintainBoundary)
		mc.setAttr(meshRelax+'.smoothFactor',self.smoothFactor)
		mc.setAttr(meshRelax+'.peak',self.peak)
	
