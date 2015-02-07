import maya.cmds as mc

import glTools.utils.curve
import glTools.utils.stringUtils

def addLengthAttrs(attrObject,length=0.0):
	'''
	Add basic curve length attributes to the specified object
	@param attrObject: Object to add curve length attributes to
	@type attrObject: str
	@param length: Rest length value
	@type length: int or float
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(attrObject):
		raise Exception('Attribute object "'+attrObject+'" does not exist!')
	
	# ===========================
	# - Add Distance Attributes -
	# ===========================
	
	if not mc.attributeQuery('length',n=attrObject,ex=True):
		mc.addAttr(attrObject,ln='length',min=0,dv=dist,k=True)
	if not mc.attributeQuery('restLength',n=attrObject,ex=True):
		mc.addAttr(attrObject,ln='restLength',min=0,dv=dist,k=True)
	
	# =================
	# - Return Result -
	# =================
	
	return attrObject+'.length'

def curveLengthSetup(	curve,
						attrObject	= None,
						prefix		= None ):
	'''
	Create curve length calculation and result attribute fpr the specified curve.
	@param curve: Curve object to create length setup for
	@type curve: str
	@param attrObject: Object to add curve length attributes to
	@type attrObject: str or None
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not glTools.utils.curve.isCurve(curve):
		raise Exception('Object "'+curve+'" is not a valid curve!')
	
	if attrObject:
		if not mc.objExists(attrObject):
			raise Exception('Attribute object "'+attrObject+'" does not exist!')
	else: attrObject = curve
	
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	
	# ============================
	# - Build Curve Length Setup -
	# ============================
	
	curveInfo = mc.createNode('curveInfo',n=prefix+'_curveInfo')
	mc.connectAttr(curve+'.worldSpace[0]',curveInfo+'.inputCurve',f=True)
	crvLen = mc.getAttr(curveInfo+'.arcLength')
	
	# Add Length Attr
	lengthAttr = addLengthAttrs(attrObject,length=crvLen)
	
	# =================
	# - Return Result -
	# =================
	
	return lengthAttr,curveInfo

