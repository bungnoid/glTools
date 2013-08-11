import maya.cmds as mc
import maya.mel as mm

import glTools.utils.channelState
import glTools.common.namingConvention

class OrientPivotUtilities(object):
	'''
	Class: OrientPivotUtilities
	'''
	def __init__(self):
		self.channelStateUtil = glTools.utils.channelState.ChannelState()
		self.namingConvention = glTools.common.namingConvention.NamingConvention()
	
	def setup(self,orient=''):
		'''
		Create and manipulate the orient pivot within the baseRig hierarchy.
		'''
		if not orient: orient = self.namingConvention.base['orient']
		orientShape = mc.listRelatives(orient,s=True,ni=True)[0]
		
		# create shape offset
		orientOffset = mc.createNode('transform',n=self.namingConvention.base['orientOffset'])
		transformGeo = mc.createNode('transformGeometry',n='orientOffset_tgn')
		mc.parent(orientOffset,orient)
		mc.connectAttr(orient+'.worldSpace[0]',transformGeo+'.inputGeometry',f=1)
		mc.connectAttr(orientOffset+'.matrix',transformGeo+'.transform',f=1)
		orientShape = mc.rename(orientShape,'orientShapeOrig')
		
		# set rotate pivot as keyable
		mc.setAttr(orient+'.rotatePivotX',k=1)
		mc.setAttr(orient+'.rotatePivotY',k=1)
		mc.setAttr(orient+'.rotatePivotZ',k=1)
		mc.setAttr(orient+'.rotatePivotTranslateX',k=1)
		mc.setAttr(orient+'.rotatePivotTranslateY',k=1)
		mc.setAttr(orient+'.rotatePivotTranslateZ',k=1)
		# connect scalePivot to rotatePivot
		mc.connectAttr(orient+'.rotatePivot',orient+'.scalePivot',f=1)
		mc.connectAttr(orient+'.rotatePivot',orientOffset+'.translate',f=1)
		
		# duplicate original orient
		orientDup = mc.duplicate(orient,rr=1,rc=1,)
		# delete duplicates decendant transforms
		orientDupChildList = mc.listRelatives(orientDup,c=1,type='transform')
		mc.delete(orientDupChildList)
		# parent duplicate shape to orient
		orientDupShape = mc.listRelatives(orientDup,s=1)
		mc.parent(orientDupShape[0],orient,s=1,r=1)
		mc.delete(orientDup)
		
		# connect shape offset to duplicate shape
		mc.connectAttr(transformGeo+'.outputGeometry',orientDupShape[0]+'.create',f=1)
		orientDupShape[0] = mc.rename(orientDupShape[0],'orientShape')
		mc.setAttr(orientShape+'.intermediateObject',1)
		
		# setup channel states
		self.channelStateUtil.setFlags([1,1,1,2,2,2,2,2,2,1],[orientOffset])
		self.channelStateUtil.set(1,[orientOffset])
		
		# Return result
		return orientOffset
	
	def set(self,snapTo,char=''):
		'''
		Set the orient pivot position within the baseRig hierarchy.
		@param snapTo: Object to snap orient pivot to.
		@type snapTo: str
		@param char: Namespace of the orient pivot to set.
		@type char: str
		'''
		orient = char+self.orient
		
		# set orient rotate pivot
		pos = mc.xform(snapTo,q=1,ws=1,rp=1)
		mc.xform(orient,ws=1,rp=(pos[0],pos[1],pos[2]))
		
		# set pivot key
		mc.setKeyframe(orient,at='rotatePivot')
		mc.setKeyframe(orient,at='rotatePivotTranslate')
		
		# force update
		mc.dgdirty(orient)
		
	def setFromSel(self,char=''):
		'''
		Set the orient pivot position within the baseRig hierarchy based on
		the position of the first selected object.
		@param char: Namespace of the orient pivot to set.
		@type char: str
		'''
		sel = mc.ls(sl=1)
		if type(sel) == list:
			self.set(sel[0],char)
		
	def reset(self,char=''):
		'''
		Reset the orient pivot position within the baseRig hierarchy.
		@param char: Namespace of the orient pivot to set.
		@type char: str
		'''
		orient = char+self.orient
		
		# set rotate pivot key
		mc.setAttr(orient+'.rotatePivot',0,0,0)
		mc.setAttr(orient+'.rotatePivotTranslate',0,0,0)
		
		# set pivot keys
		mc.setKeyframe(orient,at='rotatePivot',)
		mc.setKeyframe(orient,at='rotatePivotTranslate',)
		
		# force update
		mc.dgdirty(orient)
		
