def xformToParticles(xformList=[]):
	'''
	'''
	if not xformList: xformList = mc.ls(sl=True,type='transform')
	ptList = [mc.xform(i,q=True,ws=True,rp=True) for i in xformList]
	particle = mc.particle(p=ptList)
	return particle
	
def xformToPoly(xformList=[],scale=0.1):
        '''
        '''
        if not xformList: xformList = mc.ls(sl=True,type='transform')
        ptList = [mc.xform(i,q=True,ws=True,rp=True) for i in xformList]
        polyList = [] # = [mc.plane(p=pt,s=0.00001) for pt in ptList]
        for pt in ptList:
        	poly = mc.polyPlane(w=scale,h=scale,sx=1,sy=1,ch=0)[0]
        	mc.move(pt[0],pt[1],pt[2],poly,ws=True)
        	polyList.append(poly)
        return polyList
