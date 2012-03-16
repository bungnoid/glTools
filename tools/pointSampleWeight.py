import maya.cmds as mc

import glTools.utils.mesh

def pointSampleWeight(samplePt,pntList,weightCalc=[True,True,True],prefix=''):
	'''
	'''
	# Check prefix
	if not prefix: prefix = 'triSampleWeight'
	
	# Get tri points
	posList = [	mc.xform(pntList[0],q=True,ws=True,rp=True),
				mc.xform(pntList[1],q=True,ws=True,rp=True),
				mc.xform(pntList[2],q=True,ws=True,rp=True)	]
	
	# Build pntFace mesh
	pntFace = mc.polyCreateFacet(p=posList,n=prefix+'_sample_mesh')[0]
	mc.setAttr(pntFace+'.inheritsTransform',0,l=True)
	
	# Attach triPt locator to pntFace mesh
	pntLoc = glTools.utils.mesh.locatorMesh(pntFace,prefix=prefix)
	
	# Attach follow pt
	followLoc = mc.spaceLocator(n=prefix+'_follow_locator')[0]
	followGeoCon = mc.geometryConstraint(pntFace,followLoc)
	followPntCon = mc.pointConstraint(samplePt,followLoc)
	
	# Calculate triArea
	triEdge1_pma = mc.createNode('plusMinusAverage',n=prefix+'_triEdge1Vec_plusMinusAverage')
	triEdge2_pma = mc.createNode('plusMinusAverage',n=prefix+'_triEdge2Vec_plusMinusAverage')
	mc.setAttr(triEdge1_pma+'.operation',2) # Subtract
	mc.setAttr(triEdge2_pma+'.operation',2) # Subtract
	mc.connectAttr(pntLoc[1]+'.worldPosition[0]',triEdge1_pma+'.input3D[0]',f=True)
	mc.connectAttr(pntLoc[0]+'.worldPosition[0]',triEdge1_pma+'.input3D[1]',f=True)
	mc.connectAttr(pntLoc[2]+'.worldPosition[0]',triEdge2_pma+'.input3D[0]',f=True)
	mc.connectAttr(pntLoc[0]+'.worldPosition[0]',triEdge2_pma+'.input3D[1]',f=True)
	
	triArea_vpn = mc.createNode('vectorProduct',n=prefix+'_triArea_vectorProduct')
	mc.setAttr(triArea_vpn+'.operation',2) # Cross Product
	mc.connectAttr(triEdge1_pma+'.output3D',triArea_vpn+'.input1',f=True)
	mc.connectAttr(triEdge2_pma+'.output3D',triArea_vpn+'.input2',f=True)
	
	triArea_dist = mc.createNode('distanceBetween',n=prefix+'_triArea_distanceBetween')
	mc.connectAttr(triArea_vpn+'.output',triArea_dist+'.point1',f=True)
	
	# Calculate triPt weights
	for i in range(3):
		
		# Check weight calculation (bool)
		if weightCalc[i]:
			
			# Calculate triArea
			pntEdge1_pma = mc.createNode('plusMinusAverage',n=prefix+'_pt'+str(i)+'Edge1Vec_plusMinusAverage')
			pntEdge2_pma = mc.createNode('plusMinusAverage',n=prefix+'_pt'+str(i)+'Edge2Vec_plusMinusAverage')
			mc.setAttr(pntEdge1_pma+'.operation',2) # Subtract
			mc.setAttr(pntEdge2_pma+'.operation',2) # Subtract
			mc.connectAttr(pntLoc[(i+1)%3]+'.worldPosition[0]',pntEdge1_pma+'.input3D[0]',f=True)
			mc.connectAttr(followLoc+'.worldPosition[0]',pntEdge1_pma+'.input3D[1]',f=True)
			mc.connectAttr(pntLoc[(i+2)%3]+'.worldPosition[0]',pntEdge2_pma+'.input3D[0]',f=True)
			mc.connectAttr(followLoc+'.worldPosition[0]',pntEdge2_pma+'.input3D[1]',f=True)
			
			pntArea_vpn = mc.createNode('vectorProduct',n=prefix+'_pt'+str(i)+'Area_vectorProduct')
			mc.setAttr(pntArea_vpn+'.operation',2) # Cross Product
			mc.connectAttr(pntEdge1_pma+'.output3D',pntArea_vpn+'.input1',f=True)
			mc.connectAttr(pntEdge2_pma+'.output3D',pntArea_vpn+'.input2',f=True)
			
			pntArea_dist = mc.createNode('distanceBetween',n=prefix+'_pt'+str(i)+'Area_distanceBetween')
			mc.connectAttr(pntArea_vpn+'.output',pntArea_dist+'.point1',f=True)
			
			# Divide ptArea by triArea to get weight
			pntWeight_mdn = mc.createNode('multiplyDivide',n=prefix+'_pt'+str(i)+'Weight_multiplyDivide')
			mc.setAttr(pntWeight_mdn+'.operation',2) # Divide
			mc.connectAttr(pntArea_dist+'.distance',pntWeight_mdn+'.input1X',f=True)
			mc.connectAttr(triArea_dist+'.distance',pntWeight_mdn+'.input2X',f=True)
			
			# Add weight attribute to pntLoc
			mc.addAttr(pntLoc[i],ln='weight',min=0.0,max=1.0,dv=0.0)
			mc.connectAttr(pntWeight_mdn+'.outputX',pntLoc[i]+'.weight',f=True)

	# Group mesh locators
	pntLoc_grp = mc.group(pntLoc,n=prefix+'_3Point_grp')
	mc.parent(pntFace,pntLoc_grp)
	
	# Return result
	return [pntLoc,pntFace,pntLoc_grp]
