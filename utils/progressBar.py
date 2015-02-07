import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

class UserInterupted(Exception): pass

def init(status,maxValue):
	'''
	Initialize Progress Bar
	'''
	# Check Interactive Session
	if OpenMaya.MGlobal.mayaState(): return

	# Initialize Progress Bar
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	mc.progressBar( gMainProgressBar,e=True,bp=True,ii=True,status=status,maxValue=maxValue )

def update(step=0,status='',enableUserInterupt=False):
	'''
	Update Progress
	'''
	# Check Interactive Session
	if OpenMaya.MGlobal.mayaState(): return

	# Update Progress Bar
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')

	# Check User Interuption
	if enableUserInterupt:
		if mc.progressBar(gMainProgressBar,q=True,isCancelled=True):
			mc.progressBar(gMainProgressBar,e=True,endProgress=True)
			raise UserInterupted('Operation cancelled by user!')

	# Update Status
	if status: mc.progressBar( gMainProgressBar,e=True,status=status)

	# Step Progress
	if step: mc.progressBar(gMainProgressBar,e=True,step=step)

def end():
	'''
	End Progress
	'''
	# Check Interactive Session
	if OpenMaya.MGlobal.mayaState(): return

	# Update Progress Bar
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')

	# End Progress
	mc.progressBar(gMainProgressBar,e=True,endProgress=True)