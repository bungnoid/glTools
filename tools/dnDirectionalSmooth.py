import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.component
import glTools.utils.mathUtils
import glTools.utils.curve
import glTools.utils.surface

class UserInputError(Exception): pass

def setNeighbour(vertexList=[],referenceObject='',dnDirectionalSmoothNode='',direction='u'):
	'''
	'''
	# Flatten vertex list
	vertexList = mc.ls(vertexList,fl=True)
	
	# Get dnDirectionalSmoothNode object and target plug
	sel = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(dnDirectionalSmoothNode,sel)
	dnDirectionalSmoothNodeObj = OpenMaya.MObject()
	sel.getDependNode(0,dnDirectionalSmoothNodeObj)
	dnDirectionalSmoothNodeNode = OpenMaya.MFnDependencyNode(dnDirectionalSmoothNodeObj)
	neighbourDataPlug = dnDirectionalSmoothNodeNode.findPlug('neighbourData')
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
	mesh = glTools.utils.component.getComponentIndexList(vertexList).keys()[0]
	
	# Get vertexIterator for mesh
	sel = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getSelectionListByName(mesh,sel)
	meshObj = OpenMaya.MObject()
	sel.getDependNode(0,meshObj)
	meshIt = OpenMaya.MItMeshVertex(meshObj)
	
	# Get neighbour data
	neighbourIndexList = OpenMaya.MIntArray()
	for i in range(len(vertexList)):
		
		# Get current point
		pnt = mc.pointPosition(vertexList[i])
		pntId = glTools.utils.component.getComponentIndexList([vertexList[i]])[mesh][0]
		
		# Get closest U tangent
		if isCurve:
			u = glTools.utils.curve.closestPoint(referenceObject,pnt)
			tan = mc.pointOnCurve(referenceObject,pr=u,nt=True)
		else:
			uv = glTools.utils.surface.closestPoint(referenceObject,pnt)
			tan = [0,0,0]
			if direction == 'u':
				tan = mc.pointOnSurface(referenceObject,u=uv[0],v=uv[1],ntu=True)
			elif direction == 'v':
				tan = mc.pointOnSurface(referenceObject,u=uv[0],v=uv[1],ntv=True)
			else:
				raise Exception('Invalid direction value!')
		tan = glTools.utils.mathUtils.normalizeVector(tan)
		
		# Get neighbouring points
		conFaces = mc.ls(mc.polyListComponentConversion(vertexList[i],fv=True,tf=True),fl=True)
		conVerts = mc.ls(mc.polyListComponentConversion(conFaces,ff=True,tv=True),fl=True)
		conVertList = glTools.utils.component.getComponentIndexList(conVerts)[mesh]
		
		# Determine neighbours
		n1Id = -1
		n2Id = -1
		n1Dist = 0.5
		n2Dist = 0.5
		minDot = 0.0
		maxDot = 0.0
		# Iterate through connected verts
		for n in range(len(conVertList)):
			nPnt = mc.pointPosition(mesh+'.vtx['+str(conVertList[n])+']')
			dist = glTools.utils.mathUtils.offsetVector(pnt,nPnt)
			nDist = glTools.utils.mathUtils.normalizeVector(dist)
			dot = glTools.utils.mathUtils.dotProduct(tan,nDist)
			if dot > maxDot:
				n1Id = conVertList[n]
				n1Dist = glTools.utils.mathUtils.mag(dist)
				maxDot = dot
			if dot < minDot:
				n2Id = conVertList[n]
				n2Dist = glTools.utils.mathUtils.mag(dist)
				minDot = dot
		
		# Build neighbour data vector
		tDist = n1Dist + n2Dist
		n1Dist = 1.0 - (n1Dist/tDist)
		n2Dist = 1.0 - (n2Dist/tDist)
		neighbourData.append(OpenMaya.MVector(float(pntId),n1Id+n1Dist,n2Id+n2Dist))
	
	# Set value
	neighbourDataArrayPlug.setMObject(OpenMaya.MFnVectorArrayData().create(neighbourData))
	
	# Return result
	return neighbourData
