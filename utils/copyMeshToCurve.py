import maya.cmds as mc

def create(baseCrv,curveList,inMeshList,prefix):
	'''
	Create standard copyMeshToCurve setup based on the input arguments
	@param baseCrv: Base curve
	@type baseCrv: str
	@param curveList: List of curves to copy mesh to
	@type curveList: list
	@param inMeshList: List of meshes to copy to curves
	@type inMeshList: list
	@param prefix: Naming prefix
	@type prefix: str
	'''
	# Create copyMeshToCurve node
	copyMeshToCurve = mc.createNode('copyMeshToCurve',n=prefix+'_copyMeshToCurve')
	
	# Connect base curve
	mc.connectAttr(baseCrv+'.worldSpace[0]',copyMeshToCurve+'.baseCurve',f=True)
	
	# Connect input curves
	connectInputCurves(copyMeshToCurve,curveList)
	
	# Connect input mesh
	connectInputMesh(copyMeshToCurve,inMeshList)
	
	# Create output mesh
	outMeshShape = mc.createNode('mesh',n=prefix+'_outMeshShape')
	outMesh = mc.listRelatives(outMeshShape,p=True)[0]
	mc.rename(outMesh,prefix+'_outMesh')
	
	# Connect out mesh
	mc.connectAttr(copyMeshToCurve+'.outputMesh',outMeshShape+'.inMesh',f=True)
	
	# Return Reult
	return copyMeshToCurve

def connectInputCurves(copyMeshToCurve,curveList):
	'''
	Connect a list of input curves to the specified copyMeshToCurve node.
	@param copyMeshToCurve: copyMeshToCurve node to connect curves to
	@type copyMeshToCurve: str
	@param curveList: List of input curves to copy mesh to
	@type curveList: str
	'''
	# Connect Input Curves
	for i in range(len(curveList)):
		mc.connectAttr(curveList[i]+'.worldSpace[0]',copyMeshToCurve+'.inputCurve['+str(i)+']',f=True)
		
def connectInputMesh(copyMeshToCurve,inMeshList):
	'''
	Connect a list of input meshes to the specified copyMeshToCurve node.
	@param copyMeshToCurve: copyMeshToCurve node to connect curves to
	@type copyMeshToCurve: str
	@param inMeshList: List of input meshes to copy onto curves
	@type curveList: str
	'''
	# Connect Input Meshes
	for i in range(len(inMeshList)):
		mc.connectAttr(inMeshList[i]+'.outMesh',copyMeshToCurve+'.inputMesh['+str(i)+']',f=True)
