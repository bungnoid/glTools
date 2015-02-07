import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.tools.extractCurves

import glTools.utils.base
import glTools.utils.blendShape
import glTools.utils.component
import glTools.utils.mathUtils
import glTools.utils.mesh
import glTools.utils.wire

import copy

def straightenVerts(	edgeList,
						falloff			= 0.01,
						influence		= 1.0,
						snapToOriginal	= False,
						keepEdgeSpacing	= False,
						deleteHistory	= False ):
	'''
	Straighten specified polygon vertices.
	@param edgeList: List of polygon edges to straighten.
	@type edgeList: list
	@param falloff: Falloff distance around selected vertices.
	@type falloff: float
	@param snapToOriginal: Snap vertices back to closest point on original mesh.
	@type snapToOriginal: bool
	@param deleteHistory: Delete construction history.
	@type deleteHistory: bool
	'''
	# Get Edge List
	edgeList = mc.filterExpand(edgeList,ex=True,sm=32) or []
	if not edgeList:
		raise Exception('Invalid or empty edge list! Unable to straighten vertices...')
	
	# Build Edge Curve from Vertices
	edgeCrvList = glTools.tools.extractCurves.extractEdgeCurves(edgeList,keepHistory=False)
	straightCrvList = []
	for edgeCrv in edgeCrvList:
	
		# Build Straight Curve
		straightCrv = mc.rebuildCurve(	edgeCrv,
										ch	= False,
										rpo	= False,
										rt	= 0,
										end	= 1,
										kr	= False,
										kcp	= False,
										kep	= True,
										kt	= False,
										s	= 1,
										d	= 1,
										tol	= 0 )[0]
		
		# Rebuild Straight Curve
		dist = []
		total = 0.0
		params = []
		pts = glTools.utils.base.getMPointArray(edgeCrv)
		max = mc.getAttr(straightCrv+'.maxValue')
		if keepEdgeSpacing:
			for i in range(pts.length()-1):
				d = (pts[i]-pts[i+1]).length()
				dist.append(d)
				total += d
			for i in range(len(dist)):
				d = dist[i]/total*max
				if i: d += params[-1]
				params.append(d)
		else:
			params = glTools.utils.mathUtils.distributeValue(pts.length(),rangeEnd=max)[1:-1]
		
		params = [straightCrv+'.u['+str(i)+']' for i in params]
		mc.insertKnotCurve(params,ch=False,numberOfKnots=1,add=True,ib=False,rpo=True)
		
		# Snap To Mesh
		mesh = mc.ls(edgeList,o=True)[0]
		if snapToOriginal:
			pts = glTools.utils.component.getComponentStrList(straightCrv)
			glTools.utils.mesh.snapPtsToMesh(mesh,pts)
		
		# Append List
		straightCrvList.append(straightCrv)
	
	# =================
	# - Deform Points -
	# =================
	
	# Build Wire Deformer
	wire = glTools.utils.wire.createMulti(mesh,edgeCrvList,dropoffDist=falloff,prefix=mesh.split(':')[-1])
	mc.setAttr(wire[0]+'.rotation',0)
	
	# Blend to Straight Curve
	for i in range(len(edgeCrvList)):
		blendShape = glTools.utils.blendShape.create(baseGeo=edgeCrvList[i],targetGeo=[straightCrvList[i]])
		mc.setAttr(blendShape+'.'+straightCrvList[i],influence)
	
	# ==================
	# - Delete History -
	# ==================
	
	if deleteHistory:
		wireBaseList = glTools.utils.wire.getWireBase(wire[0])
		mc.delete(mesh,ch=True)
		for edgeCrv in edgeCrvList:
			if mc.objExists(edgeCrv):
				mc.delete(edgeCrv)
		for straightCrv in straightCrvList:
			if mc.objExists(straightCrv):
				mc.delete(straightCrv)
		for wireBase in wireBaseList:
			if mc.objExists(wireBase):
				mc.delete(wireBase)
	
	# =================
	# - Return Result -
	# =================
	
	if edgeList:
		mc.hilite(mesh)
		mc.select(edgeList)
	
	return edgeList

