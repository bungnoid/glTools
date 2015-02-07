import maya.cmds as mc

def timeWarp(animCurves,prefix):
	'''
	'''
	# Check anim curves
	if not animCurves: return
	
	# Get anim playback start and end
	st = mc.playbackOptions(q=True,min=True)
	en = mc.playbackOptions(q=True,max=True)
	
	# Create time warp curve
	timeWarpCrv = mc.createNode('animCurveTT',n=prefix+'_timeWarp')
	mc.setKeyframe(timeWarpCrv,t=st,v=st)
	mc.setKeyframe(timeWarpCrv,t=en,v=en)
	
	# Attach timeWarp
	for animCurve in animCurves:
	
		# Check curve type
		crvType = mc.objectType(animCurve)
		if crvType == 'animCurveTL' or crvType == 'animCurveTA' or crvType == 'animCurveTU':
			mc.connectAttr(timeWarpCrv+'.output',animCurve+'.input',f=True)
