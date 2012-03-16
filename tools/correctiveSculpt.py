import maya.mel as mm
import maya.cmds as mc

import glTools.utils.mesh
import glTools.utils.blendShape
import glTools.utils.dnpublish

def createSculptBase(rigMesh,baseMesh,prefix='sculpt'):
	'''
	'''
	# Checks
	if not glTools.utils.mesh.isMesh(rigMesh):
		raise Exception('Invalid mesh! ("'+rigMesh+'")')
	if not glTools.utils.mesh.isMesh(baseMesh):
		raise Exception('Invalid mesh! ("'+baseMesh+'")')
	
	# Get mesh info
	buffer = 1.1
	meshWidth = buffer * (mc.getAttr(rigMesh+'.boundingBoxMaxX') - mc.getAttr(rigMesh+'.boundingBoxMinX'))
	meshHeight = buffer * (mc.getAttr(rigMesh+'.boundingBoxMaxY') - mc.getAttr(rigMesh+'.boundingBoxMinY'))
	
	# ------------------
	# - Dulpicate mesh -
	# ------------------
	
	# Generate rigBase mesh
	rigBase = mc.duplicate(rigMesh)[0]
	rigBase = mc.rename(rigBase,prefix+'_rigBase')
	mc.parent(rigBase,w=True)
	mc.move(meshWidth,0,0,rigBase,ws=True,a=True)
	# Set display type - Reference
	mc.setAttr(rigBase+'.overrideEnabled',1)
	mc.setAttr(rigBase+'.overrideDisplayType',2)
	
	# Generate sculpt mesh
	sculpt = mc.duplicate(rigMesh)[0]
	sculpt = mc.rename(sculpt,prefix+'_sculpt')
	mc.parent(sculpt,w=True)
	mc.move(meshWidth*2,0,0,sculpt,ws=True,a=True)
	
	# Generate delta mesh
	delta = mc.duplicate(baseMesh)[0]
	delta = mc.rename(delta,prefix+'_delta')
	mc.parent(delta,w=True)
	mc.move(meshWidth*1.5,meshHeight,0,delta,ws=True,a=True)
	# Set display type - Reference
	mc.setAttr(delta+'.overrideEnabled',1)
	mc.setAttr(delta+'.overrideDisplayType',2)
	
	# Generate result mesh
	result = mc.duplicate(baseMesh)[0]
	result = mc.rename(result,prefix+'_result')
	mc.parent(result,w=True)
	mc.move(meshWidth*3,0,0,result,ws=True,a=True)
	# Set display type - Reference
	mc.setAttr(result+'.overrideEnabled',1)
	mc.setAttr(result+'.overrideDisplayType',2)
	
	# --------------------------
	# - Add BlendShape Targets -
	# --------------------------
	
	# Create delta blendShape
	deltaBlendShape = mc.blendShape(sculpt,rigBase,delta,n=delta+'_blendShape')[0]
	deltaTarget = mc.listAttr(deltaBlendShape+'.w',m=True)
	mc.setAttr(deltaBlendShape+'.'+deltaTarget[0],1.0)
	mc.setAttr(deltaBlendShape+'.'+deltaTarget[1],-1.0)
	
	# Add rig and delta mesh as targets to result mesh
	resultBlendShape = mc.blendShape(rigMesh,delta,result,n=result+'_blendShape')[0]
	resultTarget = mc.listAttr(resultBlendShape+'.w',m=True)
	mc.setAttr(resultBlendShape+'.'+resultTarget[0],1.0)
	mc.setAttr(resultBlendShape+'.'+resultTarget[1],1.0)
	
	# -----------------
	# - Return Result -
	# -----------------
	
	return [rigBase,sculpt,delta,result]

def updateSculptBase(rigMesh,baseMesh,prefix='sculpt'):
	'''
	'''
	# ----------
	# - Checks -
	# ----------
	
	# RigMesh
	if not glTools.utils.mesh.isMesh(rigMesh):
		raise Exception('Invalid mesh! ("'+rigMesh+'")')
	
	# BaseMesh
	if not glTools.utils.mesh.isMesh(baseMesh):
		raise Exception('Invalid mesh! ("'+baseMesh+'")')
	
	# RigBase / Sculpt / Delta
	rigBase = prefix+'_rigBase'
	sculpt = prefix+'_sculpt'
	delta = prefix+'_delta'
	if not glTools.utils.mesh.isMesh(rigBase):
		raise Exception('Invalid mesh! ("'+rigBase+'")')
	if not glTools.utils.mesh.isMesh(sculpt):
		raise Exception('Invalid mesh! ("'+sculpt+'")')
	if not glTools.utils.mesh.isMesh(delta):
		raise Exception('Invalid mesh! ("'+delta+'")')
	
	# ------------------------
	# - Update Sculpt Shapes -
	# ------------------------
	
	# Freeze Delta Mesh
	mc.delete(delta,ch=True)
	
	# Update rigBase
	rigBaseBlendShape = mc.blendShape(rigMesh,rigBase)[0]
	rigBaseTarget = mc.listAttr(rigBaseBlendShape+'.w',m=True)
	mc.setAttr(rigBaseBlendShape+'.'+rigBaseTarget[0],1.0)
	mc.delete(rigBase,ch=True)
	
	# Update sculpt
	sculptBlendShape = mc.blendShape(baseMesh,sculpt)[0]
	sculptTarget = mc.listAttr(sculptBlendShape+'.w',m=True)
	mc.setAttr(sculptBlendShape+'.'+sculptTarget[0],1.0)
	mc.delete(sculpt,ch=True)
	sculptBlendShape = mc.blendShape(rigBase,delta,sculpt)[0]
	sculptTarget = mc.listAttr(sculptBlendShape+'.w',m=True)
	mc.setAttr(sculptBlendShape+'.'+sculptTarget[0],1.0)
	mc.setAttr(sculptBlendShape+'.'+sculptTarget[1],1.0)
	mc.delete(sculpt,ch=True)
	
	# Update delta mesh
	deltaBlendShape = mc.blendShape(baseMesh,delta)[0]
	deltaTarget = mc.listAttr(deltaBlendShape+'.w',m=True)
	mc.setAttr(deltaBlendShape+'.'+deltaTarget[0],1.0)
	mc.delete(delta,ch=True)
	deltaBlendShape = mc.blendShape(sculpt,rigBase,delta)[0]
	deltaTarget = mc.listAttr(deltaBlendShape+'.w',m=True)
	mc.setAttr(deltaBlendShape+'.'+deltaTarget[0],1.0)
	mc.setAttr(deltaBlendShape+'.'+deltaTarget[1],-1.0)
	
	# -----------------
	# - Return Result -
	# -----------------
	
	return [rigBase,sculpt,delta]