def straightenVertsUI():
	'''
	Straighten Vertices UI
	'''
	# Window
	window = 'straightenVertsUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Straighten Vertices',s=True)
	
	# Layout
	CL = mc.columnLayout()
	
	# UI Elements
	mc.floatSliderGrp('straightenVerts_falloffFSG',label='Falloff Distance',field=True,precision=3,minValue=0.0,maxValue=10.0,fieldMinValue=0.0,fieldMaxValue=100.0,value=0.01)
	mc.checkBoxGrp('straightenVerts_edgeSpacingCBG',label='Maintain Edge Spacing',numberOfCheckBoxes=1,v1=False)
	mc.checkBoxGrp('straightenVerts_snapToOrigCBG',label='Maintain Shape',numberOfCheckBoxes=1,v1=False) # columnWidth2=[100,165]
	mc.checkBoxGrp('straightenVerts_deleteHistoryCBG',label='Delete History',numberOfCheckBoxes=1,v1=False)
	mc.button('straightenVertsB',l='Straighten',w=390,c='glTools.model.straightenVerts.straightenVertsFromUI()')
	
	# Show Window
	mc.window(window,e=True,wh=[392,92])
	mc.showWindow(window)

def straightenVertsFromUI():
	'''
	Straighten Vertices From UI
	'''
	# Get Edge Selection
	sel = mc.ls(sl=True,fl=True)
	edges = mc.filterExpand(sel,ex=True,sm=32)
	verts = mc.filterExpand(sel,ex=True,sm=31)
	if not edges and verts:
		mc.select(verts)
		mm.eval('ConvertSelectionToContainedEdges')
		edges = mc.filterExpand(ex=True,sm=32)
	if not edges:
		print('Select a list of connected vertices or edges and run again...')
		return
	
	# Get Mesh from vertices
	mesh = mc.ls(edges,o=True)
	
	# Get UI Parameters
	falloff = mc.floatSliderGrp('straightenVerts_falloffFSG',q=True,value=True)
	edgeSpacing = mc.checkBoxGrp('straightenVerts_edgeSpacingCBG',q=True,v1=True)
	snapToOrig = mc.checkBoxGrp('straightenVerts_snapToOrigCBG',q=True,v1=True)
	delHistory = mc.checkBoxGrp('straightenVerts_deleteHistoryCBG',q=True,v1=True)
	
	# Straighten Vertices
	straightenVerts(	edgeList		= edges,
						falloff			= falloff,
						keepEdgeSpacing	= edgeSpacing,
						snapToOriginal	= snapToOrig,
						deleteHistory	= delHistory)
	
	# Restore Selection
	if sel:
		mc.selectMode(component=True)
		mc.selectType(edge=True)
		mc.hilite(mesh)
		mc.select(edges)

