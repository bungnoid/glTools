import maya.cmds as mc

class UserInputError( Exception ): pass

def addResolutionAttr(obj,resList=['low','medium','high'],resAttr='resolution',keyable=False):
	'''
	Adds the resolution enum attribute to the specified object
	@input obj: The object to add the resolution attribute to.
	@inputType obj: str
	@input resList: List of resolution options on the attribute. Default is ['low','medium','high'].
	@inputType resList: list
	@input resAttr: Name of the resolution attribute
	@inputType resAttr: str
	@input keyable: Specifies if resolution attribute is keyable. Default is False.
	@inputType keyable: bool
	'''
	# Error checks
	if not mc.objExists(obj):
		raise UserInputError('Object '+obj+' does not exist. Cannot add attribute!')
	if mc.objExists(obj+'.'+resAttr):
		raise UserInputError('Attribute "'+obj+'.'+resAttr+'" already exists. Cannot add the attribute again.')
	
	# Build enum string
	enumStr = ''
	for res in resList: enumStr += (res+':')
	# Add Attribute
	if not mc.objExists(obj+'.'+resAttr):
		mc.addAttr(obj,ln=resAttr,at='enum',en=enumStr,k=keyable)
	mc.setAttr(obj+'.'+resAttr,cb=1)
