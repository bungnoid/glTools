import maya.cmds as mc

import maya.OpenMaya as OpenMaya

import glTools.utils.mesh

from math import sqrt
from copy import deepcopy

class Pt( object ):
	'''
	'''
	def __init__(self, pnt, ind):
		'''
		'''
		self.pnt = deepcopy(pnt)
		self.ind = ind

class _Node(list):
	'''
	Simple wrapper around tree nodes - mainly to make the code a little more readable (although
	members are generally accessed via indices because its faster)
	'''
	
	@property
	def point( self ): return self[0]
	@property
	def left( self ): return self[1]
	@property
	def right( self ): return self[2]
	
	def is_leaf( self ):
		return self[1] is None and self[2] is None

class ExactMatch(Exception): pass

class KdTree():
	'''
	'''
	DIMENSION = 3

	def __init__( self, mesh ):
		'''
		'''
		self.performPopulate( mesh )
	
	def performPopulate( self, mesh ):
		'''
		'''
		dimension = self.DIMENSION
		
		# Build Mesh Pt List
		meshFn = glTools.utils.mesh.getMeshFn(mesh)
		meshPtUtil = OpenMaya.MScriptUtil()
		meshPts = meshFn.getRawPoints()
		
		meshPtList = []
		for i in range(meshFn.numVertices()):
			pt = [	meshPtUtil.getFloatArrayItem(meshPts,i*3+0),
					meshPtUtil.getFloatArrayItem(meshPts,i*3+1),
					meshPtUtil.getFloatArrayItem(meshPts,i*3+2)	]
			
			meshPtList.append(Pt(pt,i))

		def populateTree( points, depth ):
			'''
			'''
			if not points: return None

			axis = depth % dimension

			# NOTE: this is slower than a DSU sort, but its a bit more readable, and the difference is only a few percent...
			points.sort( key=lambda point: point.pnt[ axis ] )

			# Find the half way point
			half = len( points ) / 2

			node = _Node( [ points[ half ],
							populateTree( points[ :half ], depth+1 ),
							populateTree( points[ half+1: ], depth+1 ) ] )

			return node

		self.root = populateTree( meshPtList, 0 )
	
	def getClosest( self, queryPoint, returnDistances=False ):
		'''
		Returns the closest point in the tree to the given point
		NOTE: see the docs for getWithin for info on the returnDistances arg
		'''
		dimension = self.DIMENSION
		
		distBest = ((self.root[0].pnt[0]-queryPoint[0]) ** 2) + ((self.root[0].pnt[1]-queryPoint[1]) ** 2) + ((self.root[0].pnt[2]-queryPoint[2]) ** 2)
		bestList = [ (distBest, self.root[0]) ]

		def search( node, depth ):
			'''
			'''
			nodePoint = node[0].pnt

			axis = depth % dimension

			if queryPoint[axis] < nodePoint[axis]:
				nearNode = node[1]
				farNode = node[2]
			else:
				nearNode = node[2]
				farNode = node[1]

			# Start Search
			if nearNode is not None:
				search( nearNode, depth+1 )

			# Get squared distance
			sd = 0
			for v1, v2 in zip( nodePoint, queryPoint ):
				sd += (v1 - v2)**2

			curBest = bestList[0][0]

			# If the point is closer than the currently stored one, insert it at the head
			if sd < curBest:
				bestList.insert( 0, (sd, node[0]) )

				# If exact match, bail
				if not sd:
					raise ExactMatch
			else:
				bestList.append( (sd, node[0]) )

			# Check whether there could be any points on the other side of the
			# splitting plane that are closer to the query point than the current best
			if farNode is not None:
				if (nodePoint[ axis ] - queryPoint[ axis ])**2 < curBest:
					search( farNode, depth+1 )

		try:
			search( self.root, 0 )
		except ExactMatch: pass

		if returnDistances:
			return bestList[0]

		return bestList[0][1]
	
	def getWithin( self, queryPoint, threshold=1e-6, returnDistances=False ):
		'''
		Returns all points that fall within the radius of the queryPoint within the tree.

		NOTE: if returnDistances is True then the squared distances between the queryPoint and the points in the
		return list are returned.  This means the return list looks like this:
		[ (sqDistToPoint, point), ... ]

		This can be useful if you need to do more work on the results afterwards - just be aware that the distances
		in the list are squares of the actual distance between the points
		'''
		dimension = self.DIMENSION
		axisRanges = axRangeX, axRangeY, axRangeZ = ( (queryPoint[0]-threshold, queryPoint[0]+threshold),
													  (queryPoint[1]-threshold, queryPoint[1]+threshold),
													  (queryPoint[2]-threshold, queryPoint[2]+threshold) )

		sqThreshold = threshold ** 2

		matches = []

		def search( node, depth ):
			'''
			'''
			nodePoint = node[0].pnt
			axis = depth % dimension
			
			if queryPoint[axis] < nodePoint[axis]:
				nearNode = node[1]
				farNode = node[2]
			else:
				nearNode = node[2]
				farNode = node[1]

			# Start Search
			if nearNode is not None:
				search( nearNode, depth+1 )

			# Test Point
			if axRangeX[0] <= nodePoint[ 0 ] <= axRangeX[1]:
				if axRangeY[0] <= nodePoint[ 1 ] <= axRangeY[1]:
					if axRangeZ[0] <= nodePoint[ 2 ] <= axRangeZ[1]:
						sd = 0
						for v1, v2 in zip( nodePoint, queryPoint ):
							sd += (v1 - v2)**2

						if sd <= sqThreshold:
							matches.append( (sd, node[0]) )

			if farNode is not None:
				if (nodePoint[ axis ] - queryPoint[ axis ])**2 < sqThreshold:
					search( farNode, depth+1 )
		
		search( self.root, 0 )
		
		# The best is guaranteed to be at the head of the list
		# But consequent points might be out of order - so order them now
		matches.sort()
		
		# Return Result
		if returnDistances: return matches
		return [ m[1] for m in matches ]
	
	def getDistanceRatioWeightedVector( self, queryPoint, ratio=2, returnDistances=False ):
		'''
		Finds the closest point to the queryPoint in the tree and returns all points within a distance
		of ratio*<closest point distance>.

		This is generally more useful that using getWithin because getWithin could return an exact
		match along with a bunch of points at the outer search limit and thus heavily bias the
		results.

		NOTE: see docs for getWithin for details on the returnDistance arg
		'''
		# Check Ratio
		assert ratio > 1
		
		# Get Closest
		closestDist, closest = self.getClosest( queryPoint, returnDistances=True )
		
		# Check Coincident
		if closestDist == 0:
			if returnDistances:
				return [ (0, closest) ]
			else:
				return [ closest ]
		
		# Get Dist / Max Dist
		closestDist = sqrt( closestDist )
		maxDist = closestDist * ratio
		
		# Return Result
		return self.getWithin( queryPoint, maxDist, returnDistances=returnDistances )

