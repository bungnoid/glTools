from PySide import QtCore, QtGui

import glTools.ui.qt.utils

class BaseWindow(QtGui.QDialog):
	'''
	
	'''
	def __init__(self, parent=glTools.ui.qt.utils.getMayaWindow()):
		'''
		Initialize the window.
		'''
		super(BaseWindow, self).__init__(parent)
		
		# style
		self.stylesheetPath = '/home/j/jfischer/dev/vfx_tools/etc/maya/common/python/glTools/ui/qt/darkBlue.qss'
		styleContents = open( self.stylesheetPath , 'r' )
		self.setStyleSheet( styleContents.read() )
		
		#Window title
		self.setWindowTitle('Overwrite in your new class')
		
		# ====================
		# create layouts
		# ====================
		
		self.mainLayout = QtGui.QVBoxLayout()
		self.setLayout(self.mainLayout)
		
		
		
	
	
				

