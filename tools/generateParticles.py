import maya.mel as mm
import maya.cmds as mc

def locatorParticlesUI():
	'''
	'''
	# Define window
	locParticleUI = 'locatorParticleWindow'
	if mc.window(locParticleUI,q=True,ex=True): mc.deleteUI(locParticleUI)
	locParticleUI = mc.window(locParticleUI,t='Generate Particles')
	
	# UI Layout
	mc.columnLayout(adj=False,cal='left')
	partiTFG = mc.textFieldGrp('locParticle_particleTFG',label='Particle',text='',cw=[(1,100)])
	radiusFFG = mc.floatSliderGrp('locParticle_radiusFSG',label='radius',f=True,min=0.1,max=10.0,fmn=0.01,fmx=100.0,pre=2,v=1.0,cw=[(1,100)])
	rotateLocCBG = mc.checkBoxGrp('locParticle_rotateCBG',label='Add rotatePP',ncb=1,v1=0,cw=[(1,100)])
	scaleLocCBG = mc.checkBoxGrp('locParticle_scaleCBG',label='Add scalePP',ncb=1,v1=0,cw=[(1,100)])
	selfCollideCBG = mc.checkBoxGrp('locParticle_selfCollideCBG',label='self collide',ncb=1,v1=0,cw=[(1,100)])
	
	mc.button(l='Create Particles',c='glTools.tools.generateParticles.locatorParticlesFromUI()')
	
	# Popup menu
	mc.popupMenu(parent=partiTFG)
	for p in mc.ls(type=['particle','nParticle']):
		mc.menuItem(p,c='mc.textFieldGrp("'+partiTFG+'",e=True,text="'+p+'")')
	
	# Show Window
	mc.showWindow(locParticleUI)

def locatorParticlesFromUI():
	'''
	'''
	# Define window
	locParticleUI = 'locatorParticleWindow'
	if not mc.window(locParticleUI,q=True,ex=True): return
	
	# Get user selection
	sel = mc.ls(sl=True)
	if len(sel) == 1:
		if not mc.objExists(sel[0]+'.localScale'):
			sel = mc.listRelatives(sel[0],c=True,pa=True)
	locList = [i for i in sel if mc.objExists(i+'.localScale')]
	
	# Get Particle
	particle = mc.textFieldGrp('locParticle_particleTFG',q=True,text=True)
	if not particle: particle = 'nParticle1'
	radius = mc.floatSliderGrp('locParticle_radiusFSG',q=True,v=True)
	selfCollide = mc.checkBoxGrp('locParticle_selfCollideCBG',q=True,v1=True)
	rt = mc.checkBoxGrp('locParticle_rotateCBG',q=True,v1=True)
	sc = mc.checkBoxGrp('locParticle_scaleCBG',q=True,v1=True)
	
	# Execute generate particle command
	locatorParticles(locList,particle,radius,selfCollide,rotatePP=rt,scalePP=sc)
		
def locatorParticles(locList,particle,radius=1,selfCollide=False,rotatePP=False,scalePP=False):
	'''
	'''
	# Check locator list
	if not locList: return
	
	# Check particles
	if not particle: particle = 'particle1'
	if not mc.objExists(particle):
		particle = mc.nParticle(n=particle)[0]
	
	# Set Particle Object Attrs
	mc.setAttr(particle+'.particleRenderType',4)
	mc.setAttr(particle+'.radius',mc.floatSliderGrp('locParticle_radiusFSG',q=True,v=True))
	mc.setAttr(particle+'.selfCollide',mc.checkBoxGrp('locParticle_selfCollideCBG',q=True,v1=True))
	
	# Create particles
	ptList = [mc.pointPosition(i) for i in locList]
	mc.emit(o=particle,pos=ptList)
	
	# Add and Set RotatePP/ScalePP Values
	if rotatePP:
		
		# Check rotatePP attrs
		if not mc.objExists(particle+'.rotatePP'):
			addRotatePP(particle)
		
		# Set rotatePP attrs
		for i in range(len(locList)):
			rot = mc.getAttr(locList[i]+'.r')
			mc.particle(particle,e=True,at='rotatePP',id=i,vv=rot[0])
	
	if scalePP:
		
		# Check scalePP attrs
		if not mc.objExists(particle+'.scalePP'):
			addScalePP(particle)
		
		# Set scalePP attrs
		for i in range(len(locList)):
			scl = mc.getAttr(locList[i]+'.s')
			mc.particle(particle,e=True,at='scalePP',id=i,vv=scl[0])
	
	# Save Initial State
	mc.saveInitialState(particle)