def evenEdgeSpacing(	edgeList,
						smooth			= 0,
						influence		= 1.0,
						snapToOrig		= False,
						deleteHistory	= False ):
	'''
	@param edgeList: List of polygon edges to evenly space
	@type edgeList: list
	@param smooth: Number of smooth iterations to apply
	@type smooth: int
	@param influence: Amount of result to apply to original vertex positions
	@type influence: float
	@param snapToOrig: Snap points back to original mesh
	@type snapToOrig: bool
	@param deleteHistory: Delete construction history.
	@type deleteHistory: bool
	'''
	# Get Edge List
	edgeList = mc.filterExpand(edgeList,ex=True,sm=32) or []
	if not edgeList:
		raise Exception('Invalid or empty edge list! Unable to even edge spacing...')
	
	edgeCrvList = glTools.tools.extractCurves.extractEdgeCurves(edgeList,keepHistory=False)
	evenCrvList = []
	for edgeCrv in edgeCrvList:
	
		# Rebuild Even Curve
		evenCrv = mc.rebuildCurve(	edgeCrv,
									ch	= False,
									rpo	= False,
									rt	= 0,
									end	= 1,
									kr	= False,
									kcp	= False,
									kep	= True,
									kt	= False,
									s	= 0,
									d	= 1,
									tol	= 0 )[0]
		
		# Smooth Curve
		if smooth: smoothCurve(evenCrv,smooth,True)
		
		# Snap To Mesh
		mesh = mc.ls(edgeList,o=True)[0]
		if snapToOrig:
			pts = glTools.utils.component.getComponentStrList(evenCrv)
			glTools.utils.mesh.snapPtsToMesh(mesh,pts)
		
		evenCrvList.append(evenCrv)
	
	# Apply Even Spacing to Mesh Edge Vertices
	wire = glTools.utils.wire.createMulti(mesh,edgeCrvList,dropoffDist=0.01,prefix=mesh.split(':')[-1])
	mc.setAttr(wire[0]+'.rotation',0)
	mc.setAttr(wire[0]+'.envelope',influence)
	
	# Blend to Even Curve
	for i in range(len(edgeCrvList)):
		blendShape = glTools.utils.blendShape.create(baseGeo=edgeCrvList[i],targetGeo=[evenCrvList[i]])
		mc.setAttr(blendShape+'.'+evenCrvList[i],1)
	
	# ==================
	# - Delete History -
	# ==================
	
	if deleteHistory:
		wireBaseList = glTools.utils.wire.getWireBase(wire[0])
		mc.delete(mesh,ch=True)
		for edgeCrv in edgeCrvList:
			if mc.objExists(edgeCrv):
				mc.delete(edgeCrv)
		for evenCrv in evenCrvList:
			if mc.objExists(evenCrv):
				mc.delete(evenCrv)
		for wireBase in wireBaseList:
			if mc.objExists(wireBase):
				mc.delete(wireBase)
	
	# =================
	# - Return Result -
	# =================
	
	if edgeList:
		mc.hilite(mesh)
		mc.select(edgeList)
	
	return edgeList

def evenEdgeSpacingUI():
	'''
	Even Edge Spacing UI
	'''
	# Window
	window = 'evenEdgeSpacingUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Even Edge Spacing',s=True)
	
	# Layout
	CL = mc.columnLayout()
	
	# UI Elements
	mc.intSliderGrp('evenEdgeSpacing_smoothISG',label='Smooth',field=True,minValue=0,maxValue=20,fieldMinValue=0,fieldMaxValue=100,value=4)
	mc.floatSliderGrp('evenEdgeSpacing_influenceFSG',label='Influence',field=True,minValue=0.0,maxValue=1.0,fieldMinValue=0.0,fieldMaxValue=1.0,value=1.0)
	mc.checkBoxGrp('evenEdgeSpacing_snapToOrigCBG',label='Maintain Shape',numberOfCheckBoxes=1,v1=False) # columnWidth2=[100,165]
	mc.checkBoxGrp('evenEdgeSpacing_deleteHistoryCBG',label='Delete History',numberOfCheckBoxes=1,v1=False)
	mc.button('evenEdgeSpacingB',l='Even Edge Spacing',w=390,c='glTools.model.straightenVerts.evenEdgeSpacingFromUI()')
	
	# Show Window
	mc.window(window,e=True,wh=[392,99])
	mc.showWindow(window)

def evenEdgeSpacingFromUI():
	'''
	Even Edge Spacing From UI
	'''
	# Get Edge Selection
	sel = mc.ls(sl=True,fl=True)
	edges = mc.filterExpand(sel,ex=True,sm=32)
	verts = mc.filterExpand(sel,ex=True,sm=31)
	if not edges and verts:
		mc.select(verts)
		mm.eval('ConvertSelectionToContainedEdges')
		edges = mc.filterExpand(ex=True,sm=32)
	if not edges:
		print('Select a list of connected vertices or edges and run again...')
		return
	
	# Get Mesh from vertices
	mesh = mc.ls(edges,o=True)
	
	# Get UI Parameters
	smooth = mc.intSliderGrp('evenEdgeSpacing_smoothISG',q=True,v=True)
	influence = mc.floatSliderGrp('evenEdgeSpacing_influenceFSG',q=True,v=True)
	snapToOrig = mc.checkBoxGrp('evenEdgeSpacing_snapToOrigCBG',q=True,v1=True)
	delHistory = mc.checkBoxGrp('evenEdgeSpacing_deleteHistoryCBG',q=True,v1=True)
	
	# Even Edge Spacing
	evenEdgeSpacing(	edgeList		= edges,
						smooth			= smooth,
						influence		= influence,
						snapToOrig		= snapToOrig,
						deleteHistory	= delHistory )
	
	# Restore Selection
	if sel:
		mc.selectMode(component=True)
		mc.selectType(edge=True)
		mc.hilite(mesh)
		mc.select(edges)

