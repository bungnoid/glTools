import maya.cmds as mc
import glTools.common.namingConvention
import glTools.common.arrayUtilities

class UserInputError( Exception ): pass

class Tag( object ):
	
	def __init__(self):
		#
		self.nameTagAttr = 'nameTag'
	
	def addNameTag(self,control,tag):
		'''
		Set the name tag value for the specified control
		'''
		
		# Check control
		if not mc.objExists(control): raise UserInputError('Object '+control+' does not exist!')
		
		# Add Tag attribute
		if mc.objExists(control+'.'+self.nameTagAttr):
			mc.addAttr(control,ln=self.nameTagAttr,dt='string')
		mc.setAttr(control+'.'+self.nameTagAttr,tag,type='string')
	
	def getNameTag(self,control):
		'''
		Return the name tag value of the specified control
		'''
		
		# Check control
		if not mc.objExists(control): raise UserInputError('Object '+control+' does not exist!')
		# Check tag attribute
		if not mc.objExists(control+'.'+self.nameTagAttr): raise UserInputError('Object '+control+' does not have a "'+self.nameTagAttr+'" attribute!')
		# Return tag string value
		return mc.getAttr(control+'.'+self.nameTagAttr)
	
	def guessNameTag(self,control,side=True,part=True,optSide=True,subPart=True,node=False):
		'''    
		Return a best guess name tag based on a controls current name.
		Uses name element comparison to our naming convention module.
		'''
		tag = ''
		
		# Get naming convention dictionaries
		nameConvention = glTools.common.namingConvention.NamingConvention()
		arrayUtil = glTools.common.arrayUtilities.ArrayUtilities()
		sideDict = arrayUtil.swapKeyValuePairs(nameConvention.side)
		partDict = arrayUtil.swapKeyValuePairs(nameConvention.part)
		subPartDict = arrayUtil.swapKeyValuePairs(nameConvention.subPart)
		nodeDict = arrayUtil.swapKeyValuePairs(nameConvention.node)
		
		# Get name elements
		controlElem = control.split(nameConvention.delineator)
		controlElemCnt = len(controlElem)
		controlElemInd = 0
		
		# Check number of elements
		if controlElemCnt < 3: print 'Warning: Name pattern does not match naming convention'
		
		# Get side
		if side and sideDict.has_key(controlElem[controlElemInd]):
			if controlElem[controlElemInd] != nameConvention.side['center']:
				tag += sideDict[controlElem[controlElemInd]].capitalize()
			controlElemInd += 1
		else: return
		# Get part
		if part and partDict.has_key(controlElem[controlElemInd][0:-2]):
			tag += partDict[controlElem[controlElemInd][0:-2]].capitalize()
			controlElemInd += 1
		else: return
		# Get optional side
		if optSide and sideDict.has_key(controlElem[controlElemInd][0:-2]):
			tag += sideDict[controlElem[controlElemInd][0:-2]].capitalize()
			controlElemInd += 1
		# Get sub-part
		if subPart and subPartDict.has_key(controlElem[controlElemInd][0:-2]):
			tag += subPartDict[controlElem[controlElemInd][0:-2]].capitalize()
			controlElemInd += 1
		# Get type
		if node and nodeDict.has_key(controlElem[controlElemInd]):
			tag += nodeDict[controlElem[controlElemInd]].capitalize()
		
		return tag
