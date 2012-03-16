import maya.cmds as mc

class UserInputError(Exception): pass

def colorize(obj,color):
	'''
	Set override color for a specified object
	@param obj: The dag node to set the color for
	@type obj: str
	@param color: The dag node to set the color for
	@type color: str or int
	'''
	# Check object
	if not mc.objExists(obj): raise UserInputError('Object "'+obj+'" does not exist!!')
	# Create color lookup dictionary
	colorDict = {'grey':2,'maroon':4,'dark blue':5,'blue':6,'purple':9,'brown':10,'red':13,'green':13,'white':16,'yellow':17,'light blue':18}
	# Enable Overrides
	mc.setAttr(obj+'.overrideEnabled',1)
	# Set Color
	if type(color) == str:
		if colorDict.has_key(color): mc.setAttr(obj+'.overrideColor',colorDict[color])
		else: raise UserInputError('Color "'+color+'" is not recognised!!')
	elif type(color) == int:
		mc.setAttr(obj+'.overrideColor',color)
	else:
		raise UserInputError('No valid color value supplied!!')
