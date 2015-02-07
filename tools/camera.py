import maya.cmds as mc

import ika.maya.file

def shotCam(side='L'):
	'''
	Return the shot camera based on a name pettern derived from the current context.
	If a camera matching the name pattern is not found, an empty string is returned.
	'''
	# Get Context
	ctx = ika.maya.file.getContext()
	
	# Check Context
	ctxType = type(ctx).__name__
	if not ctxType == 'ShotWorkfile':
		raise Exception('Unable to determine shot camera from '+ctxType+'!')
	
	# Get Seq/Shot Details
	seq = dict(ctx)['sequence']
	shot = dict(ctx)['shot']
	
	# Get Camera
	camStr = '*'+seq+'_'+shot+'_camera_'+side
	camSel = mc.ls(camStr,r=True)
	if not camSel:
		print('Unable to locate shot camera for "'+seq+'.'+shot+'"! ('+camStr+')')
		return ''
	if len(camSel) > 1:
		print('Multiple shot cameras found! Using first in list ('+str(camSel)+')')
	
	# Return Result
	return camSel[0]
