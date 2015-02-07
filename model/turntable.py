import maya.cmds as mc

import ika.maya.turntable

def costumeVariantTurntable(duration=8,startAngle=0,rotate=360,direction='cw',monitor=True):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	costume = 'costume'
	if not mc.objExists('costume'):
		raise Exception('Costume model group "'+costume+'" not found!')
	
	# ==================
	# - Get Variations -
	# ==================
	
	costumeDict = {}
	costumeList = mc.listRelatives(costume,c=True,type='transform')
	for costumeElem in costumeList:
		
		# Determine Variant
		var = costumeElem.split('_')[-1]
		
		# Check Variant String
		if len(var) != 4:
			print('Invalid variant costume suffix! ("'+var+'")')
			continue
		
		# Create Dictionary Entry
		if not costumeDict.has_key(var):
			costumeDict[var] = [costumeElem]
		else:
			costumeDict[var].append(costumeElem)
		
		# Hide
		mc.setAttr(costumeElem+'.v',0)
	
	# =========================
	# - Run Turntable Renders -
	# =========================
	
	costumeKeys = costumeDict.keys()
	for costumeKey in costumeKeys:
		
		# Unhide
		for item in costumeDict[costumeKey]: mc.setAttr(item+'.v',1)
		
		# Print Message
		print('Submitting truntable render - "'+costumeKey+'"')
		
		# Run Turntable
		ika.maya.turntable.turntable(	rotEnd = duration,
										rotStartAngle = startAngle,
										rotAmount = rotate,
										rotDirection = direction,
										animSource = None,
										animStart = 1,
										animEnd = None,
										subtaskSuffix = costumeKey,
										monitor = monitor,
										nightRender = False,
										cpus = 5	)
		
		# Hide
		for item in costumeDict[costumeKey]: mc.setAttr(item+'.v',0)
	
	# ===============================
	# - Unhide All Costume Elements -
	# ===============================
	
	for costumeElem in costumeList: mc.setAttr(costumeElem+'.v',1)
	
	# =================
	# - Return Result -
	# =================
	
	return costumeKeys
