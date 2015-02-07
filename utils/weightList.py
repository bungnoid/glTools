import maya.cmds as mc

import types

import cPickle
import os.path

class WeightList(list):
	
	'''
	to do : remap(0,1), normalize(), smooth()
	'''
	
	FILE_FILTER = "All Files (*.*)"
	
	#=============================
	# Checks
	#=============================
	def _initialChecks(self, other):
		
		self._extraElements=[]
		self._scalar=False
		
		self._checkType(other)
		self._checkLength(other)
	
	def _checkType(self, other):
		if isinstance(other,types.FloatType) or isinstance(other,types.IntType):
			self._scalar=True
			
	def _checkLength(self, other):
		if self._scalar : return
		
		if len(self) < len(other):
			self._extraElements = other[len(self):]
		elif len(self) > len(other):
			self._extraElements = self[len(other):]
	
	#=============================
	# Utilities
	#=============================
	
	def _addExtraElements(self, other):
		other.extend(self._extraElements)
		return WeightList(other)
	
	#=============================
	# Modifiers
	#=============================
	
	def clamp(self, clampMin=0, clampMax=1):
		self = [max( clampMin, min(i, clampMax)) for i in self ]
		return self

	def normalize(self, normalizeMin=0, normalizeMax=1):
		old_min = min(self)
		old_range = max(self) - old_min
		self = WeightList([(n - old_min) / old_range * normalizeMax + normalizeMin for n in self])
		return self
	
	def invert(self):
		self = WeightList([1.0-i for i in self])
		return self
	
	#=============================
	# Operators
	#=============================
	
	def __add__(self,other):
		self._initialChecks(other)
		if self._scalar:
			return WeightList([i+other for i in self])
		else:
			return self._addExtraElements([i[0]+i[1] for i in zip(self,other)])

	def __sub__(self,other):
		self._initialChecks(other)
		if self._scalar:
			return WeightList([i-other for i in self])
		else:
			return self._addExtraElements([i[0]-i[1] for i in zip(self,other)])

	def __mul__(self,other):
		self._initialChecks(other)
		if self._scalar:
			return WeightList([i*other for i in self])
		else:
			return self._addExtraElements([i[0]*i[1] for i in zip(self,other)])
			
	# needs a 0 check
	def __div__(self,other):
		self._initialChecks(other)
		if self._scalar:
			return WeightList([i/other for i in self])
		else:
			return self._addExtraElements([i[0]/i[1] for i in zip(self,other)])
	
	
	def __iadd__(self,other):
		return WeightList(self.__add__(other))
		
	def __isub__(self,other):
		return WeightList(self.__sub__(other))
			
	def __imul__(self,other):
		return WeightList(self.__mul__(other))
		
	def __idiv__(self,other):
		return WeightList(self.__div__(other))
		
	def __radd__(self,other):
		return self.__add__(other)
		
	def __rsub__(self,other):
		return self.__sub__(other)
		
	def __rmul__(self,other):
		return self.__mul__(other)
		
	def __rdiv__(self,other):
		return self.__div__(other)
	
	
	# ===============
	# - SAVE / LOAD -
	# ===============
	
	def save(self,filePath,force=False):
		'''
		Save data object to file.
		@param filePath: Target file path.
		@type filePath: str
		@param force: Force save if file already exists. (Overwrite).
		@type force: bool
		'''
		# Check Directory Path
		dirpath = os.path.dirname(filePath)
		if not os.path.isdir(dirpath): os.makedirs(dirpath)
		
		# Check File Path
		if os.path.isfile(filePath) and not force:
			raise Exception('File "'+filePath+'" already exists! Use "force=True" to overwrite the existing file.')
		
		# Save File
		fileOut = open(filePath,'wb')
		cPickle.dump(self,fileOut)
		fileOut.close()
		
		# Print Message
		print('Saved '+self.__class__.__name__+': "'+filePath+'"')
		
		# Return Result
		return filePath
	
	def saveAs(self):
		'''
		Save data object to file.
		Opens a file dialog, to allow the user to specify a file path. 
		'''
		# Specify File Path
		filePath = mc.fileDialog2(fileFilter=self.FILE_FILTER,dialogStyle=2,fileMode=0,caption='Save As')
		
		# Check Path
		if not filePath: return
		filePath = filePath[0]
		
		# Save Data File
		filePath = self.save(filePath,force=True)
		
		# Return Result
		return filePath
	
	def load(self,filePath=''):
		'''
		Load data object from file.
		@param filePath: Target file path
		@type filePath: str
		'''
		# Check File Path
		if not filePath:
			filePath = mc.fileDialog2(fileFilter=self.FILE_FILTER,dialogStyle=2,fileMode=1,caption='Load Data File',okCaption='Load')
			if not filePath: return None
			filePath = filePath[0]
		else:
			if not os.path.isfile(filePath):
				raise Exception('File "'+filePath+'" does not exist!')
		
		# Open File
		fileIn = open(filePath,'rb')
		self = cPickle.load(fileIn)
		
		# Print Message
		print('Loaded '+self.__class__.__name__+': "'+filePath+'"')
		
		# Return Result
		return self	
		
