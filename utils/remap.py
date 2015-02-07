import maya.cmds as mc

import glTools.utils.attribute

import types

class Remap(object):
	'''
	Object wrapper for remapValue node in Maya.
	'''
	# CONSTANTS
	
	_REMAPSUFFIX = 'remap'
	
	def __init__(	self,
					remapName,
					inputValue	= None,
					inputMin	= None,
					inputMax	= None,
					outputMin	= None,
					outputMax	= None ):
		'''
		Remap object initilization
		@param remapName: RemapValue node name
		@type remapName: str
		@param inputValue: RemapValue input value or source plug. If None, leave at default
		@type inputValue: float or str or None
		@param inputMin: RemapValue node input minimum value. If None, leave at default
		@type inputMin: float or None
		@param inputMax: RemapValue node input maximum value. If None, leave at default
		@type inputMax: float or None
		@param outputMin: RemapValue node output minimum value. If None, leave at default
		@type outputMin: float or None
		@param outputMax: RemapValue node output maximum value. If None, leave at default
		@type outputMax: float or None
		'''
		# Checks Existing Node
		if mc.objExists('%s_%s' % (remapName,self._REMAPSUFFIX) ):
			# Use Existing Node
			self._name = '%s_%s' % (remapName,self._REMAPSUFFIX)
		else:
			# Create New Node
			self.create(remapName)
		
		# Set Input
		if(inputValue != None): self.setInput(inputValue)
		
		# Set Range
		self.setRange(inputMin,inputMax,outputMin,outputMax)
			
		# Initialize Index
		self.setIndex(0)
	
	def create(	self,name ):
		'''
		Create new remapValue node with the specified name
		@param name: New node name.
		@type name: str
		'''
		self._name = mc.createNode('remapValue', name='%s_%s' % (name, self._REMAPSUFFIX))
		return self._name
		
	#==================
	# get
	#==================
	def getName(self):
		return self._name
	
	def getIndex(self):
		return self._index
		
	#==================
	# set
	#==================
	
	def setAttribute(self,attr,value):
		'''
		Set remapValue node value or source plug.
		@param attrName: RemapValue attribute name to set value or source plug for.
		@type attrName: float or str
		@param value: RemapValue attribute value or source plug.
		@type value: int or float or str or None
		'''
		# Check None
		if(value == None): return
		
		# Check Numeric Input
		if isinstance(value,(types.IntType,types.FloatType)):
			
			# Set Numeric Attribute Value
			try: mc.setAttr(attr,value)
			except: raise Exception('Error setting remapValue attribute "'+attr+'" value!')
			return
		
		# Check String Input
		elif isinstance(value,types.StringTypes):
			
			# Connect External Plug
			if glTools.utils.attribute.isAttr(value):
				if not mc.isConnected(value,attr):
					try: mc.connectAttr(value,attr,f=True)
					except: raise Exception('Error connecting remapValue attribute ("'+value+'" >> "'+attr+'")!')
					return
				else:
					print('RemapValue node attribute "'+attr+'" already connected to source plug "'+inputValue+'"! Skipping...')
					return
			else:
				raise Exception('Source plug value is not a valid attribute! ("'+value+'")')
		
		# Invlaid Type
		raise Exception('Invalid value type specified for remapValue attribute "'+attr+'"! ('+str(type(value))+')!')
	
	def setInput(self, inputValue):
		'''
		Set remapValue node inputValue.
		@param inputValue: RemapValue node input value or source plug.
		@type inputValue: float or str
		'''
		attr = self._name+'.inputValue'
		self.setAttribute(attr,inputValue)
	
	def setInputMin(self,inputMin):
		'''
		Set remapValue node inputMin attribute value
		@param inputMin: RemapValue node input minimum value or source plug.
		@type inputMin: float or None
		'''
		attr = self._name+'.inputMin'
		self.setAttribute(attr,inputMin)
	
	def setInputMax(self,inputMax):
		'''
		Set remapValue node inputMax attribute value
		@param inputMax: Attribute Value to set.
		@type inputMax: float or None
		'''
		attr = self._name+'.inputMax'
		self.setAttribute(attr,inputMax)
	
	def setOutputMin(self,outputMin):
		'''
		Set remapValue node outputMin attribute value
		@param outputMin: Attribute Value to set.
		@type outputMin: float or None
		'''
		attr = self._name+'.outputMin'
		self.setAttribute(attr,outputMin)

	def setOutputMax(self,outputMax):
		'''
		Set remapValue node outputMax attribute value
		@param outputMax: Attribute Value to set.
		@type outputMax: float or None
		'''
		attr = self._name+'.outputMax'
		self.setAttribute(attr,outputMax)
	
	def setInputRange(	self,
						inputMin	= None,
						inputMax	= None ):
		'''
		Set remapValue node inputMin and inputMax attribute value
		@param inputMin: Attribute value to set for inputMin.
		@type inputMin: float or None
		@param inputMax: Attribute value to set for inputMax.
		@type inputMax: float or None
		'''
		if(inputMin != None): self.setInputMin(inputMin)
		if(inputMax != None): self.setInputMax(inputMax)
		
	def setOutputRange(	self,
						outputMin	= None,
						outputMax	= None ):
		'''
		Set remapValue node outputMin and outputMax attribute value
		@param outputMin: Attribute value to set for outputMin.
		@type outputMin: float or None
		@param outputMax: Attribute value to set for outputMax.
		@type outputMax: float or None
		'''
		if(outputMin != None): self.setOutputMin(outputMin)
		if(outputMax != None): self.setOutputMax(outputMax)
	
	def setRange(	self,
					inputMin	= None,
					inputMax	= None,
					outputMin	= None,
					outputMax	= None ):
		'''
		Set remapValue node inputMin, inputMax, outputMin, outputMax attribute value
		@param outputMin: Attribute value to set for outputMin.
		@type outputMin: float or None
		@param outputMax: Attribute value to set for outputMax.
		@type outputMax: float or None
		'''
		self.setInputRange(inputMin,inputMax)
		self.setOutputRange(outputMin,outputMax)
	
	def setPoint(	self,
					index,
					position		= None,
					value			= None,
					interpolation	= None):
		'''
		Set remap point on remapValue node.
		@param index: Remap point index.
		@type index: int or str
		@param position: Remap point position.
		@type position: float or str
		@param value: Remap point value.
		@type value: float or str
		@param interpolation: Remap point interpolation.
		@type interpolation: int or str
		'''
		# Set Index
		self.setIndex(index)
		# Set Position
		self.setPosition(position)
		# Set Value
		self.setValue(value)
		# Set Interpolation
		self.setInterpolation(interpolation)
			
	def setIndex(self,index):
		'''
		Set remapValue point index.
		@param index: RemapValue point index.
		@type index: int
		'''
		self._index = index
		self._indexedName = '%s.value[%s]' % (self._name, index)
		
	def setPosition(self,position):
		'''
		Set remapValue point position value.
		@param position: RemapValue point float position or source plug.
		@type position: float or str
		'''
		attr = self._indexedName+'.value_Position'
		self.setAttribute(attr,position)
	
	def setValue(self,value):
		'''
		Set remapValue point float value.
		@param value: RemapValue point float value or source plug.
		@type value: float or str
		'''
		attr = self._indexedName+'.value_FloatValue'
		self.setAttribute(attr,value)
		
	def setInterpolation(self,interpolation):
		'''
		Set remapValue point interpolation value.
		@param interpolation: RemapValue point interpolation value or source plug.
		@type interpolation: int or str
		'''
		attr = self._indexedName+'.value_Interp'
		self.setAttribute(attr,interpolation)
	
	def connectInput(self, objectAttrName):
		'''
		'''
		if not mc.isConnected(objectAttrName, '%s.inputValue' % self._name):
			mc.connectAttr(objectAttrName, '%s.inputValue' % self._name, force=True)
	
	def connectOutput(self,dstAttr):
		'''
		Connect remapValue node output to destination plug.
		@param dstAttr: Destination plug for remapValue node output.
		@type dstAttr: str
		'''
		# Checks
		if not glTools.utils.attribute.isAttr(dstAttr):
			raise Exception('Destination attribute "'+dstAttr+'" is not a valid attribute! Unable to establish output connection...')
		
		# Connect Output
		outAttr = self._name+'.outValue'
		if not mc.isConnected(outAttr,dstAttr):
			try: mc.connectAttr(outAttr,dstAttr,f=True)
			except: raise Exception('Error connecting remapValue output ("'+outAttr+'" >> "'+dstAttr+'")!')
		else:
			print('RemapValue node output "'+outAttr+'" already connected to destination plug "'+dstAttr+'"! Skipping...')
	

