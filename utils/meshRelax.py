import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.common.componentUtilities
import glTools.utils.mathUtils
import glTools.utils.curve
import glTools.utils.surface

class UserInputError(Exception): pass

def neighbour(vertexList,referenceObject,meshRelax):
	'''
	'''
	# Get meshRelax object and target plug
	sel = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(meshRelax,sel)
	meshRelaxObj = OpenMaya.MObject()
	sel.getDependNode(0,meshRelaxObj)
	meshRelaxNode = OpenMaya.MFnDependencyNode(meshRelaxObj)
	neighbourDataPlug = meshRelaxNode.findPlug('neighbourData')
	neighbourDataArrayPlug = neighbourDataPlug.elementByLogicalIndex(0)
	
	# Check reference object
	isCurve = True
	if not glTools.utils.curve.isCurve(referenceObject):
		isCurve = False
	elif not glTools.utils.curve.isSurface(referenceObject):
		raise UserInputError('Reference object must be a valid nurbs curve or surface!!')
	
	# Create neighbourData object
	neighbourData = OpenMaya.MVectorArray()
	
	# Get mesh and vertex list
	compUtil = glTools.common.componentUtilities.ComponentUtilities()
	mesh = compUtil.getComponentIndexList(vertexList).keys()[0]
	
	# Get vertexIterator for mesh
	sel = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(mesh,sel)
	meshObj = OpenMaya.MObject()
	sel.getDependNode(0,meshObj)
	meshIt = OpenMaya.MItMeshVertex(meshObj)
	
	# Get neighbour data
	for i in range(len(vertexList)):
		
		# Get current point
		pnt = mc.pointPosition(vertexList[i])
		pntId = compUtil.getComponentIndexList([vertexList[i]])[mesh][0]
		
		# Get closest U tangent
		if isCurve:
			u = glTools.utils.curve.closestPoint(referenceObject,pnt)
			tan = mc.pointOnCurve(referenceObject,pr=u,nt=True)
		else:
			uv = glTools.utils.surface.closestPoint(referenceObject,pnt)
			tan = mc.pointOnSurface(referenceObject,u=uv[0],v=uv[1],ntu=True)
		tangent = OpenMaya.MVector(tan[0],tan[1],tan[2])
		
		# Get neighbouring points
		n1 = mc.pickWalk(vertexList[i],d='up')[0]
		n1Id = compUtil.getComponentIndexList([n1])[mesh][0]
		n1Pt = mc.pointPosition(n1)
		n1Dist = glTools.utils.mathUtils.distanceBetween(pnt,n1Pt)
		
		n2 = mc.pickWalk(vertexList[i],d='down')[0]
		n2Id = compUtil.getComponentIndexList([n2])[mesh][0]
		n2Pt = mc.pointPosition(n2)
		n2Dist = glTools.utils.mathUtils.distanceBetween(pnt,n2Pt)
		
		# Build neighbour data vector
		tDist = n1Dist + n2Dist
		neighbourData.append(OpenMaya.MVector(float(pntId),n1Id+(n1Dist/tDist),n2Id+(n2Dist/tDist)))
	
	# Set value
	neighbourDataArrayPlug.setMObject(OpenMaya.MFnVectorArrayData().create(neighbourData))
