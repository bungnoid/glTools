import maya.cmds as mc

#import glTools.utils.blendShape

def duplicateAndBlend(obj,parent='',search='',replace='',worldSpace=False):
	'''
	Duplicate a specified deformable object, then blendShape the duplicate to the original.
	@param obj: Object to duplicate
	@type obj: str
	@param parent: Parent transform to place the duplicate object under
	@type parent: str
	@param search: Names search string used to generate the duplicate object name 
	@type search: str
	@param replace: Names replace string used to generate the duplicate object name 
	@type replace: str
	@param worldSpace: Create the blendShape in relation to local or world space 
	@type worldSpace: bool
	'''
	# Check object exists
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	
	# Duplicate object
	dup = mc.duplicate(obj,rr=True,n=obj.replace(search,replace))[0]
	
	# Create blendShape from original to duplicate
	origin = 'local'
	if worldSpace: origin = 'world'
	blendShape = mc.blendShape(obj,dup,o=origin)[0]
	
	# Set blendShape weight
	blendAlias = mc.listAttr(blendShape+'.w',m=True)[0]
	mc.setAttr(blendShape+'.'+blendAlias,1.0)
	
	# Parent
	if parent and mc.objExists(parent):
		mc.parent(dup,parent)
	else:
		mc.parent(dup,w=True)
	
	# Return result
	return blendShape