def smoothEdgeLine(	edgeList,
					smooth			= 4,
					falloff			= 0.01,
					snapToOrig		= False,
					keepEdgeSpacing	= False,
					deleteHistory	= False ):
	'''
	'''
	# Get Edge List
	edgeList = mc.filterExpand(edgeList,ex=True,sm=32) or []
	if not edgeList:
		raise Exception('Invalid or empty edge list! Unable to even edge spacing...')
	
	edgeCrvList = glTools.tools.extractCurves.extractEdgeCurves(edgeList,keepHistory=False)
	smoothCrvList = []
	for edgeCrv in edgeCrvList:
	
		# Smooth Edge Line
		smoothCrv = mc.duplicate(edgeCrv,n=edgeCrv+'_smoothed')[0]
		smoothCurve(	crv			= smoothCrv,
						iterations	= smooth,
						keepEnds	= True,
						keepSpacing	= keepEdgeSpacing )
		
		# Snap To Mesh
		mesh = mc.ls(edgeList,o=True)[0]
		if snapToOrig:
			pts = glTools.utils.component.getComponentStrList(smoothCrv)
			glTools.utils.mesh.snapPtsToMesh(mesh,pts)
		
		# Append List
		smoothCrvList.append(smoothCrv)
	
	# Apply Smoothed Edge to Vertices
	wire = glTools.utils.wire.createMulti(mesh,edgeCrvList,dropoffDist=falloff,prefix=mesh.split(':')[-1])
	mc.setAttr(wire[0]+'.rotation',0)
	
	# Blend to Smooth Curve
	for i in range(len(edgeCrvList)):
		blendShape = glTools.utils.blendShape.create(baseGeo=edgeCrvList[i],targetGeo=[smoothCrvList[i]])
		mc.setAttr(blendShape+'.'+smoothCrvList[i],1)
	
	# ==================
	# - Delete History -
	# ==================
	
	if deleteHistory:
		wireBaseList = glTools.utils.wire.getWireBase(wire[0])
		mc.delete(mesh,ch=True)
		for edgeCrv in edgeCrvList:
			if mc.objExists(edgeCrv):
				mc.delete(edgeCrv)
		for smoothCrv in smoothCrvList:
			if mc.objExists(smoothCrv):
				mc.delete(smoothCrv)
		for wireBase in wireBaseList:
			if mc.objExists(wireBase):
				mc.delete(wireBase)
	
	# =================
	# - Return Result -
	# =================
	
	if edgeList:
		mc.hilite(mesh)
		mc.select(edgeList)
	
	return edgeList

def smoothEdgeLineUI():
	'''
	Smooth Edge Line UI
	'''
	# Window
	window = 'smoothEdgesUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Smooth Edge Line',s=True)
	
	# Layout
	CL = mc.columnLayout()
	
	# UI Elements
	mc.intSliderGrp('smoothEdges_smoothISG',label='Smooth',field=True,minValue=1,maxValue=20,fieldMinValue=1,fieldMaxValue=100,value=4)
	mc.floatSliderGrp('smoothEdges_falloffFSG',label='Falloff Distance',field=True,precision=3,minValue=0.0,maxValue=10.0,fieldMinValue=0.0,fieldMaxValue=100.0,value=0.01)
	mc.checkBoxGrp('smoothEdges_edgeSpacingCBG',label='Maintain Edge Spacing',numberOfCheckBoxes=1,v1=False)
	mc.checkBoxGrp('smoothEdges_snapToOrigCBG',label='Maintain Shape',numberOfCheckBoxes=1,v1=False) # columnWidth2=[100,165]
	mc.checkBoxGrp('smoothEdges_deleteHistoryCBG',label='Delete History',numberOfCheckBoxes=1,v1=False)
	mc.button('smoothEdgesB',l='Smooth',w=390,c='glTools.model.straightenVerts.smoothEdgeLineFromUI()')
	
	# Show Window
	mc.window(window,e=True,wh=[392,115])
	mc.showWindow(window)

