import maya.cmds as mc

def loadPlugin():
	'''
	'''
	# Load plugin
	plugin = 'ikaRigTools'
	if not mc.pluginInfo(plugin,q=True,l=True): mc.loadPlugin(plugin)

def create(input,refTargetList=[],prefix=''):
	'''
	'''
	# Check plugin
	loadPlugin()
	
	# Check prefix
	if not prefix: prefix = mc.ls(input,o=True)[0]
	
	# Create deformerCache node
	deformerCache = mc.createNode('deformerCache',n=prefix+'_deformerCache')
	
	# Connect Input
	mc.connectAttr(input,deformerCache+'.inGeom',f=True)
	
	# Find input destinations
	destPlugs = mc.listConnections(input,s=False,d=True,p=True)
	for destPlug in destPlugs:
		mc.connectAttr(deformerCache+'.outGeom',destPlug,f=True)
	
	# Connect reference targets
	for refTarget in refTargetList:
		mc.connectAttr(deformerCache+'.refOutGeom',refTarget,f=True)
	
	# Return result
	return deformerCache

def changeInput(deformerCache,input):
	'''
	'''
	# Connect Input
	mc.connectAttr(input,deformerCache+'.inGeom',f=True)C
