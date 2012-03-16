import maya.mel as mm
import maya.cmds as mc

def createCurve(ptList,start,end,group=''):
	'''
	'''
	# Initialize Curves
	crvList = []
	for pt in ptList:
		pos = mc.pointPosition(pt)
		curve = mc.curve(p=[pos,pos],d=1)
		curve = mc.rename(curve,pt+'_curve')
		crvList.append(curve)
	
	# Track Curves
	for i in range(start,end+1):
		mc.currentTime(i)
		for n in range(len(ptList)):
			pos = mc.pointPosition(ptList[n])
			mc.curve(crvList[n],a=True,p=pos)
	
	# Remove Initial CV and Rebuild
	for crv in crvList:
		mc.delete(crv+'.cv[0]')
		mc.rebuildCurve(crv,ch=False,rpo=True,rt=0,end=1,kr=2,kcp=True,kep=True)
	
	# Group Curves
	if group:
		# Check Group
		if not mc.objExists(group): group = mc.group(em=True,n=group)
		# Parent Curves to Group
		mc.parent(crvList,group)
	
	# Return Result
	if group: return [group]
	else: return crvList
