import os

import glTools.ui.qt.baseWindow
import glTools.ui.qt.baseListWidget


from PySide import QtCore, QtGui

import maya.cmds as mc
import maya.mel as mm
import glTools.tools.inverseDistanceWeights
import glTools.tools.smoothWeights

import glTools.utils.skinCluster


class GraphProfiler(glTools.ui.qt.baseWindow.BaseWindow):
	
	
	def __init__(self):
		'''
		Initialize the window.
		'''
		super(GraphProfiler, self).__init__()
					
		self.uiData = {}
		
		#Window title
		self.setWindowTitle('Graph Profiler')
		
		
		vLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom)
		toolbarLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
		verticalLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom)
		
		self.mainLayout.addLayout(vLayout)
		vLayout.addLayout(toolbarLayout)
		vLayout.addLayout(verticalLayout)
		
		self.dataTableWidget = QtGui.QTableWidget(10,9,parent=self)
		self.startButton = QtGui.QPushButton('Start', parent=self)
		self.stopButton = QtGui.QPushButton('Stop', parent=self)
		self.resetButton = QtGui.QPushButton('Reset', parent=self)
		
		toolbarLayout.addWidget(self.startButton)
		toolbarLayout.addWidget(self.stopButton)
		toolbarLayout.addWidget(self.resetButton)
		verticalLayout.addWidget(self.dataTableWidget)
		
		self.connectSignals()
		
		self.dataFields = ['rank', 'On', 'self', 'Percent', 'Cumulative', 'Inclusive', 'Count', 'Type', 'Node']
		self.profileData={}
		
		self.dataTableWidget.verticalHeader().hide()
		self.dataTableWidget.setHorizontalHeaderLabels(self.dataFields)
		
	def connectSignals(self):
		self.connect(self.startButton, QtCore.SIGNAL("clicked()"), self.startCallback)
		self.connect(self.stopButton, QtCore.SIGNAL("clicked()"), self.stopCallback)
		self.connect(self.resetButton, QtCore.SIGNAL("clicked()"), self.resetCallback)
	
	def startCallback(self):
		self.startTimer()
		
	def stopCallback(self):
		self.stopTimer()
		self.collectProfileData()
		self.setDataInTable()
		
	def resetCallback(self):
		self.resetProfileData()
		self.dataTableWidget.clear()
		
	def startTimer(self):
		mc.dgtimer( on=True, reset=True )
		
	def stopTimer(self):
		mc.dgtimer( off=True )
		
	def resetProfileData(self):
		self.profileData={}
		
	def collectProfileData(self):
		
		results = mc.dgtimer(query=True, noHeader=True, outputFile='MEL')
		
		for index, result in enumerate(results):
			
			try: 
				resultList = result.split(' ')
			except:
				continue
				
			#self.dataFields = ['rank', 'On', 'self', 'Percent', 'Cumulative', 'Inclusive', 'Count', 'Type', 'Node']
			self.profileData[index]=[]
			
			for i, element in enumerate(resultList):
				if element != '': self.profileData[index].append(element)


		
	def setDataInTable(self):
		for row in self.profileData:
			
			entry  = self.profileData[row]
			
			for column, element in enumerate(entry):
				
				self.dataTableWidget.setRowCount(row+1)
				
				itemWidget = QtGui.QTableWidgetItem()
				itemWidget.setText(entry[column])
				self.dataTableWidget.setItem(row, column, itemWidget)
		
