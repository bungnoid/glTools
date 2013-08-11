#############################################################################################################################

import maya.cmds as mc
import maya.mel as mm
import glTools.utils.channelState

# Create exception class
class UserInputError(Exception): pass

class VisibilityUtilities(object):
	def __init__(self):
		pass
	
	def connect(self,controlAttr,objectList,overrideExistingConnections=False):
		'''
		Connect the visibility of a list of controls to a specified control attribute
		@param controlAttr: Attribute that will control the visibility of a list of objects
		@type controlAttr: str
		@param objectList: List of objects whose visibility will be connected to the control attribute
		@type objectList: list
		'''
		# Check Object List
		if not objectList:
			raise UserInputError('No valid list of objects providedfor visibility connection!!')
		for obj in objectList:
			if not mc.objExists(obj):
				raise UserInputError('Object "'+obj+'" does not exist!!')
		
		# Check Control Attribute
		if not mc.objExists(controlAttr):
			if not controlAttr.count('.'):
				raise UserInputError('Control attribute is not in the expected format "object.attribute"!!')
			objAttr = controlAttr.split('.')
			if len(objAttr) != 2:
				raise UserInputError('Control attribute is not in the expected format "object.attribute"!!')
			if not mc.objExists(objAttr[0]):
				raise UserInputError('Control object "'+objAttr[0]+'" does not exist!!')
			mc.addAttr(objAttr[0],ln=objAttr[1],at='enum',en='off:on:',k=True,dv=1)
		
		# Connect Visibility
		for obj in objectList:
			if not overrideExistingConnections and mc.listConnections(obj+'.v',s=True,d=False): continue
			mc.connectAttr(controlAttr,obj+'.v',f=True)
		
		# Set Channel State
		glTools.utils.channelState.ChannelState().setFlags([-1,-1,-1,-1,-1,-1,-1,-1,-1,1][objectList])
		glTools.utils.channelState.ChannelState().set(1,[objectList])
	
	def connectControls(self,char='',connectAttr='supermover.controls',connectHiddenJoints=False):
		'''
		Function to connect the visibility of all animateable controls and joints of a character to
		the supermover.controls attribute
		@param char: namespace of character
		@type char: str
		@param connectHiddenJoints: Connect unconnected, hidden joints
		@type connectHiddenJoints: bool
		'''
		
		# Check control attribute
		if not mc.objExists(connectAttr):
			raise UserInputError('Attribute "'+connectAttr+'" does not exist! Run BaseRig.addControlToggleAttr() and try again.')
		
		# Allow function to work with or without namespace
		if char.count(':'): raise UserInputError('No support for nested namespaces!')
		# Append colon
		if char: char += ':'
		
		# Get a list of all the controls in the scene
		hideNodes = mc.ls(char + '*',type='nurbsCurve')
		hideNodes.extend(mc.ls(char + '*',type='joint'))
		
		# Loop thru all the controls and joints in the scene and connect them to the supermover.control attr
		failedItems=[]
		for node in hideNodes:
			try:
				# Check lock state of vis channel
				if mc.setAttr(node+'.visibility',q=True,l=True):
					glTools.utils.channelState.ChannelState().setFlags([-1,-1,-1,-1,-1,-1,-1,-1,-1,1][node])
					glTools.utils.channelState.ChannelState().set(1,[node])
				# Check for incoming connections
				visObjConnections = mc.listConnections(node+'.visibility', s=True, d=False)
				visAttrConnections = mc.listConnections(node+'.visibility', s=True, d=False, p=True)
				# Check for existing connections
				if visObjConnections:
					if (mc.objectType(visObjConnections[0]) != 'multDoubleLinear') and visAttrConnections[0] != connectAttr:
						# Add multDoubleLinear vis connections
						vis_mdl = mc.createNode('multDoubleLinear', name= node + '_vis01_dbl')
						mc.connectAttr(connectAttr, vis_mdl+'.input1',f=True)
						mc.connectAttr(visAttrConnections[0], vis_mdl+'.input2',f=True)
						mc.connectAttr(vis_mdl+'.output', node + '.visibility',f=True)
				else:
					if not connectHiddenJoints and not mc.getAttr(node+'.visibility'): continue
					mc.connectAttr(connectAttr,node+'.visibility',f=True)
			except:
				failedItems.append(node)