def particleLocatorsUI():
	'''
	'''
	# Get current frame range
	start = mc.playbackOptions(q=True,min=True)
	end = mc.playbackOptions(q=True,max=True)
	
	# Define window
	particleLocatorsUI = 'particleLocatorsWindow'
	if mc.window(particleLocatorsUI,q=True,ex=True): mc.deleteUI(particleLocatorsUI)
	particleLocatorsUI = mc.window(particleLocatorsUI,t='Generate Locators')
	
	# UI Layout
	mc.columnLayout(adj=False,cal='left')
	partiTFG = mc.textFieldGrp('partiLoc_particleTFG',label='Particle',text='',cw=[(1,120)])
	prefixTFG = mc.textFieldGrp('partiLoc_prefixTFG',label='Prefix',text='',cw=[(1,120)])
	bakeAnimCBG = mc.checkBoxGrp('partiLoc_bakeAnimCBG',label='Bake Animation',ncb=1,v1=0,cw=[(1,120)])
	startEndIFG = mc.intFieldGrp('partiLoc_startEndISG',nf=2,label='Frame Range',v1=start,v2=end,cw=[(1,120)])
	
	rotateLocCBG = mc.checkBoxGrp('partiLoc_rotateCBG',label='Rotate (rotatePP)',ncb=1,v1=0,cw=[(1,120)])
	scaleLocCBG = mc.checkBoxGrp('partiLoc_scaleCBG',label='Scale (scalePP)',ncb=1,v1=0,cw=[(1,120)])
	
	mc.button(l='Create Locators',c='glTools.tools.generateParticles.particleLocatorsFromUI()')
	
	# Popup menu
	mc.popupMenu(parent=partiTFG)
	for p in mc.ls(type=['particle','nParticle']):
		mc.menuItem(p,c='mc.textFieldGrp("'+partiTFG+'",e=True,text="'+p+'")')
	
	# Show Window
	mc.showWindow(particleLocatorsUI)

def particleLocatorsFromUI():
	'''
	'''
	# Define window
	particleLocatorsUI = 'particleLocatorsWindow'
	if not mc.window(particleLocatorsUI,q=True,ex=True): return
	
	# Get Particle
	particle = mc.textFieldGrp('partiLoc_particleTFG',q=True,text=True)
	if not particle: raise Exception('Particle "'+particle+'" does not exist!!')
	
	# Get Options
	prefix = mc.textFieldGrp('partiLoc_prefixTFG',q=True,text=True)
	bake = mc.checkBoxGrp('partiLoc_bakeAnimCBG',q=True,v1=True)
	st = mc.intFieldGrp('partiLoc_startEndISG',q=True,v1=True)
	en = mc.intFieldGrp('partiLoc_startEndISG',q=True,v2=True)
	rotate = mc.checkBoxGrp('partiLoc_rotateCBG',q=True,v1=True)
	scale = mc.checkBoxGrp('partiLoc_scaleCBG',q=True,v1=True)
	
	# Create Locators
	particleLocators(particle,bakeSimulation=bake,rotate=rotate,scale=scale,start=st,end=en,prefix=prefix)

