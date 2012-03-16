import maya.cmds as mc

def centerPointLocator(ptList,name=''):
	'''
	'''
	# Determine center point
	numPt = len(ptList)
	avgPt = [0,0,0]
	for pt in ptList: avgPt = [avgPt[0]+pt[0],avgPt[1]+pt[1],avgPt[2]+pt[2]]
	avgPt = [avgPt[0]/numPt,avgPt[1]/numPt,avgPt[2]/numPt]
	
	# Create locator
	if not name: name = 'locator#'
	loc = mc.spaceLocator(n=name)[0]
	
	# Position locator
	mc.move(avgPt[0],avgPt[1],avgPt[2],loc,ws=True,a=True)
