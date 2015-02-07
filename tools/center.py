import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.component
import glTools.utils.mathUtils

def centerPoint_average(ptList):
	'''
	Calculate the average center of the specified point list
	@param ptList: List of points to calculate the average center from
	@type ptList: list
	'''
	# Calculate Center (Average)
	avgPt = [0,0,0]
	numPt = len(ptList)
	for pt in ptList:
		pos = glTools.utils.base.getPosition(pt)
		avgPt = [avgPt[0]+pos[0],avgPt[1]+pos[1],avgPt[2]+pos[2]]
	avgPt = [avgPt[0]/numPt,avgPt[1]/numPt,avgPt[2]/numPt]
	
	# Return Result
	return avgPt

def centerPoint_geometric(ptList):
	'''
	Calculate the geometric center of the specified point list
	@param ptList: List of points to calculate the geometric center from
	@type ptList: list
	'''
	# Calculate Center (Geometric/BoundingBox)
	bbox = OpenMaya.MBoundingBox()
	for pt in ptList:
		pos = glTools.utils.base.getPosition(pt)
		bbox.expand(OpenMaya.MPoint(pos[0],pos[1],pos[2],1.0))
	cntPt = bbox.center()
	
	# Return Result
	return [cntPt.x,cntPt.y,cntPt.z]

def centerPointLocator(ptList,name=''):
	'''
	Create a locator at the average center of the specified point list
	@param ptList: List of points to calculate the average center from
	@type ptList: list
	@param name: Name for locator
	@type name: str
	'''
	# Determine center point
	avgPt = centerPoint_average(ptList)
	
	# Create locator
	if not name: name = 'locator#'
	loc = mc.spaceLocator(n=name)[0]
	
	# Position locator
	mc.move(avgPt[0],avgPt[1],avgPt[2],loc,ws=True,a=True)

def centerToGeometry(geo,obj=None):
	'''
	Position a specified object at the average center of the a given geometry
	@param obj: Object to position to geometry
	@type obj: str
	@param geo: Geometry to calculate the object position from
	@type geo: str
	'''
	# Check Object
	if not obj: obj = mc.spaceLocator(n=geo+'_center')[0]
	
	# Get Geometry Center
	geoPts = glTools.utils.component.getComponentStrList(geo)
	pt = centerPoint_average(geoPts)
	
	# Move Object to Geometry Center
	pos = glTools.utils.base.getPosition(obj)
	offset = glTools.utils.mathUtils.offsetVector(pos,pt)
	mc.move(offset[0],offset[1],offset[2],obj,ws=True,r=True)

def centerToPoints(ptList,obj):
	'''
	Position a specified object at the average center of the a given list of points
	@param obj: Object to position to geometry
	@type obj: str
	@param geo: Geometry to calculate the object position from
	@type geo: str
	'''
	# Get Geometry Center
	pt = centerPoint_average(ptList)
	
	# Move Object to Geometry Center
	pos = glTools.utils.base.getPosition(obj)
	offset = glTools.utils.mathUtils.offsetVector(pos,pt)
	mc.move(offset[0],offset[1],offset[2],obj,ws=True,r=True)