def particleLocators(particle,bakeSimulation=False,rotate=False,scale=False,start=0,end=-1,prefix=''):
	'''
	'''
	# Check Particle
	if not mc.objExists(particle):
		raise Exception('Object "'+nParticle+'" is not a valid particle or nParticle object!')
	
	# Check Prefix
	if not prefix: prefix = particle
	
	# Get particle count
	count = mc.getAttr(particle+'.count')
	if not count: raise Exception('Invalid particle count! ('+count+')')
	
	# Create locators
	partiLocs = [mc.spaceLocator(n=prefix+'_loc'+str(i))[0] for i in range(count)]
	partiLocsGrp = prefix+'_locGrp'
	if not mc.objExists(partiLocsGrp): partiLocsGrp = mc.group(em=True,n=partiLocsGrp)
	mc.parent(partiLocs,partiLocsGrp)
	
	# For each particle, set locator position
	for i in range(count):
		pt = mc.pointPosition(particle+'.pt['+str(i)+']')
		mc.setAttr(partiLocs[i]+'.t',*pt)
		if rotate:
			rt = mc.particle(particle,q=True,at='rotatePP',id=i)
			mc.setAttr(partiLocs[i]+'.r',*rt)
		if scale:
			sc = mc.particle(particle,q=True,at='scalePP',id=i)
			mc.setAttr(partiLocs[i]+'.s',*sc)
	
	# Bake Simulation
	if(bakeSimulation):
		
		# Append particle expression
		expStr = '\n\n//--\n'
		expStr += 'int $id = id;\n'
		expStr += 'vector $pos = pos;\n'
		expStr += 'string $loc = ("'+prefix+'_loc"+$id);\n'
		expStr += 'if(`objExists $loc`){'
		expStr += '\t move -a ($pos.x) ($pos.y) ($pos.z) $loc;\n'
		if rotate:
			expStr += '\tvector $rot = rotatePP;\n'
			expStr += '\t rotate -a ($rot.x) ($rot.y) ($rot.z) $loc;\n'
		if scale:
			expStr += '\tvector $scl = scalePP;\n'
			expStr += '\t scale -a ($scl.x) ($scl.y) ($scl.z) $loc;\n'
		expStr += '}'
		
		# Old expression string
		oldRadStr = mc.dynExpression(particle,q=True,s=True,rad=True)
		
		# Apply particle expression
		mc.dynExpression(particle,s=oldRadStr+expStr,rad=True)
		
		# Bake to keyframes
		if end < start:
			start = mc.playbackOptions(q=True,min=True)
			end = mc.playbackOptions(q=True,max=True)
		bakeAttrs = ['tx','ty','tz']
		if rotate: bakeAttrs.extend(['rx','ry','rz'])
		if scale: bakeAttrs.extend(['sx','sy','sz'])
		mc.bakeSimulation(partiLocs,at=bakeAttrs,t=(start,end))
		
		# Restore particle expression
		mc.dynExpression(particle,s=oldRadStr,rad=True)

def addRotatePP(particle):
	'''
	Add a per particle vector(Array) attribute named "rotatePP", to the specified particle object.
	An initial state attribute "rotatePP0" will also be created.
	@param particle: The particle or nParticle object to add the attribute to
	@type particle: str
	'''
	# Check Particle
	if not mc.objExists(particle):
		raise Exception('Particle "'+particle+'" does not exist!')
	if mc.objectType(particle) == 'transform':
		particleShape = mc.listRelatives(particle,s=True)
		if not particleShape:
			raise Exception('Unable to determine particle shape from transform "'+particle+'"!')
		else:
			particle = particleShape[0]
	if (mc.objectType(particle) != 'particle') and (mc.objectType(particle) != 'nParticle'):
		raise Exception('Object "'+particle+'" is not a valid particle or nParticle object!')
	
	# Add rotatePP attribute
	if not mc.objExists(particle+'.rotatePP0'):
		mc.addAttr(particle,ln='rotatePP0',dt='vectorArray')
	if not mc.objExists(particle+'.rotatePP'):
		mc.addAttr(particle,ln='rotatePP',dt='vectorArray')
	
	# Return Result
	return particle+'.rotatePP'

def addScalePP(particle):
	'''
	Add a per particle vector(Array) attribute named "scalePP", to the specified particle object.
	An initial state attribute "scalePP0" will also be created.
	@param particle: The particle or nParticle object to add the attribute to
	@type particle: str
	'''
	# Check Particle
	if not mc.objExists(particle):
		raise Exception('Particle "'+particle+'" does not exist!')
	if mc.objectType(particle) == 'transform':
		particleShape = mc.listRelatives(particle,s=True)
		if not particleShape:
			raise Exception('Unable to determine particle shape from transform "'+particle+'"!')
		else:
			particle = particleShape[0]
	if (mc.objectType(particle) != 'particle') and (mc.objectType(particle) != 'nParticle'):
		raise Exception('Object "'+particle+'" is not a valid particle or nParticle object!')
	
	# Add rotatePP attribute
	if not mc.objExists(particle+'.scalePP0'):
		mc.addAttr(particle,ln='scalePP0',dt='vectorArray')
	if not mc.objExists(particle+'.scalePP'):
		mc.addAttr(particle,ln='scalePP',dt='vectorArray')
	
	# Return Result
	return particle+'.scalePP'
