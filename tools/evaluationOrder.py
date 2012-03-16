import maya.cmds as mc

import glTools.utils.constraint

import glTools.tools.dependencyHierarchyNode

class EvaluationOrder( object ):
	'''
	This python class object is used to determine a reliable evaluation order for a hierarchy of rig controls.
	The DependencyHierarchyNode object is first used to map an entire rig hierarchy. Class methods of the
	EvaluationOrder class are then used to reshuffle the hierarchy based on various rig dependencies.
	'''
	def __init__(self,root,debug=False):
		'''
		'''
		# Transform type list
		self.transform = ['transform','joint','ikHandle']
		# Hierarchy root
		self.root = root
		# Attribute
		self.attribute = 'evalOrder'
		# Initialize dependancy network
		self.hierarchy = glTools.tools.dependencyHierarchyNode.DependencyHierarchyNode()
		self.hierarchy.buildHierarchyFromNode(root)
		# DEBUG
		self.debug = debug
	
	def reorder(self):
		'''
		Reorder hierarchy based on ik and constraint relationships
		'''
		ikReorder()
		constraintReorder()
	
	def ikReorder(self):
		'''
		Reorganize the evaluation order based on ikHandle/joint relationships.
		'''
		# Iterate through all ikHandles below hierarchy root
		ikList = mc.listRelatives(self.hierarchy.fullName,ad=True,type='ikHandle')
		for ik in ikList:
			ikNode = self.hierarchy.findDependNode(ik)
			# Find ikHandle start joint
			startJoint = mc.listConnections(ik+'.startJoint',s=True,d=False)[0]
			startJointNode = self.hierarchy.findDependNode(startJoint)
			
			# Check ikHandle is in a lower generation than the startJoints current parent
			if startJointNode.parent:
				if startJointNode.parent.getGeneration() >= ikNode.getGeneration(): continue
			
			# Adjust dependency hierarchy
			if ikNode.getGeneration() > startJointNode.getGeneration():
				if self.debug: print('Parent '+startJoint+' under ikHandle '+ik)
				startJointNode.reparent(ikNode)
			
		# Print complete message
		print('EvaluationOrder::ikReorder() completed.')
	
	def constraintReorder(self,constraintList=[]):
		'''
		Reorganize the evaluation order based on hierarchy constraint dependencies.
		@param constraintList: List of constraints to consider in the reorder.
		@type constraintList: list
		'''
		# Iterate through all constraints below hierarchy root
		if not constraintList: constraintList = mc.listRelatives(self.hierarchy.fullName,ad=True,type='constraint')
		
		if self.debug: print constraintList
		
		for constraintNode in constraintList:
			
			if self.debug: print constraintNode
			
			# Initialize comparison variables
			lowestNode = None
			generation = -1
			
			# Iterate through constraint targets, to find the target at the lowest generation
			targetList = glTools.utils.constraint.targetList(constraintNode)
			if self.debug: print 'targetlist = '
			if self.debug: print targetList
			for target in targetList:                                             
				targetNode = self.hierarchy.findDependNode(target)
				targetGeneration = targetNode.getGeneration()
				
				if self.debug: print 'targetGen = '+str(targetGeneration)+' : gen = '+str(generation)
				
				if targetGeneration > generation:
					lowestNode = targetNode
					generation = targetGeneration
			
			if self.debug:
				if lowestNode: print 'Lowest node = '+lowestNode.shortName
				else: print 'Lowest node = None'
			
			# Move constraint slaves below the lowest generation constraint target
			if lowestNode:
				slaveList = glTools.utils.constraint.slaveList(constraintNode)
				if self.debug: print 'slaveList = '
				if self.debug: print slaveList
				for slave in slaveList:
					slaveNode = self.hierarchy.findDependNode(slave)
					if lowestNode.getGeneration() > slaveNode.getGeneration():
						if self.debug: print('Parent '+slave+' under constraint target '+lowestNode.shortName)
						slaveNode.reparent(lowestNode)
			
		# Print complete message
		print('EvaluationOrder::constraintReorder() completed.')
	
	def addAttribute(self,target):
		'''
		Add evaluation order array attribute to a specified maya node.
		@param target: Target maya node that will hold the evaluation order array attribute.
		@type target: str
		'''
		# Check object exists
		if not mc.objExists(target):
			raise UserInputError('Target object '+target+' does not exist!')
		# Create attribute
		if not mc.objExists(target+'.'+self.attribute):
			mc.addAttr( target,ln=self.attribute,dt='string',multi=True,h=True)
		else:
			print('Attribute "'+target+'.'+self.attribute+'" already exists!')
	
	def setAttr(self,target,intersectList=[],evalOrderList=[]):
		'''
		Store the calculated evaluation order list as a string array attribute to a specified control.
		@param target: The maya node that will hold the evaluation order array attribute.
		@type target: str
		@param intersectList: Perform a list intersection between the calculated evaluation order with this list. If empty, no intersection is performed.
		@type intersectList: list
		@param evalOrderList: You can override the calculated evaluation order with a custom ordered list. If empty, use calculated evaluation order.
		@type evalOrderList: list
		'''
		# Check object exists
		if not mc.objExists(target):
			raise UserInputError('Target object '+target+' does not exist!')
		# Create attribute
		if mc.objExists(target+'.'+self.attribute):
			mc.deleteAttr(target,at=self.attribute)
		self.addAttribute(target)
		# Get calculated evaluation order list
		if not evalOrderList: evalOrderList = self.hierarchy.generationList()
		# Perform list intersection
		if intersectList: evalOrderList = [i for i in evalOrderList if intersectList.count(i)]
		# Set evaluation order array attribute
		for i in range(len(evalOrderList)):
			mc.setAttr(target+'.'+self.attribute+'['+str(i)+']',evalOrderList[i],type='string')
		# Return evaluation order list
		return evalOrderList
	
