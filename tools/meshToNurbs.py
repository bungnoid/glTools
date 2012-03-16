import maya.cmds as mc
import maya.mel as mm

import glTools.utils.mesh
import glTools.utils.stringUtils

def meshToNurbs(mesh,rebuild=False,spansU=0,spansV=0,prefix=''):
	'''
	'''
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(mesh)
	
	# Convert poly to subdiv
	subd = mc.polyToSubdiv(mesh,ch=False,preserveVertexOrdering=True)[0]
	
	# Full crease corner vertices
	cornerIds = glTools.utils.mesh.getCornerVertexIds(mesh)
	mc.select([subd+'.vtx['+str(i)+']' for i in cornerIds])
	mm.eval('FullCreaseSubdivSurface')
	
	# Convert subdiv to nurbs
	nurbsConvert = mc.subdToNurbs(subd,ch=False)[0]
	nurbs = mc.listRelatives(nurbs,c=True)
	
	# Cleanup
	mc.parent(nurbs,w=True)
	mc.delete(nurbsConvert)
	mc.delete(subd)
	
	# Return result
	return nurbs
