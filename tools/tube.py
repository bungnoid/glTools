import maya.cmds as mc

import glTools.tools.controlBuilder

import glTools.utils.attach
import glTools.utils.base
import glTools.utils.attribute
import glTools.utils.component
import glTools.utils.stringUtils

def buildProfile(radius=1,spans=8):
	'''
	Create tube profile curve (circle)
	@param radius: Profile radius
	@type radius: float
	@param spans: Number of profile curve spans
	@type spans: int
	'''
	crv = mc.circle(c=[0,0,0],nr=[0,0,1],sw=360,r=radius,s=spans,d=3,ch=False)
	return crv

def buildOffsetCurve(crv):
	'''
	'''
	prefix = glTools.utils.stringUtils.stripSuffix(crv)
	offsetCrvShape = mc.createNode('nurbsCurve',n=prefix+'_offsetCrvShape')
	offsetCrv = mc.listRelatives(offsetCrvShape,p=True,pa=True)[0]
	mc.connectAttr(crv+'.worldSpace[0]',offsetCrvShape+'.create',f=True)
	return offsetCrv

def buildSubCurveDetach(crv):
	'''
	'''
	# Get Prefix
	prefix = glTools.utils.stringUtils.stripSuffix(crv)
	
	# Prep Curve
	mc.rebuildCurve(crv,ch=False,rpo=True,rt=0,end=1,kr=0,kcp=1,kep=1,kt=0,s=0,d=3)
	mc.delete(crv,ch=True)
	
	# Detach Curve
	detach = mc.detachCurve(crv,p=(0.001,0.999),k=(0,1,0),rpo=False)
	detachCrv = detach[1]
	detachNode = detach[-1]
	mc.delete(detach[0],detach[2])
	
	# Connect Detach Min/Max
	mc.addAttr(subCrv,ln='min',min=0,max=0.999,dv=0,k=True)
	mc.addAttr(subCrv,ln='max',min=0.001,max=1,dv=1,k=True)
	mc.addAttr(subCrv,ln='offset',min=-1,max=1,dv=1,k=True)
	minAdd = mc.createNode('addDoubleLinear',n=prefix+'_minAdd_addDoubleLinear')
	maxAdd = mc.createNode('addDoubleLinear',n=prefix+'_maxAdd_addDoubleLinear')
	minMaxClamp = mc.createNode('clamp',n=prefix+'_minMax_clamp')
	mc.connectAttr(subCrv+'.min',minAdd+'.input1',f=True)
	mc.connectAttr(subCrv+'.offset',minAdd+'.input2',f=True)
	mc.connectAttr(subCrv+'.max',maxAdd+'.input1',f=True)
	mc.connectAttr(subCrv+'.offset',maxAdd+'.input2',f=True)
	mc.connectAttr(minAdd+'.output',minMaxClamp+'.inputR',f=True)
	mc.connectAttr(maxAdd+'.output',minMaxClamp+'.inputB',f=True)
	mc.setAttr(minMaxClamp+'.min',0,0,0.0001)
	mc.setAttr(minMaxClamp+'.max',0.9999,0,0)
	mc.connectAttr(minMaxClamp+'.outputR',detachNode+'.parameter[0]',f=True)
	mc.connectAttr(minMaxClamp+'.outputB',detachNode+'.parameter[1]',f=True)
	
	# Return Result
	return detachCrv

def buildCurveRig(crv):
	'''
	'''
	# Get Prefix
	prefix = glTools.utils.stringUtils.stripSuffix(crv)
	
	# Build Joints
	pts = glTools.utils.base.getPointArray(crv)
	
	jnts = []
	mc.select(cl=True)
	for i in range(len(pts)):
		ind = glTools.utils.stringUtils.alphaIndex(i)
		jnt = mc.joint(p=pts[i],n=prefix+'_fk'+ind+'_jnt')
		mc.joint()
		mc.select(jnt)
	
	# Orient Joints
	
	# Build FK
	
	# Build Offset

def buildSubCurve(crv):
	'''
	'''
	# Build Sub Curve
	prefix = glTools.utils.stringUtils.stripSuffix(crv)
	subCrvShape = mc.createNode('nurbsCurve',n=prefix+'_subCrvShape')
	subCrv = mc.listRelatives(subCrvShape,p=True,pa=True)[0]
	subCrvNode = mc.createNode('subCurve',n=prefix+'_subCurve')
	
	# Connect Sub Curve
	mc.connectAttr(crv+'.worldSpace[0]',subCrvNode+'.inputCurve',f=True)
	mc.connectAttr(subCrvNode+'.outputCurve',subCrvShape+'.create',f=True)
	
	# Connect Sub Curve Min/Max
	mc.addAttr(subCrv,ln='min',min=0,max=0.999,dv=0,k=True)
	mc.addAttr(subCrv,ln='max',min=0.001,max=1,dv=1,k=True)
	mc.connectAttr(subCrv+'.min',subCrvNode+'.minValue',f=True)
	mc.connectAttr(subCrv+'.max',subCrvNode+'.maxValue',f=True)
	mc.setAttr(subCrvNode+'.relative',1)
	
	# Return Result
	return subCrv
	
