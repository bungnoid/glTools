import maya.cmds as mc

def copyChannels(src,dst,transform=True,joint=True,userDefined=True):
	'''
	'''
	# Check source and destination objects
	if not mc.objExists(src):
		raise Exception('Source object "'+src+'" does not exist!!')
	if not mc.objExists(dst):
		raise Exception('Destination object "'+dst+'" does not exist!!')
		
	# -----------------------
	# - Copy channel values -
	# -----------------------
	
	# Transform
	if transform:
		
		tAttrs = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
		for attr in tAttrs:
			
			# Get source attribute value
			attrVal = mc.getAttr(src+'.'+attr)
			
			# Set destination attribute value
			if not mc.objExists(dst+'.'+attr):
				raise Exception('Destination attribute "'+dst+'.'+attr+'" does not exist!!')
			mc.setAttr(dst+'.'+attr,l=False)
			mc.setAttr(dst+'.'+attr,attrVal)
	
	# Joint
	if joint:
		
		jAttrs = ['radius','stx','sty','stz','pax','pay','paz','jox','joy','joz']
		for attr in jAttrs:
			
			# Check source attribute
			if not mc.objExists(src+'.'+attr): continue
			
			# Get source attribute value	
			attrVal = mc.getAttr(src+'.'+attr)
			
			# Set destination attribute value
			if not mc.objExists(dst+'.'+attr):
				raise Exception('Destination attribute "'+dst+'.'+attr+'" does not exist!!')
			mc.setAttr(dst+'.'+attr,l=False)
			mc.setAttr(dst+'.'+attr,attrVal)
	
	# User Defined
	if userDefined:
		
		uAttrs = mc.listAttr(src,ud=True)
		for attr in tAttrs:
			
			# Get source attribute value
			attrVal = mc.getAttr(src+'.'+attr)
			
			# Check destination attribute
			if not mc.objExists(dst+'.'+attr):
				print('Destination attribute "'+dst+'.'+attr+'" does not exist!! Skipping attribute...')
				continue
			
			# Set destination attribute value
			mc.setAttr(dst+'.'+attr,l=False)
			mc.setAttr(dst+'.'+attr,attrVal)

