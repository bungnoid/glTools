import maya.cmds as mc
import maya.OpenMaya as OpenMaya

class UserInputError(Exception): pass

class SmoothMeshUtilities(object):
	
	def __init__(self):
		self.smoothLevelOverrideType = ['double','long']
		self.smoothLevelCondition = 'cn_high01_cnd'

	def create(self, modelGroup, smoothAttr='supermover.resolution', smoothValue=2, smoothLevelOverrideAttr=''):
		'''
		This replaces our old createSmooth proc since we no longer need smooth geometry generated in the scene.
		This proc checks for the "resolution" attribute on the supermover if it does not exist,it will raise an exception.
		Run BaseRig.addResolutionAttr() to add the .resolution attr to the supermover.
		It will also generate the condition node for the smoothValue and connect the supermover.resolution to the
		cn_high01_cnd.smoothLevel
		
		@param modelGroup: The group node under which to serch for mesh objects to connect
		@type modelGroup: str
		@param smoothAttr: Attribute that will control the smoothLevel toggle
		@type smoothAttr: str
		@param smoothValue: The value the attribute specified by smoothAttr must be to activate the toggle
		@type smoothValue: int
		@param smoothLevelOverrideAttr: Attribute that will set the number of smooth subdivisions.
		@type smoothLevelOverrideAttr: str
		@keyword: model, utility, toggle, smooth
		'''
		# Check resolution toggle attribute
		if not mc.objExists(smoothAttr):
			raise UserInputError('Attribute "'+smoothAttr+'" does not exists! Can\'t connect smooth.')
		
		# Get the meshes under the model group
		mesh = mc.listRelatives(modelGroup , type='mesh', ad=1)
		if not mesh:
			print('No mesh decendants of "'+modelGroup+'"! Skipping smoothMesh preview connection!!')
			return
		
		# Add condition node, connect and set attributes.
		if not mc.objExists(self.smoothLevelCondition):
			self.smoothLevelCondition = mc.shadingNode('condition', asUtility=1, n=self.smoothLevelCondition)
			mc.connectAttr(smoothAttr, self.smoothLevelCondition+'.firstTerm', f=1)
			mc.setAttr(self.smoothLevelCondition + '.secondTerm', smoothValue)
			mc.setAttr(self.smoothLevelCondition + '.operation', 0)
			mc.setAttr(self.smoothLevelCondition + '.colorIfTrueR', 1)
			mc.setAttr(self.smoothLevelCondition + '.colorIfFalseR', 0)
		
		# Connect the condition node outColorR to the smoothLevel of the shapes
		for shape in mesh:
			mc.setAttr(shape + '.displaySmoothMesh',2)
			mc.connectAttr(self.smoothLevelCondition+'.outColorR', shape + '.smoothLevel')
		
		# Connect smoothLevel override attribute
		if len(smoothLevelOverrideAttr):
			# Check attr exists
			if not mc.objExists(smoothLevelOverrideAttr):
				objAttr = smoothLevelOverrideAttr.split('.')
				if len(objAttr) != 2: raise UserInputError('smoothLevelOverrideAttr string must be in the form of "object.attribute"!!')
				# Add override attr
				mc.addAttr(objAttr[0],ln=objAttr[1],at='long',dv=1)
			else:
				if not self.smoothLevelOverrideType.count(mc.addAttr(smoothLevelOverrideAttr,q=True,at=True)):
					raise UserInputError('Attribute "' + smoothLevelOverrideAttr + '" is not of the expected type! Attribute must be "double" or "long" type!!')
			mc.connectAttr(smoothLevelOverrideAttr,self.smoothLevelCondition+'.colorIfTrueR',force=True)
		
		print 'Finished Connecting Smooth Levels. See script editor for details.'
	
	def smoothWrapper(self):
		'''
		This is  a simple wrapper for smoothMeshUtilities.create
		@keyword: model, utility, toggle
		@appVersion: 8.5, 2008
		'''
		if not mc.objExists('supermover.resolution'):
			raise UserInputError('Attribute "supermover.resolution" does not exist! Cannot connect smooth!!')
		# Query enum string
		enumStr = mc.addAttr('supermover.resolution',q=1,en=1)
		enumCnt = len(enumStr.split(':'))
		# Query number of resolution options
		if enumCnt == 3: smoothVal = 2
		elif enumCnt == 2: smoothVal = 1
		else: raise UserInputError('Unexpected resolution enum size for "supermover.resolution"!')
		# run smooth
		self.create('model','supermover.resolution',smoothVal,'supermover.smoothLevelOverride')