def resetCV(cvs):
	'''
	'''
	# Check CVs
	if not cvs: return None
	cvList = mc.filterExpand(cvs,ex=True,sm=28)
	
	# Reset CVs
	for cv in cvList:
		crv = mc.ls(cv,o=True)[0]
		i = glTools.utils.component.index(cv)
		mc.setAttr(crv+'.controlPoints['+i+'].xValue',0)
		mc.setAttr(crv+'.controlPoints['+i+'].yValue',0)
		mc.setAttr(crv+'.controlPoints['+i+'].zValue',0)

def attachCurve(base,crv,cleanup=True):
	'''
	'''
	# Get Spans
	spans = mc.getAttr(crv+'.spans')
	mc.setAttr(base+'.spans',spans)
	
	# Match Shape
	shapeOrig = base+'ShapeOrig'
	mc.setAttr(shapeOrig+'.intermediateObject',0)
	mc.rebuildCurve(shapeOrig,ch=True,rpo=True,rt=0,end=1,kr=0,kcp=0,kep=1,kt=0,s=spans,d=3)
	bs = mc.blendShape(crv,shapeOrig)[0]
	mc.setAttr(bs+'.w[0]',1)
	
	# Delete Orig
	if cleanup:
		mc.delete(shapeOrig,ch=True)
		mc.delete(crv)
	
	# Restore Intermediate Shape
	mc.setAttr(shapeOrig+'.intermediateObject',1)
	
	# Return Result
	return

def attachToCurveParam(ctrl,crv):
	'''
	'''
	grp = mc.listRelatives(ctrl,p=True,pa=True)[0]
	param = mc.getAttr(ctrl+'.param')
	glTools.utils.attach.attachToCurve(crv,grp,param,uAttr='param')
	mc.connectAttr(ctrl+'.param',grp+'.param',f=True)

def addDropoffControls(locs,prefix):
	'''
	'''
	ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
	for i in range(len(locs)):
		pre = prefix+glTools.utils.stringUtils.stripSuffix(locs[i])
		wire = mc.listConnections(locs[i]+'.param',s=False,d=True)[0]
		param = mc.getAttr(locs[i]+'.param')
		ind = glTools.utils.attribute.getConnectionIndex(locs[i]+'.param')
		ctrl = ctrlBuilder.create('sphere',pre+'_ctrl')
		grp = glTools.utils.base.group(ctrl)
		mc.connectAttr(locs[i]+'.worldPosition[0]',grp+'.translate',f=True)
		mc.addAttr(ctrl,ln='param',min=0,max=1,dv=param,k=True)
		mc.addAttr(ctrl,ln='bulge',min=-1,dv=0,k=True)
		mc.connectAttr(ctrl+'.param',locs[i]+'.param['+str(ind)+']',f=True)
		mc.connectAttr(ctrl+'.bulge',wire+'.wireLocatorEnvelope['+str(ind)+']',f=True)
	


def buildTube(	crv
				profile=None,
				addCage=False,
				prefix=None)
	'''
	'''
	# Nurbs Tube
	mc.extrude(
		ch	= True,
		rn	= False,
		po	= 0,
		et	= 2,
		ucp	= 1,
		fpt	= 1,
		upn	= 1,
		rotation	=0,
		scale	= 1,
		rsp	= 1
		)
	
	# Polygon Tube
	mc.extrude(
		ch	= True,
		rn	= False,
		po	= 1,
		et	= 2,
		ucp	= 1,
		fpt	= 1,
		upn	= 1,
		rotation =0,
		scale =1,
		rsp	= 1
		)

#AbcExport -j "-frameRange 1 115 -ro -stripNamespaces -root |beetle_wrap_001_crv_export -root |beetle_wrap_002_crv_export -root |beetle_wrap_003_crv_export -root |beetle_wrap_004_crv_export -root |beetle_wrap_005_crv_export -root |beetle_wrap_006_crv_export -root |beetle_wrap_007_crv_export -root |beetle_wrap_008_crv_export -file /laika/jobs/kbo/vfx/seq/2900/0150/anm/workfile/cache/alembic/2900.0150.beetle_monkey_wrap_blocking.curves.012.abc";
#AbcImport -mode import -fitTimeRange -setToStartFrame -debug "/laika/jobs/kbo/vfx/seq/2900/0150/anm/workfile/cache/alembic/2900.0150.beetle_monkey_wrap_blocking.geometry.012.abc";

