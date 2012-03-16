import maya.cmds as mc
import maya.mel as mm
import glTools.common.namingConvention

#import ika.apps.maya.maya_stage

class UserInputError(Exception): pass

class PropAci( object ):
	
	def __init__(self):
		self.nameUtil=glTools.common.namingConvention.NamingConvention()
		#self.stage = ika.apps.maya.maya_stage.MayaStage()
		
	def addControls(self,controls=[]):
		'''
		Creates ACI buttons based on the users selection
		'''
		# Gather all ccc nodes in the scene and create aci widgets for them
		if not controls:
			raise UserInputError('Please select the controls you want to create buttons for.')
		
		#self.stage.editAciFile('/home/r/rgomez/Desktop/ACI/prop.aci',actorName='')
		
		mc.select(cl=True)
		startX = .1
		startY = .1
		addX = .125
		addY = .125
		for control in controls:
			mm.eval('aci "cd /book/main"')
			buttons = mm.eval('aci "ls"')
			buttonsList = buttons.split('\n')
			if not buttonsList.count(control):
				mc.select(control)
				mm.eval('aci "cd /book/main"')
				mm.eval('aci "new widget class=selection_button"')
				mm.eval('aci "setattr name"' + control)
				mm.eval('aci "setattr size-height .1"')
				mm.eval('aci "setattr size-width .1"')
				mm.eval('aci "setattr color-pressed \#ffffff"')
				mm.eval('aci "setattr color-toggled \#ffffff"')
				mm.eval('aci "setattr pos-x ' + str(startX) + '"')
				mm.eval('aci "setattr pos-y ' + str(startY) + '"')
				startX += addX
				#startY += addY
				channelState = glTools.utils.channelState.ChannelState().get(control)
				if not channelState: channelState = [0,0,0,0,0,0,0,0,0,0]
				if not channelState[0] or not channelState[1] or not channelState[2]:
					mm.eval('aci "setattr manipulatorstate translate"')
				elif not channelState[3] or not channelState[4] or not channelState[5]:
					mm.eval('aci "setattr manipulatorstate rotate"')
				elif not channelState[6] or not channelState[7] or not channelState[8]:
					mm.eval('aci "setattr manipulatorstate scale"')
	
