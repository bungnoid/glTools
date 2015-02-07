import maya.cmds as mc

import glTools.utils.component
import glTools.utils.mathUtils
import glTools.utils.mesh

def getConnectedEdges(edgeList):
	'''
	Partition Edge IDs based on connectivity.
	@param edgeList: Polygon mesh edge list to partition based on connectivity
	@type edgeList: list
	'''
	# Check Edge List
	if not edgeList: raise Exception('Invalid or empty edge list!')
	edgeList = mc.filterExpand(edgeList,ex=True,sm=32) or []
	if not edgeList: raise Exception('Invalid edge list! List of polygon edges required...')
	
	# Get Mesh from Edges
	mesh = list(set(mc.ls(edgeList,o=True) or []))
	if len(mesh) > 1:
		print mesh
		raise Exception('Edges from multiple mesh shapes were supplied!')
	mesh = mesh[0]
	
	# Get Edge and Vertex IDs
	edgeIDs = glTools.utils.component.singleIndexList(edgeList)
	vertIDs = [glTools.utils.mesh.getEdgeVertexIndices(mesh,i) for i in edgeIDs]
	
	# Sort Edge IDs based on Connectivity
	connectedEdges = []
	connectedVerts = []
	escape = 0
	while edgeIDs:
		
		# Move First Edge to Connected List
		connectedEdges.append([edgeIDs[0]])
		connectedVerts.extend([vertIDs[0]])
		del edgeIDs[0]
		del vertIDs[0]
		
		# Initialize Connected Status
		connected = True
		while connected:
			
			# Reset Connected Status
			connected = False
			
			# Add Connected Edges
			for i in range(len(edgeIDs)):
				escape += 1
				if list(set(connectedVerts[-1]) & set(vertIDs[i])):
					connected = True
					connectedEdges[-1].append(edgeIDs[i])
					connectedVerts[-1].extend(vertIDs[i])
					del edgeIDs[i]
					del vertIDs[i]
					break
		
		# Check Crazy Iteration Count
		if escape > 100000000: break
	
	# Return Result
	return connectedEdges

def extractEdgeCurves(edgeList,form=2,degree=1,keepHistory=True):
	'''
	Extract mesh edges as nurbs curves.
	@param edgeList: Geometry to get shading group from
	@type edgeList: list
	@param form: Curve form. 0=Open, 1=Periodic, 2=Best Guess
	@type form: int
	@param degree: Curve degree
	@type degree: int
	@param keepHistory: Maintain polyToCurve construction nodes
	@type keepHistory: bool
	'''
	# Check Edge List
	if not edgeList:
		raise Exception('Invalid or empty edge list! Unable to extract edge curves...')
	
	# Partition Connected Edges
	connectedEdges = getConnectedEdges(edgeList)
	
	# Get Mesh from Edges
	mesh = mc.ls(edgeList,o=True)[0]
	
	# Extract Edge Curves
	crvList = []
	nodeList = []
	for connectedEdgeList in connectedEdges:
		edgeLine = [mesh+'.e['+str(i)+']' for i in connectedEdgeList]
		mc.select(edgeLine)
		polyToCurve = mc.polyToCurve(form=form,degree=degree,ch=keepHistory)
		crvList.append(polyToCurve[0])
		if keepHistory: nodeList.append(polyToCurve[1])
	
	# Return Result
	mc.select(crvList)
	return crvList
