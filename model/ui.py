import maya.cmds as mc

def displayListWindow(itemList,title):
	'''
	'''
	# Check itemList
	if not itemList: return
	
	# Window
	window = 'displayListWindowUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t=title,s=True)
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	TSL = mc.textScrollList('displayListWindowTSL',allowMultiSelection=True)
	for item in itemList: mc.textScrollList(TSL,e=True,a=item)
	mc.textScrollList(TSL,e=True,sc='glTools.ui.utils.selectFromTSL("'+TSL+'")')
	closeB = mc.button('displayListWindowB',l='Close',c='mc.deleteUI("'+window+'")')
	
	# Form Layout
	mc.formLayout(FL,e=True,af=[(TSL,'top',5),(TSL,'left',5),(TSL,'right',5)])
	mc.formLayout(FL,e=True,af=[(closeB,'bottom',5),(closeB,'left',5),(closeB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(TSL,'bottom',5,closeB)])
	
	# Display Window
	mc.showWindow(window)

def reportWindow(msg,title):
	'''
	'''
	# Check message
	if not msg: return
	
	# Window
	window = 'reportWindowUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,t=title,s=True)
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	reportSF = mc.scrollField('reportWindowSF',editable=False,wordWrap=True,text=msg)
	closeB = mc.button('reportWindowB',l='Close',c='mc.deleteUI("'+window+'")')
	
	# Form Layout
	mc.formLayout(FL,e=True,af=[(reportSF,'top',5),(reportSF,'left',5),(reportSF,'right',5)])
	mc.formLayout(FL,e=True,af=[(closeB,'bottom',5),(closeB,'left',5),(closeB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(reportSF,'bottom',5,closeB)])
	
	# Display Window
	mc.showWindow(window)
