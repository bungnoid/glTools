import os

import glTools.ui.qt.baseWindow
import glTools.ui.qt.baseListWidget


from PySide import QtCore, QtGui

import maya.cmds as mc
import maya.mel as mm
import glTools.tools.inverseDistanceWeights
import glTools.tools.smoothWeights

import glTools.utils.skinCluster


class WeightsManager(glTools.ui.qt.baseWindow.BaseWindow):
	
	
	def __init__(self):
		'''
		Initialize the window.
		'''
		super(WeightsManager, self).__init__()
					
		self.uiData = {}
		
		#Window title
		self.setWindowTitle('Weights Manager')
		
		
		horizontalLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
		vertexListLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom)
		jointListLayout  = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom)
		buttonLayout     = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom)
		
		
		self.mainLayout.addLayout(horizontalLayout)
		horizontalLayout.addLayout(vertexListLayout) # seperators?
		horizontalLayout.addLayout(jointListLayout)
		horizontalLayout.addLayout(buttonLayout)
		
		self.vertexListWidget =  glTools.ui.qt.baseListWidget.BaseListWidget(vertexListLayout)
		self.vertexListWidget.templateData['listText'] = 'Vertex List'
		self.vertexListWidget.templateData['buttonText'] = 'Add Vertices'
		self.vertexListWidget.templateData['listItemType'] = 'float3'
		self.vertexListWidget.create()
		
		self.jointListWidget =  glTools.ui.qt.baseListWidget.BaseListWidget(jointListLayout)
		self.jointListWidget.templateData['listText'] = 'Joint List'
		self.jointListWidget.templateData['buttonText'] = 'Add Joints'
		self.jointListWidget.templateData['listItemType'] = 'joint'
		self.jointListWidget.create()
		
		self.inverseWeightsButton = QtGui.QPushButton("Inverse Distance Weights", parent=self)
		self.smoothWeightsButton = QtGui.QPushButton("Smooth Weights", parent=self)
		self.weightHammerButton = QtGui.QPushButton("Weight Hammer", parent=self)
		buttonLayout.addWidget(self.inverseWeightsButton)
		buttonLayout.addWidget(self.smoothWeightsButton)
		buttonLayout.addWidget(self.weightHammerButton)
		
		
		self.connectSignals()
		
		
	
	def connectSignals(self):
		self.connect(self.inverseWeightsButton, QtCore.SIGNAL("clicked()"), self.inverseWeightsCallback)
		self.connect(self.smoothWeightsButton, QtCore.SIGNAL("clicked()"), self.smoothWeightsCallback)
		self.connect(self.weightHammerButton, QtCore.SIGNAL("clicked()"), self.weightHammerCallback)

		
	# ====================
	# UI Query's
	# ====================
	def queryUI(self):
		self.uiData={}
		
		self.uiData['vertices'] = self.vertexListWidget.getList()
		self.uiData['joints']   = self.jointListWidget.getList()
		
		
	# ====================
	# Callbacks
	# ====================
	
	def inverseWeightsCallback(self):
		self.queryUI()
		
		meshName = None
		if len(self.uiData['vertices']):
			meshName = self.uiData['vertices'][0].split('.')[0]
			
		skinCluster = None
		if meshName:
			skinCluster = glTools.utils.skinCluster.findRelatedSkinCluster(meshName)
		else:
			raise Exception("Not all vertices are deformed by a skinCluster")
		
		try:
			glTools.tools.inverseDistanceWeights.buildPointWeights(self.uiData['vertices'], self.uiData['joints'], skinCluster)
		except Exception, e:
			print "Warning :: Inverse Distance weights failed"
			print e

	def smoothWeightsCallback(self):
		self.queryUI()
		
		try:
			glTools.tools.smoothWeights.smoothWeights(vtxList=self.uiData['vertices'],
													faceConnectivity=True,
													showProgress=True)
		except:
			print "Warning :: smooth weights failed"
			
	def weightHammerCallback(self):
		self.queryUI()
		
		try:
			mc.select(cl=True)
			mc.select(self.uiData['vertices'])
			mm.eval('weightHammerVerts;')
			print 'Hammer Time!!!'
			mc.select(cl=True)
		except:
			print "Warning :: weight hammer failed"

