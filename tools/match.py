import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import math
import copy

class UserInputError( Exception ): pass

class Match( object ):
	
	def __init__(self):
		
		# Attribute names
		self.twinAttr = 'twin'
		self.twinXAttr = 'twinX'
		self.twinYAttr = 'twinY'
		self.twinZAttr = 'twinZ'
		self.pivotAttr = 'pivot'
		self.axisAttr = 'mirrorAxis'
		self.modeAttr = 'matchMode'
		self.evalOrderAttr = 'all.evalOrder'
		self.xform = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
		
		# Axis vectors
		self.xAxis = (1,0,0)
		self.yAxis = (0,1,0)
		self.zAxis = (0,0,1)
		
		# Axis'
		self.axisIndex = {'x':0,'y':1,'z':2,'-x':3,'-y':4,'-z':5}
		# Rotate Order
		self.rotateOrder = {'xyz':0,'yzx':1,'zxy':2,'xzy':3,'yxz':4,'zyx':5}
		
		# Side
		self.leftPrefix = 'lf'
		self.rightPrefix = 'rt'
		
		# Constants
		self.radian = 180.0/math.pi
		
		# Recognized transform types
		self.transform = ['transform','joint']
		
		# Maya Window Elements
		self.channelBox = 'MayaWindow|mayaMainWindowForm|formLayout3|formLayout11|formLayout32|formLayout33|ChannelsLayersPaneLayout|formLayout36|menuBarLayout1|frameLayout1|mainChannelBox'
	
	#---------
	# EXECUTE
	#---------
	
	def twinTransform(self,master='',slave='',pivot='',mirrorAxis='',mirrorMode='',xformList=[1,1,1,1,1,1,1,1,1]):
		'''
		Twin transformations of master object to slave object across a pivot object.
		@param master: Master object that will provide the transformation information to be passed to the slave object
		@type master: str
		@param slave: Slave object that will be posed to match the master object across the specified pivot
		@type slave: str
		@param pivot: Object that will be used as the mirror pivot for pose matching
		@type pivot: str
		@param mirrorAxis: Axis across which the mirror will be scaled. This axis is local to the pivot object
		@type pivot: str
		@param mirrorMode: Specifies local or global pose matching
		@type mirrorMode: int
		@param xformList: List of 9 boolean elements. Each element specifies if a particular transform attribute will be affected by the twin operation.
		@type xformList: list
		'''
		# Check valid master
		if not mc.objExists(master+'.'+self.twinAttr): return
		
		# Get control parent transforms
		masterParent = ''
		try: masterParent = str(mc.listRelatives(master,p=1)[0])
		except: pass
		slaveParent = ''               
		try: slaveParent = str(mc.listRelatives(slave,p=1)[0])
		except: pass
		pivotParent = ''
		try: pivotParent = str(mc.listRelatives(pivot,p=1)[0])
		except: pass
		
		# Get match attr values
		twinX = mc.getAttr(slave+'.'+self.twinXAttr)
		twinY = mc.getAttr(slave+'.'+self.twinYAttr)
		twinZ = mc.getAttr(slave+'.'+self.twinZAttr)
		if not mirrorAxis: mirrorAxis = mc.getAttr(slave+'.'+self.axisAttr)
		if type(mirrorAxis) == str: mirrorAxis = self.axisIndex[mirrorAxis]
		if not mirrorMode: mirrorMode = mc.getAttr(slave+'.'+self.modeAttr)
		slaveRotateOrder = mc.getAttr(slave+'.ro')
		masterRotateOrder = mc.getAttr(master+'.ro')
		
		# Get Mater Transform channel values
		pos = list(mc.getAttr(master+'.translate')[0])
		rot = list(mc.getAttr(master+'.rotate')[0])
		scl = list(mc.getAttr(master+'.scale')[0])
		
		if mirrorMode: # LOCAL Match
			
			# Translate #===============
			translate = [pos[0],pos[1],pos[2],-pos[0],-pos[1],-pos[2]]
			pos[0] = translate[twinX]
			pos[1] = translate[twinY]
			pos[2] = translate[twinZ]
			
			# Rotate #===============
			
			# Convert degrees to radians
			rot = [(rot[i]/self.radian) for i in range(3)]
			# Reorder to XYZ
			eulerRotation = OpenMaya.MEulerRotation(rot[0],rot[1],rot[2],masterRotateOrder)
			eulerRotation.reorderIt(0)
			rot = [eulerRotation.x,eulerRotation.y,eulerRotation.z]
			# Determine twin equivalent
			rotate = [-rot[0],-rot[1],-rot[2],rot[0],rot[1],rot[2]]
			rot = [rotate[twinX],rotate[twinY],rotate[twinZ]]
			# Adjust for mis-matched twin axis relationships
			rotateOrderStr = 'xyz'[twinX%3] + 'xyz'[twinY%3] + 'xyz'[twinZ%3]
			eulerRotation = OpenMaya.MEulerRotation(rot[0],rot[1],rot[2],self.rotateOrder[rotateOrderStr])
			eulerRotation = eulerRotation.reorder(slaveRotateOrder)
			rot = [eulerRotation.x,eulerRotation.y,eulerRotation.z]
			# Convert radians to degrees
			rot = [(rot[i]*self.radian) for i in range(3)]
			
			# Scale #===============
			scale = [scl[0],scl[1],scl[2]]
			scl[0] = scale[(twinX%3)]
			scl[1] = scale[(twinY%3)]
			scl[2] = scale[(twinZ%3)]
			
		else: # WORLD Match
			
			# Translate #===============
			if xformList[0] or xformList[1] or xformList[2]:
				
				# Check self pivot
				if master == pivot: pos[mirrorAxis] *= -1
				else:
					# Transform to world
					if masterParent: pos = self.transformVector(pos,masterParent,transformAsPoint=True,invertTransform=False)
					# Mirror across pivot axis
					pos = self.transformVector(pos,pivot,transformAsPoint=True,invertTransform=True)
					pos[mirrorAxis] *= -1
					pos = self.transformVector(pos,pivot,transformAsPoint=True,invertTransform=False)
					# Transform to slave local
					if slaveParent: pos = self.transformVector(pos,slaveParent,transformAsPoint=True,invertTransform=True)
				
			# Rotate #===============
			if xformList[3] or xformList[4] or xformList[5] or xformList[6] or xformList[7] or xformList[8]:
			
				# Check self pivot
				if master == pivot: pivot = str(pivotParent)
				
				# Build basis vectors
				twinAxis = []
				twinAxis.append(self.vectorTwinSpaceMirror(self.xAxis,master,slave,pivot,mirrorAxis))
				twinAxis.append(self.vectorTwinSpaceMirror(self.yAxis,master,slave,pivot,mirrorAxis))
				twinAxis.append(self.vectorTwinSpaceMirror(self.zAxis,master,slave,pivot,mirrorAxis))
				twinAxis.append([-twinAxis[0][0],-twinAxis[0][1],-twinAxis[0][2]])
				twinAxis.append([-twinAxis[1][0],-twinAxis[1][1],-twinAxis[1][2]])
				twinAxis.append([-twinAxis[2][0],-twinAxis[2][1],-twinAxis[2][2]])
				xAxis = twinAxis[twinX]
				yAxis = twinAxis[twinY]
				zAxis = twinAxis[twinZ]
				
				# Create rotation matrix from basis vectors
				matrix = OpenMaya.MMatrix()
				OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 0, xAxis[0])
				OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 1, xAxis[1])
				OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 2, xAxis[2])
				OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 0, yAxis[0])
				OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 1, yAxis[1])
				OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 2, yAxis[2])
				OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 0, zAxis[0])
				OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 1, zAxis[1])
				OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 2, zAxis[2])
				xformMatrix = OpenMaya.MTransformationMatrix(matrix)
				eulerRotation = xformMatrix.eulerRotation()
				eulerRotation = eulerRotation.reorder(slaveRotateOrder)
				rot = (eulerRotation.x*self.radian,eulerRotation.y*self.radian,eulerRotation.z*self.radian)
				
				# Scale #===============
				if xformList[6] or xformList[7] or xformList[8]:
					
					# Extract scale values from basis vector lengths
					scl[0] = OpenMaya.MVector(xAxis[0],xAxis[1],xAxis[2]).length()
					scl[1] = OpenMaya.MVector(yAxis[0],yAxis[1],yAxis[2]).length()
					scl[2] = OpenMaya.MVector(zAxis[0],zAxis[1],zAxis[2]).length()
			
		return [pos[0],pos[1],pos[2],rot[0],rot[1],rot[2],scl[0],scl[1],scl[2]]
	
	def twinCustomAttrs(self,master='',slave='',customAttrList=[]):
		'''
		Twin all non transform attribute values. Results are returned via a dictionary which stores the attribute:value
		as a key:value pair.
		@param master: Object that will provide the custom attribute values
		@type master: str
		@param customAttrList: List of custom attributes to twin
		@type customAttrList: list
		'''
		# Twin custom attribute values
		customAttrValues = {}
		for attr in customAttrList:
			twinAttr = attr
			# Check self pivot
			if master == slave:
				if attr.startswith('lf'): twinAttr = attr.replace('lf','rt')
				if attr.startswith('rt'): twinAttr = attr.replace('rt','lf')
			# Store twin attribute value
			customAttrValues[twinAttr] = mc.getAttr(master+'.'+attr)
		return customAttrValues
	
	def twin(self,master='',slave='',pivot='',mirrorAxis='',mirrorMode='',xformList=[1,1,1,1,1,1,1,1,1],customAttrList=['all']):
		'''
		Perform twin based on input arguments
		@param master: Master object that will provide the transformation information to be passed to the slave object
		@type master: str
		@param slave: Slave object that will be posed to match the master object across the specified pivot
		@type slave: str
		@param pivot: Object that will be used as the mirror pivot for pose matching
		@type pivot: str
		@param mirrorAxis: Axis across which the mirror will be scaled. This axis is local to the pivot object
		@type pivot: str
		@param mirrorMode: Specifies local or global pose matching
		@type mirrorMode: int
		@param xformList: List of 9 boolean elements. Each element specifies if a particular transform attribute will be affected by the twin operation.
		@type xformList: list
		@param customAttrList: List of custom attributes to twin
		@type customAttrList: list
		'''
		
		# Check valid arguments
		if not master: raise UserInputError('You must specifiy a valid master transform!')
		if not mc.objExists(master+'.'+self.twinAttr): return
		if not slave: slave = str(mc.getAttr(master+'.'+self.twinAttr))
		if not pivot: pivot = str(mc.getAttr(master+'.'+self.pivotAttr))
		
		# Check namespace
		ns = ''
		if master.count(':'):
			try: ns = master.split(':')[0]+':'
			except: pass
			else: 
				if not slave.startswith(ns): slave = ns+slave
				if not pivot.startswith(ns): pivot = ns+pivot
		
		# Check objects exist
		if not mc.objExists(master): raise UserInputError('Master object '+master+' does not exists!')
		if not mc.objExists(slave): raise UserInputError('Slave object '+slave+' does not exists!')
		if not mc.objExists(pivot): raise UserInputError('Pivot object '+pivot+' does not exists!')
		
		# Transform ---------
		
		# Check distination attributes settable state
		for i in range(9):
			if xformList[i]: xformList[i] = mc.getAttr(slave+'.'+self.xform[i],se=True)
		# Get twin transform values
		xform = self.twinTransform(master,slave,pivot,mirrorAxis,mirrorMode,xformList)
		# Set Slave Transforms
		for i in range(9):
			if xformList[i]: mc.setAttr(slave+'.'+self.xform[i],xform[i])
		
		# Custom Attributes ---------
		
		# Check custom attribute list
		if len(customAttrList) == 1 and customAttrList[0] == 'all': customAttrList = mc.listAttr(master,keyable=True,userDefined=True)
		# Initialize custom attr value dictionary
		customAttrVals = {}
		# Retrieve custom attribute values
		if customAttrList: customAttrVals = self.twinCustomAttrs(master,slave,customAttrList)
		# Set custom attribute values
		for attr in customAttrVals.iterkeys():
			if mc.objExists(slave+'.'+attr): mc.setAttr(slave+'.'+attr,customAttrVals[attr])
	
	#----------
	# WRAPPERS
	#----------
	
	def twinSelection(self):
		'''
		Twin the current selected objects.
		'''
		# Get selection list
		selection =  mc.ls(sl=1,type=self.transform)
		# Get namespace
		ns = ''
		try:
			if selection[0].count(':'): ns = selection[0].split(':')[0]+':'
		except: pass
		# Get channelBox attribute selection
		xformList = self.getCBxformList()
		userDefList = self.getCBuserDefList()
		# Get selection list in order of evaluation
		orderedSel = selection
		if mc.objExists(ns+self.evalOrderAttr):
			evalOrderLen = mc.getAttr(ns+self.evalOrderAttr,s=True)
			evalOrder = [(ns+mc.getAttr(ns+self.evalOrderAttr+'['+str(i)+']')) for i in range(evalOrderLen)]
			orderedSel = [str(i) for i in evalOrder if selection.count(i)]
		# Perform twin
		for master in orderedSel:
			dcXformList = copy.deepcopy(xformList)
			self.twin(master,xformList=dcXformList,customAttrList=userDefList)
	
	def swapSelection(self):
		'''
		Swap the current selected objects.
		'''
		# Get selection list
		selection =  mc.ls(sl=1,type=self.transform)
		# Get namespace
		ns = ''
		try:
			if selection[0].count(':'): ns = selection[0].split(':')[0]+':'
		except: pass
		# Get attr selection
		xformList = self.getCBxformList()
		userDefList = self.getCBuserDefList()
		
		# Get selection list in order of evaluation
		evalOrder = selection
		if mc.objExists(ns+self.evalOrderAttr):
			evalOrderLen = mc.getAttr(ns+self.evalOrderAttr,s=True)
			evalOrder = [(ns+mc.getAttr(ns+self.evalOrderAttr+'['+str(i)+']')) for i in range(evalOrderLen)]
		
		# Get list of master controls
		masterList = []
		for obj in selection:
			master = obj.replace(ns+self.leftPrefix,ns+self.rightPrefix)
			if not mc.objExists(master+'.'+self.twinAttr): continue
			if not masterList.count(master): masterList.append(master)
		masterEvalOrder = [str(i) for i in evalOrder if masterList.count(i)]
		
		# Get list of slave controls
		slaveList = []
		for master in masterList:
			try: slave = ns+str(mc.getAttr(master+'.'+self.twinAttr))
			except: continue
			if slave == master: continue
			if not (slaveList.count(slave) or masterList.count(slave)): slaveList.append(slave)
		slaveEvalOrder = [str(i) for i in evalOrder if slaveList.count(i)]
		
		# Get original slave transform values
		slaveOrigXformList = []
		slaveOrigCustomAttrList = []
		for slave in slaveEvalOrder:
			slaveOrigXformList.append(self.getTransformValues(slave))
			slaveOrigCustomAttrList.append(self.getCustomAttrValues(slave))
		
		# Perform twin
		for master in masterEvalOrder:
			dcXformList = copy.deepcopy(xformList)
			self.twin(master,xformList=dcXformList,customAttrList=userDefList)
		
		# Get twined slave transform values
		slaveTwinXformList = []
		slaveTwinCustomAttrList = []
		for slave in slaveEvalOrder:
			slaveTwinXformList.append(self.getTransformValues(slave))
			slaveTwinCustomAttrList.append(self.getCustomAttrValues(slave))
		
		# Restore original slave transform values
		for i in range(len(slaveEvalOrder)):
			self.setTransformValues(slaveEvalOrder[i],slaveOrigXformList[i])
			self.setCustomAttrValues(slaveEvalOrder[i],slaveOrigCustomAttrList[i])
			
		# Perform slave twin
		for slave in slaveEvalOrder:
			dcXformList = copy.deepcopy(xformList)
			self.twin(slave,xformList=dcXformList,customAttrList=userDefList)
		
		# Restore twined slave transform values
		for i in range(len(slaveEvalOrder)):
			self.setTransformValues(slaveEvalOrder[i],slaveTwinXformList[i])
			self.setCustomAttrValues(slaveEvalOrder[i],slaveTwinCustomAttrList[i])
	
	def selectTwin(self):
		'''
		Select the twin of the currectly selected object
		'''
		selection =  mc.ls(sl=1,type=self.transform)
		twinList = []
		for obj in selection:
			# Get twin name string
			twin = str(mc.getAttr(master+'.'+self.twinAttr))
			# Check namespace
			ns = ''
			if obj.count(':'):
				try: ns = obj.split(':')[0]+':'
				except: pass
				else:
					if not twin.startswith(ns): twin = ns+twin
			twinList.append(twin)
		mc.select(twinList,r=True)
	
	#----------
	# UTILITIY
	#----------
	
	def transformVector(self,vector=[0,0,0],transform=OpenMaya.MMatrix.identity,transformAsPoint=False,invertTransform=False):
		'''
		Transform a vector (or point) by a given transformation matrix.
		@param vector: Vector or point to be transformed
		@type vector: list
		@param transform: Transform object or MMatrix obect to provide the transformation
		@type transform: str or OpenMaya.MMatrix
		@param transformAsPoint: Transform the vector as a point
		@type transformAsPoint: bool
		@param invertTransform: Use the matrix inverse to transform the vector
		@type invertTransform: bool
		'''
		# Create MPoint/MVector object for transformation
		if transformAsPoint: vector = OpenMaya.MPoint(vector[0],vector[1],vector[2],1.0)
		else: vector = OpenMaya.MVector(vector[0],vector[1],vector[2])
		
		# Check Local Space
		transformMatrix = OpenMaya.MMatrix()
		if type(transform) == str or type(transform) == unicode:
			# Get transformation matrix
			transformMatrix = self.getTransformMatrix(transform,parentSpace=False)
		else:
			# Check input is of type MMatrix
			if type(transform) != OpenMaya.MMatrix:
				raise UserInputError('"Transform" input variable is not of expected type! Expecting string or MMatrix, received '+str(type(transform))+'!!')
		
		# Transform vector
		if transformMatrix != OpenMaya.MMatrix.identity:
			if invertTransform: vector *= transformMatrix.inverse()
			else: vector *= transformMatrix
		
		# Return new vector
		return [vector.x,vector.y,vector.z]
	
	def getTransformMatrix(self,transform='',parentSpace=False):
		'''
		Return an MTransformationMatrix of the specified transform
		@param transform: The transform to query
		@type transform: str
		@param parentSpace: Return the parent (local) space intead of object space
		@type parentSpace: bool
		'''
		# Check object exists
		if not mc.objExists(transform): raise UserInputError('Local space object '+transform+' does not exists!')
		if not self.transform.count(mc.objectType(transform)): transform = mc.listRelatives(transform,p=True)[0]
		
		# Get selectionList
		sel = OpenMaya.MSelectionList()
		OpenMaya.MGlobal.getSelectionListByName(transform,sel)
		
		# Get DagPath to localSpace object
		transformPath = OpenMaya.MDagPath()
		sel.getDagPath(0,transformPath)
		
		# Step up to parent path
		if parentSpace: transformPath.pop(1)
		
		# Return transformation matrix
		return transformPath.inclusiveMatrix()
	
	def vectorTwinSpaceMirror(self,vector,master,twin,pivot,axis):
		'''
		Transform a vector to twin local space after mirroring across the pivot object's specified axis
		@param vector: The vector to be transformed
		@type vector: list
		@param master: Vectors initial local space object (parent)
		@type master: string
		@param twin: Vectors destination local space object
		@type twin: string
		@param pivot: Pivot object across which the vector will be mirrored
		@type pivot: string
		@param axis: Axis across which the vector will be mirrored
		@type axis: string or int
		'''
		# Check inputs
		if not mc.objExists(master): raise UserInputError('Master object '+master+' does not exist')
		if not mc.objExists(twin): raise UserInputError('Twin object '+twin+' does not exist')
		if not mc.objExists(pivot): raise UserInputError('Pivot object '+pivot+' does not exist')
		
		# Get Twin Parent
		twinParent = ''
		try: twinParent = str(mc.listRelatives(twin,p=1)[0])
		except: pass
		
		if type(axis) == str: axis = self.axisIndex[axis]
		
		# Get vector in world space
		vector = self.transformVector(vector,master,transformAsPoint=False,invertTransform=False)
		# Mirror vector across pivot axis
		vector = self.transformVector(vector,pivot,transformAsPoint=False,invertTransform=True)
		vector[axis] *= -1
		vector = self.transformVector(vector,pivot,transformAsPoint=False,invertTransform=False)
		# Get axis in local twin local space
		if twinParent: vector = self.transformVector(vector,twinParent,transformAsPoint=False,invertTransform=True)
		
		# Compensate for joint orientation
		if mc.objectType(twin) == 'joint':
			jointOrient = mc.getAttr(twin+'.jointOrient')[0]
			jointOrient = [jointOrient[i]/self.radian for i in range(3)]
			jointOrientMatrix = OpenMaya.MEulerRotation(jointOrient[0],jointOrient[1],jointOrient[2],0).asMatrix()
			vector = OpenMaya.MVector(vector[0],vector[1],vector[2]) * jointOrientMatrix.inverse()
		
		return vector
	
	def getTransformValues(self,obj):
		'''
		Return a list of transform values for the specified maya transform object
		@param obj: Maya transform object to query local space values from
		@type obj: str
		'''
		return [mc.getAttr(obj+'.'+self.xform[i]) for i in range(9)]
		
	def setTransformValues(self,obj,xformList=[0,0,0,0,0,0,1,1,1]):
		'''
		Set transform values for the specified maya transform object from the input value list
		@param obj: Maya transform object to set local space values for
		@type obj: str
		'''
		for i in range(9):
			if mc.getAttr(obj+'.'+self.xform[i],se=True): mc.setAttr(obj+'.'+self.xform[i],xformList[i])
	
	def getCustomAttrValues(self,obj):
		'''
		Return a list of custom attribute values for the specified maya transform object
		@param obj: Maya transform object to query custom attribute values from
		@type obj: str
		'''
		customAttrVals = {}
		customAttrList = mc.listAttr(obj,k=True,ud=True)
		if customAttrList:
			for attr in customAttrList: customAttrVals[attr] = mc.getAttr(obj+'.'+attr)
		return customAttrVals
	
	def setCustomAttrValues(self,obj,customAttrVals={}):
		'''
		Return a list of custom attribute values for the specified maya transform object
		@param obj: Maya transform object to query custom attribute values from
		@type obj: str
		'''
		for attr in customAttrVals.iterkeys():
			if not mc.objExists(obj+'.'+attr): continue
			if not mc.getAttr(obj+'.'+attr,k=True): continue
			mc.setAttr(obj+'.'+attr,customAttrVals[attr])
	
	def getCBattrList(self):
		'''
		Return a list of selected attributes from the channel box.
		If nothing is selected, returns an empty list
		'''
		cbAttrList = mc.channelBox(self.channelBox,q=True,selectedMainAttributes=True)
		if not cbAttrList: cbAttrList = []
		return cbAttrList
	
	def getCBxformList(self):
		'''
		Get an (boolean) integer list representing the selected transform attributes from the channel box.
		'''
		cbAttrList = self.getCBattrList()
		xformList = [1,1,1,1,1,1,1,1,1]
		if cbAttrList: xformList = [cbAttrList.count(self.xform[i]) for i in range(9)]
		return xformList
	
	def getCBuserDefList(self):
		'''
		Get a list of selected user defined attributes from the channel box.
		'''
		cbAttrList = self.getCBattrList()
		xformList = self.xform
		xformList.append('v')
		usedDefList = ['all']
		if cbAttrList: usedDefList = [attr for attr in cbAttrList if not xformList.count(attr)]
		return usedDefList
	
	#-------
	# SETUP
	#-------
	
	def setSelfPivotAttrs(self,pivotList,axis='x',mode=0):
		'''
		Setup self pivot pose matching attributes for the specified controls
		@param pivotList: List of controls to setup pose match attribute values for
		@type pivotList: list
		@param axis: Axis across which the match position for the control will be projected
		@type axis: str
		@param mode: Specifies local or world pose matching. 0=World 1=Local
		@type mode: int
		'''
		for pivot in pivotList:
			if not mc.objExists(pivot): raise UserInputError('Pivot object '+pivot+' does not exist!!')
			else: self.setMatchAttrs(pivot,pivot,pivot,axis,mode)
	
	def setTwinMatchAttrs(self,masterList,pivot,axis='x',mode=0,search='lf_',replace='rt_'):
		'''
		Setup twin pose matching attributes for the specified controls
		@param masterList: List of controls to setup pose match attribute values for
		@type masterList: list
		@param pivot: Pivot object for current control
		@type pivot: str
		@param axis: Axis across which the match position for the control will be projected
		@type axis: str
		@param mode: Specifies local or world pose matching. 0=World 1=Local
		@type mode: int
		'''
		if not mc.objExists(pivot): raise UserInputError('Pivot object '+pivot+' does not exist!!')
		for master in masterList:
			if not mc.objExists(master): raise UserInputError('Control object '+master+' does not exist!!')
			twin = master
			if master.startswith(search):
				twin = master.replace(search,replace)
			elif master.startswith(replace):
				continue
				#twin = master.replace(replace,search)
			self.setMatchAttrs(master,twin,pivot,axis,mode)
			self.setMatchAttrs(twin,master,pivot,axis,mode)
	
	def setModeAttr(self,controlList,mode):
		'''
		Set pose match mode attribute for the specified controls
		@param controlList: List of control to set mode attribute for
		@type controlList: list
		@param mode: Specifies local or world pose matching. 0=World 1=Local
		@type mode: int
		'''
		for control in controlList:
			if mc.objExists(control+'.matchMode'): mc.setAttr(control+'.matchMode',mode)
			else: print('Control object '+control+' does not have a "matchMode" attribute! Run Match.setMatchAttrs()!!')
	
	def removeOldAttrs(self,controlList):
		'''
		Remove old match attributes from the specified objects.
		@param controlList: List of control to remove old match attributes from
		@type controlList: list
		'''
		for control in controlList:
			if mc.objExists(control+'.matchLevel'): mc.deleteAttr(control,at='matchLevel')
			if mc.objExists(control+'.pivotDefault'): mc.deleteAttr(control,at='pivotDefault')
			if mc.objExists(control+'.matchX'): mc.deleteAttr(control,at='matchX')
			if mc.objExists(control+'.matchY'): mc.deleteAttr(control,at='matchY')
			if mc.objExists(control+'.matchZ'): mc.deleteAttr(control,at='matchZ')
	
	def setMatchAttrs(self,master,twin,pivot,axis,mode=0,twinX='',twinY='',twinZ=''):
		'''
		Set match attribute values.
		If attributes don't already exist, they will becreated and set to the specified values
		@param master: Master object to set match attribute values for
		@type master: str
		@param twin: Match slave control for current control
		@type twin: str
		@param pivot: Pivot object for current control
		@type pivot: str
		@param axis: Axis across which the match position for the slave will be projected
		@type axis: str
		@param mode: Specifies local or world pose matching. 0=World 1=Local
		@type mode: str
		@param twinX: Override the default value to manually set the twin mirror xAxis. Leave as default to calculate automatically
		@type twinX: str
		@param twinY: Override the default value to manually set the twin mirror yAxis. Leave as default to calculate automatically
		@type twinY: str
		@param twinZ: Override the default value to manually set the twin mirror zAxis. Leave as default to calculate automatically
		@type twinZ: str
		'''
		# 
		master = str(master)
		twin = str(twin)
		pivot = str(pivot)
		
		# Check inputs
		if not mc.objExists(master): raise UserInputError('Master object '+master+' does not exist')
		if not mc.objExists(twin): raise UserInputError('Twin object '+twin+' does not exist')
		if not mc.objExists(pivot): raise UserInputError('Pivot object '+pivot+' does not exist')
		
		# Twin
		if not mc.objExists(master+'.'+self.twinAttr):
			mc.addAttr(master,ln=self.twinAttr,dt='string')
		mc.setAttr(master+'.'+self.twinAttr,twin,type='string')
		
		# Pivot
		if not mc.objExists(master+'.'+self.pivotAttr):
			mc.addAttr(master,ln=self.pivotAttr,dt='string')
		mc.setAttr(master+'.'+self.pivotAttr,pivot,type='string')
		
		# Axis
		if not mc.objExists(master+'.'+self.axisAttr):
			mc.addAttr(master,ln=self.axisAttr,at='enum',en="X:Y:Z")
		mc.setAttr(master+'.'+self.axisAttr,self.axisIndex[axis])
		
		# Mode
		if not mc.objExists(master+'.'+self.modeAttr):
			mc.addAttr(master,ln=self.modeAttr,at='enum',en="World:Local")
		mc.setAttr(master+'.'+self.modeAttr,mode)
		
		# Twin XYZ
		twinAttrVal = self.getTwinMirrorAxis(master,twin,pivot,axis)
		# X Axis
		if not mc.objExists(master+'.'+self.twinXAttr):
			mc.addAttr(master,ln=self.twinXAttr,at='enum',en="X:Y:Z:-X:-Y:-Z")
		if twinX: mc.setAttr(master+'.'+self.twinXAttr,self.axisIndex[twinX])
		else: mc.setAttr(master+'.'+self.twinXAttr,twinAttrVal[0])
		# Y Axis
		if not mc.objExists(master+'.'+self.twinYAttr):
			mc.addAttr(master,ln=self.twinYAttr,at='enum',en="X:Y:Z:-X:-Y:-Z")
		if twinY: mc.setAttr(master+'.'+self.twinYAttr,self.axisIndex[twinY])
		else: mc.setAttr(master+'.'+self.twinYAttr,twinAttrVal[1])
		# Z Axis
		if not mc.objExists(master+'.'+self.twinZAttr):
			mc.addAttr(master,ln=self.twinZAttr,at='enum',en="X:Y:Z:-X:-Y:-Z")
		if twinZ: mc.setAttr(master+'.'+self.twinZAttr,self.axisIndex[twinZ])
		else: mc.setAttr(master+'.'+self.twinZAttr,twinAttrVal[2])
	
	def getTwinMirrorAxis(self,master,twin,pivot,axis):
		'''
		Returns the mirrired twin axis' (XYZ) for a specified slave control, based on a master, pivot and mirror axis
		@param master: Twin master object that will provide the basis vectors to be mirrored
		@type master: str
		@param twin: Twin slave object that will be used for the mirrored basis vector comparison
		@type twin: str
		@param pivot: Pivot object that will be used as the axis mirror pivot
		@type pivot: str
		@param axis: Axis across which the master basis vectors will be mirrored
		@type axis: str
		'''
		# Check inputs
		if not mc.objExists(master): raise UserInputError('Master object '+master+' does not exist')
		if not mc.objExists(twin): raise UserInputError('Twin object '+twin+' does not exist')
		if not mc.objExists(pivot): raise UserInputError('Pivot object '+pivot+' does not exist')
		
		# Initialize mirror axis
		twinMirrorAxis = [0,1,2]
		
		# X Axis
		# -------
		xAxis = self.vectorTwinSpaceMirror(self.xAxis,master,twin,pivot,axis)
		# Determine mirror axis
		axisMirror = 'x'
		if abs(xAxis[self.axisIndex[axisMirror]]) < abs(xAxis[1]): axisMirror = 'y'
		if abs(xAxis[self.axisIndex[axisMirror]]) < abs(xAxis[2]): axisMirror = 'z'
		if xAxis[self.axisIndex[axisMirror]] < 0: axisMirror = '-'+axisMirror
		twinMirrorAxis[0] = self.axisIndex[axisMirror]
		
		# Y Axis
		# -------
		yAxis = self.vectorTwinSpaceMirror(self.yAxis,master,twin,pivot,axis)
		# Determine mirror axis
		axisMirror = 'x'
		if abs(yAxis[self.axisIndex[axisMirror]]) < abs(yAxis[1]): axisMirror = 'y'
		if abs(yAxis[self.axisIndex[axisMirror]]) < abs(yAxis[2]): axisMirror = 'z'
		if yAxis[self.axisIndex[axisMirror]] < 0: axisMirror = '-'+axisMirror
		twinMirrorAxis[1] = self.axisIndex[axisMirror]
		
		# Z Axis
		# -------
		zAxis = self.vectorTwinSpaceMirror(self.zAxis,master,twin,pivot,axis)
		# Determine mirror axis
		axisMirror = 'x'
		if abs(zAxis[self.axisIndex[axisMirror]]) < abs(zAxis[1]): axisMirror = 'y'
		if abs(zAxis[self.axisIndex[axisMirror]]) < abs(zAxis[2]): axisMirror = 'z'
		if zAxis[self.axisIndex[axisMirror]] < 0: axisMirror = '-'+axisMirror
		twinMirrorAxis[2] = self.axisIndex[axisMirror]
		
		return twinMirrorAxis
	
