from PySide import QtCore, QtGui

import maya.cmds as mc

class BaseListWidget(QtGui.QListWidget):
	
	def __init__(self, layout):
		
		super(BaseListWidget, self).__init__()
		
		self.parentLayout = layout
		
		self.widgets = []
		
		self.templateData = {}
		
		self.templateData['listText'] = None
		self.templateData['buttonText'] = 'Add'
		self.templateData['listItemType'] = 'float3'
	
	# ====================
	# Create
	# ====================	
	def create(self):
		self.createWidgets()
		self.addToLayout()
		self.connectSignals()
		self.addContextMenu()
			
	def addToLayout(self):
		for widget in self.widgets:
			self.parentLayout.addWidget(widget)
		
	def createWidgets(self):
		self.widgets = []
			
		self.labelTitle = QtGui.QLabel()
		if self.templateData['listText']:
			self.labelTitle.setText( self.templateData['listText'] )
			labelFont = self.labelTitle.font()
			labelFont.setPointSize(12)
			labelFont.setWeight(75)
			labelFont.setBold(False)
			labelFont.setFamily('Helvetica')
			self.labelTitle.setFont(labelFont)
			#self.labelTitle.setStyleSheet('font: bold large "Helvetica" ')
			self.widgets.append(self.labelTitle)
		
		self.listWidget = QtGui.QListWidget()
		self.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.widgets.append(self.listWidget)
		
		self.addButton = QtGui.QPushButton(self.templateData['buttonText'], parent=self)
		self.widgets.append(self.addButton)
		
		
	def connectSignals(self):
		self.connect(self.addButton, QtCore.SIGNAL("clicked()"), self.addItemsCallback)
		
	def addContextMenu(self):
		
		self.listWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
		
		# Add Select option
		selectAction = QtGui.QAction(self)
		selectAction.setText('Select')
		selectAction.triggered.connect(self.selectCallback)
		self.listWidget.addAction(selectAction)
		
		# Add Select All option
		selectAllAction = QtGui.QAction(self)
		selectAllAction.setText('Select All')
		selectAllAction.triggered.connect(self.selectAllCallback)
		self.listWidget.addAction(selectAllAction)
		
		# Add Clear option
		clearAction = QtGui.QAction(self)
		clearAction.setText('Clear')
		clearAction.triggered.connect(self.clearCallback)
		self.listWidget.addAction(clearAction)
		

	# ====================
	# Callbacks
	# ====================
	def addItemsCallback(self):
		
		self.listWidget.clear()
		
		sel = mc.ls(sl=True, fl=True, type=self.templateData['listItemType'])
		
		# why do I get indices for transform and shape?
		sel = [ i for i in sel if not i.count('Shape') ]  	
		
		for i in sel:
			item = QtGui.QListWidgetItem()
			
			item.setText(i)
			self.listWidget.addItem(item)
			
	def selectCallback(self):
		listText = self.getList()
		if len(listText) < 1: return
		
		mc.select(cl=True)
		mc.select(listText)
		
	def selectAllCallback(self):
		listText=[]
		for index in range(self.listWidget.count()):
				item = self.listWidget.item(index)
				listText.append(item.text())
		
		mc.select(cl=True)
		mc.select(listText)
		
	def clearCallback(self):
		self.listWidget.clear()
		
	# ====================
	# Return
	# ====================
	
	def getList(self):
		
		listText = []
		
		# collect return items
		if len(self.listWidget.selectedItems()) > 0:
		
			listText = [ item.text() for item in self.listWidget.selectedItems() ]
		
		else:

			for index in range(self.listWidget.count()):
				item = self.listWidget.item(index)
				listText.append(item.text())

		return listText
		
