#################################################################################################################

import maya.cmds as mc
class UserInputError(Exception): pass

#################################################################################################################

def visConnect():
	'''
	connects the visibilty attr of two or more objects
	'''
   sel = mc.ls(sl = True)
   
   if sel < 2:
	   raise UserInputError('You must select at least two objects in order to connect visibilities')
	
   ccc = sel[0]
   obj[] = stringArrayRemove({ccc}, sel);
   
   rig_visConnect(ccc, obj);

#################################################################################################################

def rig_visConnect(control, geo[]):
	
	'''
	used to create a vis channel on an object (first selected object)
	and attach it to the visibility of all other selected objects
	'''
	
	if not mc.objExists(control):
	   raise UserInputError('The control specified to rig_visConnect does not exist!')
	   
   if not mc.attributeExists('vis', control):
	   mc.addAttr(control, k=True, ln='vis', at='enum', en='off:on:')
	   mc.setAttr(control + '.vis') 1
	
	for i in len(geo):
		if not mc.objExists(geo[i]):
			continue
		temp = mc.listConnections(s=True, d=False, geo[i] + '.v')
		if not temp:
			raise UserInputError('Warning, the object ' + geo[i] + ' already has an incoming connection on its visibility and will be skipped.')
			continue
		mc.setAttr(geo[i] + '.v', l=False)
		mc.connectAttr((geo[i] + '.v'), (control + '.vis'), f=True)
		channelStateSetFlags(-1,-1,-1,-1,-1,-1,-1,-1,-1,2, {geo[i]})
