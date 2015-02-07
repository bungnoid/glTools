'''
@newfield input: Input, Inputs
@newfield inputType: Input Type, Input Types
@newfield output: Output, Outputs
@newfield outputType: Output Type, Output Types
'''

import maya.cmds as mc
import maya.mel as mm

import glTools.utils.base
import glTools.utils.curve
import glTools.utils.stringUtils

def create(	path,
			objectType,
			num=0,
			parent=False,
			useDist=False,
			min=0.0,
			max=1.0,
			prefix=''	):
	'''
	Create objects along a curve
	
	# INPUTS:
	@input path: Input nurbs curve path
	@inputType path: str
	@input objectType: Type of objects to create and place along path
	@inputType objectType: str
	@input num: Number of objects to create along path. If num=0, number of edit points will be used.
	@inputType num: int
	@input parent: Parent each new object to the previously created object. eg. Joint chain
	@inputType parent: bool
	@input useDist: Use distance along curve instead of parametric length for sample distribution
	@inputType useDist: bool
	@input min: Percent along the path to start placing objects
	@inputType min: float
	@input max: Percent along the path to stop placing objects
	@inputType max: float
	@input prefix: Name prefix for builder created nodes. If left at default ("") prefix will be derived from path name.
	@inputType prefix: str
	
	# OUTPUTS:
	@output outObjectList: List of objects placed along path
	@outputType outObjectList: list
	'''
	
	# Check Path
	if not glTools.utils.curve.isCurve(path):
		raise Exception('Path object '+path+' is not a valid nurbs curve!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(path)
	
	# Check object count
	if not num: num = mc.getAttr(path+'.spans') + 1
	
	# Get curve sample points
	paramList = glTools.utils.curve.sampleParam(path,num,useDist,min,max)
	
	# Create object along path
	objList = []
	for i in range(num):
		
		# Get string index
		ind = glTools.utils.stringUtils.stringIndex(i+1)
		
		# Create object
		obj = mc.createNode(objectType,n=prefix+ind+'_'+objectType)
		if not glTools.utils.base.isTransform(obj): obj = mc.listRelatives(obj,p=True,pa=True)[0]
		
		# Position
		pos = mc.pointOnCurve(path,pr=paramList[i])
		mc.xform(obj,t=pos,ws=True)
		
		# Parent
		if parent and i: obj = mc.parent(obj,objList[-1])[0]
		
		# Orient Joint
		if objectType == 'joint' and i: mc.joint(objList[-1],e=True,zso=True,oj='xyz',sao='yup')
		
		# Append result
		objList.append( str(obj) )
	
	# Return result
	return objList