def smoothEdgeLineFromUI():
	'''
	Smooth Edge Line From UI
	'''
	# Get Edge Selection
	sel = mc.ls(sl=True,fl=True)
	edges = mc.filterExpand(sel,ex=True,sm=32)
	verts = mc.filterExpand(sel,ex=True,sm=31)
	if not edges and verts:
		mc.select(verts)
		mm.eval('ConvertSelectionToContainedEdges')
		edges = mc.filterExpand(ex=True,sm=32)
	if not edges:
		print('Select a list of connected vertices or edges and run again...')
		return
	
	# Get Mesh from vertices
	mesh = mc.ls(edges,o=True)
	
	# Get UI Parameters
	smooth = mc.intSliderGrp('smoothEdges_smoothISG',q=True,v=True)
	falloff = mc.floatSliderGrp('smoothEdges_falloffFSG',q=True,v=True)
	edgeSpacing = mc.checkBoxGrp('smoothEdges_edgeSpacingCBG',q=True,v1=True)
	snapToOrig = mc.checkBoxGrp('smoothEdges_snapToOrigCBG',q=True,v1=True)
	delHistory = mc.checkBoxGrp('smoothEdges_deleteHistoryCBG',q=True,v1=True)
	
	# Smooth Edges
	smoothEdgeLine(	edges,
					smooth			= smooth,
					falloff			= falloff,
					snapToOrig		= snapToOrig,
					keepEdgeSpacing	= edgeSpacing,
					deleteHistory	= delHistory )
	
	# Restore Selection
	if sel:
		mc.selectMode(component=True)
		mc.selectType(edge=True)
		mc.hilite(mesh)
		mc.select(edges)

def smoothLine(pts,iterations=1,keepEnds=True,keepSpacing=False):
	'''
	Smooth Point Array
	@param pts: List of line point positions to smooth
	@type pts: list
	@param iterations: Number of smooth iterations to apply
	@type iterations: int
	@param keepEnds: Maintain end point positions
	@type keepEnds: bool
	@param keepSpacing: Maintain edge distance ratios
	@type keepSpacing: bool
	'''
	# Smooth Iterations
	end = int(keepEnds)
	for it in range(iterations):
		ref = copy.deepcopy(pts)
		for i in range(end,len(pts)-end):
			curr = glTools.utils.base.getMPoint(ref[i])
			next = glTools.utils.base.getMPoint(ref[i+1])
			prev = glTools.utils.base.getMPoint(ref[i-1])
			if keepSpacing:
				nextDist = (curr-next).length()
				prevDist = (curr-prev).length()
				nextWt = prevDist/(nextDist+prevDist) * 0.6
				prevWt = nextDist/(nextDist+prevDist) * 0.6
				pt = (curr * 0.4) + OpenMaya.MVector(next * nextWt) + OpenMaya.MVector(prev * prevWt)
			else:
				pt = (curr * 0.4) + OpenMaya.MVector((next+OpenMaya.MVector(prev)) * 0.3)
			pts[i] = [pt.x,pt.y,pt.z]
	
	# Return Result
	return pts

def smoothCurve(crv,iterations,keepEnds=True,keepSpacing=False):
	'''
	Smooth specified curve CVs.
	@param crv: Curve to smooth.
	@type crv: str
	@param iterations: Number of smooth iterations to apply
	@type iterations: int
	@param keepEnds: Maintain end point positions
	@type keepEnds: bool
	@param keepSpacing: Maintain edge distance ratios
	@type keepSpacing: bool
	'''
	# Get Smoothed Points
	pts = smoothLine(	pts	= glTools.utils.base.getPointArray(crv),
						iterations	= iterations,
						keepEnds	= keepEnds,
						keepSpacing	= keepSpacing )
	
	# Flatten Smooth Points List
	ptsFlat = []
	[ptsFlat.extend(i) for i in pts]
	
	# Apply Smoothed Points
	mc.setAttr(crv+'.cv[0:'+str(len(pts)-1)+']',*ptsFlat)
