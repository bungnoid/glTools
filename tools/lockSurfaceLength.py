import maya.cmds as mc

import glTools.utils.stringUtils
import glTools.utils.surface

def loadPlugin():
	'''
	Load glCurveUtils plugin.
	'''
	# Check if plugin is loaded
	if not mc.pluginInfo('glCurveUtils',q=True,l=True):
		
		# Load Plugin
		try: mc.loadPlugin('glCurveUtils')
		except: raise Exception('Unable to load glCurveUtils plugin!')
	
	# Return Result
	return 1

def create(surface,spansU=0,spansV=0,prefix=None):
	'''
	'''
	# Load Plugins
	loadPlugin()
	
	# ==========
	# - Checks -
	# ==========
	
	# Check Surface
	if not glTools.utils.surface.isSurface(surface):
		raise Exception('Object "'+surface+'" is not a valid nurbs surface!')
	
	# Check Prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(surface)
	
	# Get Surface Details
	if not spansU: spansU = mc.getAttr(surface+'.spansU')
	if not spansV: spansV = mc.getAttr(surface+'.spansV')
	minU = mc.getAttr(surface+'.minValueU')
	maxU = mc.getAttr(surface+'.maxValueU')
	minV = mc.getAttr(surface+'.minValueV')
	maxV = mc.getAttr(surface+'.maxValueV')
	incU = (maxU-minU)/spansU
	incV = (maxV-minV)/spansV
	
	# =============
	# - Rebuild U -
	# =============
	
	crvU = []
	for i in range(spansU+1):
		
		# Duplicate Surface Curve
		dupCurve = mc.duplicateCurve(surface+'.u['+str(incU*i)+']',ch=True,rn=False,local=False)
		dupCurveNode = mc.rename(dupCurve[1],prefix+'_spanU'+str(i)+'_duplicateCurve')
		dupCurve = mc.rename(dupCurve[0],prefix+'_spanU'+str(i)+'_crv')
		crvU.append(dupCurve)
		
		# Set Curve Length
		arcLen = mc.arclen(dupCurve)
		setLen = mc.createNode('setCurveLength',n=prefix+'_spanU'+str(i)+'_setCurveLength')
		crvInfo = mc.createNode('curveInfo',n=prefix+'_spanU'+str(i)+'_curveInfo')
		blendLen = mc.createNode('blendTwoAttr',n=prefix+'_spanU'+str(i)+'length_blendTwoAttr')
		mc.addAttr(dupCurve,ln='targetLength',dv=arcLen,k=True)
		mc.connectAttr(dupCurveNode+'.outputCurve',crvInfo+'.inputCurve',f=True)
		mc.connectAttr(dupCurveNode+'.outputCurve',setLen+'.inputCurve',f=True)
		mc.connectAttr(crvInfo+'.arcLength',blendLen+'.input[0]',f=True)
		mc.connectAttr(dupCurve+'.targetLength',blendLen+'.input[1]',f=True)
		mc.connectAttr(blendLen+'.output',setLen+'.length',f=True)
		mc.connectAttr(setLen+'.outputCurve',dupCurve+'.create',f=True)
		
		# Add Control Attributes
		mc.addAttr(dupCurve,ln='lockLength',min=0,max=1,dv=1,k=True)
		mc.addAttr(dupCurve,ln='lengthBias',min=0,max=1,dv=0,k=True)
		mc.connectAttr(dupCurve+'.lockLength',blendLen+'.attributesBlender',f=True)
		mc.connectAttr(dupCurve+'.lengthBias',setLen+'.bias',f=True)
	
	# Loft New Surface
	srfU = mc.loft(crvU,ch=True,uniform=True,close=False,autoReverse=False,degree=3)
	srfUloft = mc.rename(srfU[1],prefix+'_rebuildU_loft')
	srfU = mc.rename(srfU[0],prefix+'_rebuildU_srf')
	
	# Rebuild 0-1
	rebuildSrf = mc.rebuildSurface(srfU,ch=True,rpo=True,rt=0,end=1,kr=0,kcp=1,su=0,du=3,sv=0,dv=3,tol=0)
	rebuildSrfNode = mc.rename(rebuildSrf[1],prefix+'_rebuildU_rebuildSurface')
	
	# Add Control Attributes
	mc.addAttr(srfU,ln='lockLength',min=0,max=1,dv=1,k=True)
	mc.addAttr(srfU,ln='lengthBias',min=0,max=1,dv=0,k=True)
	for crv in crvU:
		mc.connectAttr(srfU+'.lockLength',crv+'.lockLength',f=True)
		mc.connectAttr(srfU+'.lengthBias',crv+'.lengthBias',f=True)
	
	# =============
	# - Rebuild V -
	# =============
	
	crvV = []
	for i in range(spansV+1):
		
		# Duplicate Surface Curve
		dupCurve = mc.duplicateCurve(srfU+'.v['+str(incV*i)+']',ch=True,rn=False,local=False)
		dupCurveNode = mc.rename(dupCurve[1],prefix+'_spanV'+str(i)+'_duplicateCurve')
		dupCurve = mc.rename(dupCurve[0],prefix+'_spanV'+str(i)+'_crv')
		crvV.append(dupCurve)
		
		# Set Curve Length
		arcLen = mc.arclen(dupCurve)
		setLen = mc.createNode('setCurveLength',n=prefix+'_spanV'+str(i)+'_setCurveLength')
		crvInfo = mc.createNode('curveInfo',n=prefix+'_spanV'+str(i)+'_curveInfo')
		blendLen = mc.createNode('blendTwoAttr',n=prefix+'_spanV'+str(i)+'length_blendTwoAttr')
		mc.addAttr(dupCurve,ln='targetLength',dv=arcLen,k=True)
		mc.connectAttr(dupCurveNode+'.outputCurve',crvInfo+'.inputCurve',f=True)
		mc.connectAttr(dupCurveNode+'.outputCurve',setLen+'.inputCurve',f=True)
		mc.connectAttr(crvInfo+'.arcLength',blendLen+'.input[0]',f=True)
		mc.connectAttr(dupCurve+'.targetLength',blendLen+'.input[1]',f=True)
		mc.connectAttr(blendLen+'.output',setLen+'.length',f=True)
		mc.connectAttr(setLen+'.outputCurve',dupCurve+'.create',f=True)
		
		# Add Control Attribute
		mc.addAttr(dupCurve,ln='lockLength',min=0,max=1,dv=1,k=True)
		mc.addAttr(dupCurve,ln='lengthBias',min=0,max=1,dv=0,k=True)
		mc.connectAttr(dupCurve+'.lockLength',blendLen+'.attributesBlender',f=True)
		mc.connectAttr(dupCurve+'.lengthBias',setLen+'.bias',f=True)
	
	# Loft New Surface
	srfV = mc.loft(crvV,ch=True,uniform=True,close=False,autoReverse=False,degree=3)
	srfVloft = mc.rename(srfV[1],prefix+'_rebuildV_loft')
	srfV = mc.rename(srfV[0],prefix+'_rebuildV_srf')
	
	# Rebuild 0-1
	rebuildSrf = mc.rebuildSurface(srfV,ch=True,rpo=True,rt=0,end=1,kr=0,kcp=1,su=0,du=3,sv=0,dv=3,tol=0)
	rebuildSrfNode = mc.rename(rebuildSrf[1],prefix+'_rebuildV_rebuildSurface')
	
	# Add Control Attribute
	mc.addAttr(srfV,ln='lockLength',min=0,max=1,dv=1,k=True)
	mc.addAttr(srfV,ln='lengthBias',min=0,max=1,dv=0,k=True)
	for crv in crvV:
		mc.connectAttr(srfV+'.lockLength',crv+'.lockLength',f=True)
		mc.connectAttr(srfV+'.lengthBias',crv+'.lengthBias',f=True)
	
	# ===================
	# - Build Hierarchy -
	# ===================
	
	rebuildUGrp = mc.group(em=True,n=prefix+'_rebuildU_grp')
	mc.parent(crvU,rebuildUGrp)
	mc.parent(srfU,rebuildUGrp)
	
	rebuildVGrp = mc.group(em=True,n=prefix+'_rebuildV_grp')
	mc.parent(crvV,rebuildVGrp)
	mc.parent(srfV,rebuildVGrp)
	
	rebuildGrp = mc.group(em=True,n=prefix+'_lockLength_grp')
	mc.parent(rebuildUGrp,rebuildGrp)
	mc.parent(rebuildVGrp,rebuildGrp)
	
	# =================
	# - Return Result -
	# =================
	
	return rebuildGrp
