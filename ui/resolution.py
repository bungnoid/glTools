import maya.cmds as mc
import glTools.utils.resolution

def addResAttr(isProp=True):
	'''
	Wrapper for addResolutionAttr.
	@input isProp: Set the resolution enum attribute array based on this value (prop/character).
	@inputType isProp: bool
	'''
	obj = 'supermover'
	if isProp:
		glTools.utils.resolution.addResolutionAttr(obj=obj,resList=['medium','high'])
	else:
		glTools.utils.resolution.addResolutionAttr(obj=obj)
