import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.mesh
import glTools.utils.deformer
import glTools.tools.symmetryTable

class UserInputError(Exception): pass

def mirrorWeights(mesh,deformer,axis='x',posToNeg=True,refMesh=''):
	'''
	Mirror deformer weights
	@param mesh: Mesh to mirror weights on
	@type mesh: str
	@param deformer: Deformer to mirror weights for
	@type deformer: str
	@param axis: Axis to mirror weights across
	@type axis: str
	@param posToNeg: Apply weight mirror from positive to negative vertices
	@type posToNeg: bool
	@param refMesh: Mesh used for symmetry reference
	@type refMesh: str
	'''
	# Check deformers
	if not mc.objExists(deformer):
		raise UserInputError('Deformer "'+deformer+'" does not exist!!')
	
	# Check refMesh
	if not refMesh: refMesh = mesh
	
	# Get symmetry table
	axisIndex = {'x':0,'y':1,'z':2}[axis]
	sTable = glTools.tools.symmetryTable.SymmetryTable()
	symTable = sTable.buildSymTable(refMesh,axisIndex)
	
	# Get current weights
	wt = glTools.utils.deformer.getWeights(deformer)
	mem = glTools.utils.deformer.getDeformerSetMemberIndices(deformer,mesh)
	
	# Mirror weights
	for i in [sTable.negativeIndexList,sTable.positiveIndexList][int(posToNeg)]:
		if mem.count(i) and mem.count(symTable[i]):
			wt[mem.index(symTable[i])] = wt[mem.index(i)]
	
	# Apply mirrored weights
	glTools.utils.deformer.setWeights(deformer,wt,mesh)
	
def flipWeights(mesh,sourceDeformer,targetDeformer='',axis='x',refMesh=''):
	'''
	Flip deformer weights
	@param mesh: Mesh to flip weights for
	@type mesh: str
	@param sourceDeformer: Deformer to query weights from
	@type sourceDeformer: str
	@param targetDeformer: Deformer to apply weights to
	@type targetDeformer: str
	@param axis: Axis to flip weights across
	@type axis: str
	@param refMesh: Mesh used for symmetry reference
	@type refMesh: str
	'''
	# Check deformers
	if not mc.objExists(sourceDeformer):
		raise UserInputError('Source deformer '+sourceDeformer+' does not exist!!')
	if targetDeformer and not mc.objExists(targetDeformer):
		raise UserInputError('Traget deformer '+targetDeformer+' does not exist!!')
	if not targetDeformer:
		targetDeformer = sourceDeformer
	
	# Check refMesh
	if not refMesh: refMesh = mesh
	
	# Get mesh shape
	meshShape = mesh
	if mc.objectType(meshShape) == 'transform':
		meshShape = mc.listRelatives(mesh,s=True,ni=True)[0]
	
	# Get symmetry table
	axisIndex = {'x':0,'y':1,'z':2}[axis]
	symTable = glTools.common.symmetryTable.SymmetryTable().buildSymTable(refMesh,axisIndex)
	
	# Get current weights
	wt = glTools.utils.deformer.getWeights(sourceDeformer,mesh)
	sourceMem = glTools.utils.deformer.getDeformerSetMemberIndices(sourceDeformer,meshShape)
	targetMem = glTools.utils.deformer.getDeformerSetMemberIndices(targetDeformer,meshShape)
	targetWt = [0.0 for i in range(len(targetMem))]
	
	# Mirror weights
	for i in sourceMem:
		if targetMem.count(symTable[i]):
			try: targetWt[targetMem.index(symTable[i])] = wt[sourceMem.index(i)]
			except:
				print('Error @: '+str(symTable[i]))
				pass
		else:
			print('Cant find sym index for '+str(i))
	
	# Apply mirrored weights
	glTools.utils.deformer.setWeights(targetDeformer,targetWt,mesh)

def copyWeights(sourceMesh,targetMesh,sourceDeformer,targetDeformer):
	'''
	Copy deformer weights from one mesh to another.
	Source and Target mesh objects must have matching point order!
	@param sourceMesh: Mesh to copy weights from
	@type sourceMesh: str
	@param targetMesh: Mesh to copy weights to
	@type targetMesh: str
	@param sourceDeformer: Deformer to query weights from
	@type sourceDeformer: str
	@param targetDeformer: Deformer to apply weights to
	@type targetDeformer: str
	'''
	# Check source and target mesh
	if not mc.objExists(sourceMesh):
		raise UserInputError('Source mesh "'+sourceMesh+'" does not exist!!')
	if not mc.objExists(targetMesh):
		raise UserInputError('Target mesh "'+targetMesh+'" does not exist!!')
	
	# Check deformers
	if not mc.objExists(sourceDeformer):
		raise UserInputError('Source deformer "'+sourceDeformer+'" does not exist!!')
	if targetDeformer and not mc.objExists(targetDeformer):
		raise UserInputError('Target deformer "'+targetDeformer+'" does not exist!!')
	if not targetDeformer: targetDeformer = sourceDeformer
	
	# Compare vertex count
	if mc.polyEvaluate(sourceMesh,v=True) != mc.polyEvaluate(targetMesh,v=True):
		raise UserInputError('Source and Target mesh vertex counts do not match!!')
	
	# Copy weights
	wtList = glTools.utils.deformer.getWeights(sourceDeformer,sourceMesh)
	# Paste weights
	glTools.utils.deformer.setWeights(targetDeformer,wtList,targetMesh)
