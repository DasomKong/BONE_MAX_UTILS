import MaxPlus
import pymxs

from pymxs import runtime as rt
from pymxs import attime as at

from PySide2 import QtCore
import PySide2.QtWidgets
from PySide2.QtWidgets import (QApplication, QWidget, QLineEdit,
QGroupBox, QVBoxLayout, QPushButton)

class _GCProtector(object):
    widgets = []

class XYZEnum:
	x = 0b001
	y = 0b010
	z = 0b100

class formatToUE4:
	data = None
	rootNode = None
	pelvisNode = None
	def __init__(self):
		self.data = {}
		
	def setRootNode(self, rootName):
		self.rootNode = rt.getNodeByName(rootName)
		
		if self.rootNode != rt.undefined:
			cnt = self.rootNode.children.count
			
			if cnt > 0:
				self.pelvisNode = self.rootNode.children[0]
			else:
				rt.messageBox("no children in node!")
			
		else:
			rt.messageBox("no bone name \"" + rootName + "\"")
		
	# with attime
	def doChangeJobWithattime(self):
		newRoot = rt.Dummy()
		newRoot.name = self.rootNode.name
		pelvisDum = rt.Dummy()
		pelvisDum.name = "pelvis"

		with pymxs.animate(True):
			for i in range(rt.animationRange.end + 1):
				with at(i):
					# root dum
					pos = self.rootNode.position
					pos.x = 0
					pos.z = 0
					newRoot.position = pos
			
					# pelvis dum
					pos = self.pelvisNode.position
					pos.y = 0
					pelvisDum.transform = self.pelvisNode.transform
					pelvisDum.position = pos
	
			self.pelvisNode.parent = rt.undefined

			for i in range(rt.animationRange.end + 1):
				with at(i):				
					self.pelvisNode.transform = pelvisDum.transform

		self.pelvisNode.parent = newRoot

		rt.delete(pelvisDum)
		rt.delete(self.rootNode)
		rootNode = 0


class formatChangerWindow(QWidget):
	class lineEditWithFocus(QLineEdit):
		def __init(self, parent=None):
			QWidget.__init__(self, parent)
	
		def focusInEvent(self, event):
			self.focusInOut(False)
	
		def focusOutEvent(self, event):
			self.focusInOut(True)
			
		def focusInOut(self, isOut):
			MaxPlus.CUI.EnableAccelerators() if isOut else MaxPlus.CUI.DisableAccelerators()
	
	changer = None
	rootNameLine = None
	
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setWindowTitle('AnimFormatChanger')
		
		self.changer = formatToUE4()
		
		mainBox = QGroupBox("Changer", self)
		mainLayout = QVBoxLayout(mainBox)
		
		#self.rootNameLine = QLineEdit(self)
		self.rootNameLine = self.lineEditWithFocus(self)
		self.rootNameLine.setPlaceholderText("type root node name")
		
		btn_ChangeFormat = QPushButton("&Change", self)
		btn_ChangeFormat.clicked.connect(self.onExecuteChange)
		
		mainLayout.addWidget(self.rootNameLine)
		mainLayout.addWidget(btn_ChangeFormat)
		
		self.setLayout(mainLayout)


	def onExecuteChange(self):
		self.changer.setRootNode(self.rootNameLine.text())
		
		if self.changer.rootNode == None or self.changer.pelvisNode == None:
			rt.messageBox("no bone selected in scene!")
		else:
			self.changer.doChangeJobWithattime()
	

def openAnimFormatChangeForUE4():
	app = PySide2.QtWidgets.qApp
	if not app:
		app = QApplication([])
	
	changerWindow = formatChangerWindow()
	changerWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	changerWindow.show()
	
	_GCProtector.widgets.append(changerWindow)
