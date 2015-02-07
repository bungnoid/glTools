import maya.cmds as mc
import maya.mel as mm

import glTools.utils.base
import glTools.utils.mathUtils
import glTools.utils.skinCluster
import glTools.utils.progressBar

def buildPointWeights(	points,
						influenceList,
						skinCluster,
						maxInfluences = 3 ):
	'''
	Build and execute skinPercent commands to apply distance based weights given a list of deformed components and a list of influences.
	Weights are calculated using an inverse distance function using a set number of influences per point.
	@param points: List of deformed points to calculate skin weights for
	@type points: list
	@param influenceList: List of skinCluster influences to calculate weights from
	@type influenceList: list
	@param skinCluster: SkinCluster to apply weights to
	@type skinCluster: str
	@param maxInfluences: Number of influences per component
	@type maxInfluences: int
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Build Influence Points
	influencePts = [glTools.utils.base.getPosition(i) for i in influenceList]
	
	# Add Missing Influences
	skinInfList = mc.skinCluster(skinCluster,q=True,inf=True)
	missingInfList = list(set(influenceList)-set(skinInfList)) or []
	for inf in missingInfList:
		mc.skinCluster(skinCluster,e=True,addInfluence=inf,lockWeights=True)
	for inf in missingInfList:
		mc.setAttr(inf+'.liw',0)
	
	# =======================
	# - Build Point Weights -
	# =======================
	
	#glTools.utils.progressBar.init('Beginning Weights', len(points)/10)

	cmd = ''
	ptWts = {}
	for i, pt in enumerate(points):
		
		ptPos = glTools.utils.base.getPosition(pt)
		wt, influenceID = calcPointWeights(ptPos,influencePts,maxInfluences)
		ptWts[pt] = [influenceID, wt]
		
	cmd += buildSkinPercentCmd(pt, influenceList, wt, skinCluster, ptWts)
		
	#if not i%10: glTools.utils.progressBar.update(1,'Generating Weights')
	
	# =================
	# - Return Result -
	# =================
	
	#glTools.utils.progressBar.end()
	
	# Run Cmd
	mm.eval(cmd)
	
def calcPointWeights(	pos,
						influencePts,
						maxInfluences,
						smoothInterp	= True ):
	'''
	Calculate inverse distance weights
	@param pos: Point to calculate weights for
	@type pos: str or list
	@param influencePts: List of influence points to calculate weights from
	@type influencePts: str
	@param maxInfluences: Maximum number of influences per point
	@type maxInfluences: int
	@param smoothInterp: Smooth interpolation of weights.
	@type smoothInterp: bool
	'''
	# Get Point Position
	pt = glTools.utils.base.getPosition(pos)
	
	# Sort By Distance
	dist = [glTools.utils.mathUtils.distanceBetween(pt,i) for i in influencePts]
	distSorted = sorted(dist)
	closestID = [dist.index(distSorted[i]) for i in range(maxInfluences)]
	
	# Calculate Inverse Distance Weight
	ptArray = [influencePts[i] for i in closestID]
	wt = glTools.utils.mathUtils.inverseDistanceWeight3D(ptArray,pt)
	if smoothInterp:
		wt = [ glTools.utils.mathUtils.smoothStep(x) for x in wt ]
	infWt = [wt[closestID.index(i)] if i in closestID else 0.0 for i in range(len(influencePts))]
	
	
	# Return Result
	return infWt, closestID

def buildSkinPercentCmd(	pt,
							influenceList,
							wts,
							skinCluster,
							ptWts ):
	'''
	Build skinPercent command
	@param pt: Deformed component to build weight command for
	@type pt: str
	@param influenceList: List of influences to apply weights for
	@type influenceList: list
	@param wts: List of weight values to apply
	@type wts: list
	@param skinCluster: SkinCluster to apply weight to
	@type skinCluster: str
	@param ptWts:
	@type ptWts:
	'''
	x = 0
	cmd = ''
	for vertex in ptWts:
		transValues = ''
		for i, n in enumerate(ptWts[vertex][0]):
			transValues += '-transformValue "%s" %s ' % (influenceList[n], ptWts[vertex][1][n])
		cmd += 'skinPercent %s "%s" "%s";\n' % (transValues, skinCluster, vertex)
		x+=1
	
	print "vertices :: %s " % len(ptWts)
	print "influences :: %s" % len(influenceList)
	print "generated %s skinPercent cmds" % x
	print cmd
	return cmd
