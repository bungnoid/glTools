import maya.cmds as mc

import glTools.utils.curve

def fromRefCurve(curve,refCurve,rebuildToRef=True):
	'''
	'''
	# Get start and end reference points
	stRef = mc.pointOnCurve(refCurve,top=True,pr=0.0,p=True)
	enRef = mc.pointOnCurve(refCurve,top=True,pr=1.0,p=True)
	
	# Get boundary parameters
	stParam = glTools.utils.curve.closestPoint(curve,stRef)
	enParam = glTools.utils.curve.closestPoint(curve,enRef)
	
	# SubCurve
	subCurve = mc.detachCurve(curve,p=[stParam,enParam],replaceOriginal=False,ch=False)
	mc.delete(subCurve[0],subCurve[2])
	subCurve = mc.rename(subCurve[1],curve+'_subCurve')
	
	if rebuildToRef:
		degree = mc.getAttr(refCurve+'.degree')
		spans = mc.getAttr(refCurve+'.spans')
		mc.rebuildCurve(subCurve,ch=0,rpo=1,rt=0,end=1,kr=0,kcp=0,kep=1,kt=0,s=spans,d=degree,tol=0)
	
	# Return result
	return subCurve
	
def fromPoint(curve,pnt=[0.0,0.0,0.0],replaceOrig=False,keepHistory=True):
	'''
	'''
	# Get subCurve parameter
	param = glTools.utils.curve.closestPoint(curve,pnt)
	
	# Detach curve
	subCurve = mc.detachCurve(curve,p=param,replaceOriginal=replaceOrig,ch=keepHistory)
	
	# Return result
	return subCurve