def curveLengthRemapOutput(	curve,
							minLength	= None,
							maxLength	= None,
							minValue	= 0.0,
							maxValue	= 1.0,
							restValue	= None,
							attrObject	= None,
							interpType	= 3,
							prefix		= None):
	'''
	Create curve length remap output setup for specified curve.
	@param curve: Curve object to create length setup for
	@type curve: str
	@param minLength: Minimum curve length
	@type minLength: float or None
	@param maxLength: Maximum curve length
	@type maxLength: float or None
	@param minValue: Minimum output value
	@type minValue: float
	@param maxValue: Maximum output value
	@type maxValue: float
	@param restValue: Rest length output value
	@type restValue: float or None
	@param attrObject: Object to add remap output attributes to
	@type attrObject: str or None
	@param interpType: Remap interpolation type. 0=None, 1=Linear, 2=Smooth, 3=Spline
	@type interpType: int
	@param prefix: Naming prefix
	@type prefix: str or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Curve
	if not glTools.utils.curve.isCurve(curve):
		raise Exception('Object "'+curve+'" is not a vlaid curve!')
	
	# Check Attribute Object
	if not attrObject: attrObject = curve
	
	# Prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	
	# Check Curve Length Setup
	crvLenAttr,lengthNode = curveLengthSetup(curve,attrObject,prefix)
	length = mc.getAttr(crvLenAttr)
	
	# ======================
	# - Build Length Remap -
	# ======================
	
	# Add Min/Max Length Attrs
	if minLength == None: minLength = 0
	if not mc.objExists(attrObject+'.minLength'):
		mc.addAttr(attrObject,ln='minLength',min=0,max=length,dv=minLength,k=True)
	if maxLength == None: maxLength = length*2
	if not mc.objExists(attrObject+'.maxLength'):
		mc.addAttr(attrObject,ln='maxLength',min=length,dv=maxLength,k=True)
	
	# Add Rest Value Attr
	if not restValue == None:
		if not mc.objExists(attrObject+'.restValue'):
			mc.addAttr(attrObject,ln='restValue',dv=restValue,k=True)
	
	# Add Min/Max Value Attr
	if not mc.attributeQuery('minValue',n=attrObject,ex=True):
		mc.addAttr(attrObject,ln='minValue',dv=minValue,k=True)
	if not mc.attributeQuery('maxValue',n=attrObject,ex=True):
		mc.addAttr(attrObject,ln='maxValue',dv=maxValue,k=True)
	
	# Build Remap Value
	remapNode = mc.createNode('remapValue',n=prefix+'_remapValue')
	mc.connectAttr(crvLenAttr,remapNode+'.inputValue',f=True)
	
	mc.setAttr(remapNode+'.value[0].value_Interp',interpType)
	mc.connectAttr(attrObject+'.minLength',remapNode+'.value[0].value_Position',f=True)
	mc.connectAttr(attrObject+'.minValue',remapNode+'.value[0].value_FloatValue',f=True)
	
	mc.setAttr(remapNode+'.value[1].value_Interp',interpType)
	mc.connectAttr(attrObject+'.maxLength',remapNode+'.value[1].value_Position',f=True)
	mc.connectAttr(attrObject+'.maxValue',remapNode+'.value[1].value_FloatValue',f=True)
	
	# Set Rest Value
	if not restValue == None:
		mc.setAttr(remapNode+'.value[2].value_Interp',interpType)
		mc.connectAttr(curve+'.restLength',remapNode+'.value[2].value_Position',f=True)
		mc.connectAttr(attrObject+'.restValue',remapNode+'.value[2].value_FloatValue',f=True)
	
	# Connect Output
	if not mc.objExists(attrObject+'.outValue'):
		mc.addAttr(attrObject,ln='outValue',dv=0.0,k=True)
	mc.connectAttr(remapNode+'.outValue',attrObject+'.outValue',f=True)
	outAttr = attrObject+'.outValue'
	
	# =================
	# - Return Result -
	# =================
	
	return outAttr,distNode,remapNode

def curveLengthAttach(	curve,
						targetAttr,
						inputMin	= 0.0,
						inputMax	= 1.0,
						outputMin	= 0.0,
						outputMax	= 1.0,
						prefix		= '' ):
	'''
	Attach the curve length of a specified curve to drive a given attribute value via a remapValue node.
	@param curve: Curve to use as the attribute driver
	@type curve: str
	@param targetAttr: Attribute to drive using the remaped curve length value
	@type targetAttr: str
	@param inputMinMax: Remap value input min anmax values
	@type inputMinMax: list
	@param outputMinMax: Remap value input min anmax values
	@type outputMinMax: list
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(targetAttr.replace('.','_'))
	
	# Check Target Attribute
	if not mc.objExists(targetAttr):
		raise Exception('Target attribute "'+targetAttr+'" does not exist!')
	
	# Check Curve
	if not glTools.utils.curve.isCurve(curve):
		raise Exception('Object "'+curve+'" is not a vlaid curve!')
	
	# Check Curve Length Setup
	if not mc.objExists(curve+'.length'): curveLengthSetup(curve,prefix)
	
	# ====================
	# - Build Remap Node -
	# ====================
	
	# Build Remap Node
	remapNode = mc.createNode('remapValue',n=prefix+'_remapValue')
	
	# Connect Remap Node
	curveLen = mc.getAttr(curve+'.curveLength')
	mc.connectAttr(curve+'.curveLength',remapNode+'.inputValue',f=True)
	
	# SetAttr
	mc.setAttr(remapNode+'.inputMin',inputMin)
	mc.setAttr(remapNode+'.inputMax',inputMax)
	mc.setAttr(remapNode+'.outputMin',outputMin)
	mc.setAttr(remapNode+'.outputMax',outputMax)
	
	# Connect Target Attribute
	mc.connectAttr(remapNode+'.outValue',targetAttr,f=True)
	
	# =================
	# - Return Result -
	# =================
	
	return remapNode

