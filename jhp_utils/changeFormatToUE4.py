import MaxPlus
import pymxs

from pymxs import runtime as rt
from pymxs import attime as at

from PySide2 import QtCore
import PySide2.QtWidgets
from PySide2.QtWidgets import (QApplication, QWidget, QLineEdit,
QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox)

defaultRootNodeName = "Bip001"
toeNames = ["Bip001 L Toe0", "Bip001 R Toe0"]

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
	def doChangeJobWithattime(self,changeWindow):
		# set animation range again
		start = 0
		end = 0
		
		if changeWindow.useManualCheckBox.isChecked():
			s = changeWindow.rangeMin.text()
			e = changeWindow.rangeMax.text()

			if not s.isdecimal() or not e.isdecimal():
				rt.messageBox("not numeric values in range!")
				return
				
			start = int(s)
			end = int(e)
			
		else:
			c = self.rootNode.getmxsprop('position.controller')
			
			count = c.keys.count

			start = c.keys[0].time
			end = c.keys[count - 1].time
			
		rt.animationRange = rt.Interval(start, end)
		
		# set dummies
		newRoot = rt.Dummy()
		newRoot.name = self.rootNode.name
		pelvisDum = rt.Dummy()
		pelvisDum.name = "pelvis"
		
		rootZCheck = changeWindow.IncludeRootZCheckBox.isChecked()
		
		lToe = None
		rToe = None
		
		if rootZCheck:
			lToe = rt.getNodeByName(toeNames[0])
			rToe = rt.getNodeByName(toeNames[1])

		RootZOffset = 0
		p2rZOffset = 0
		
		with pymxs.animate(True):
			for i in range(rt.animationRange.end + 1):
				with at(i):
					# root dum
					rtPos = self.rootNode.position
					# pelvis dum
					pelPos = self.pelvisNode.position
					
					if lToe != None and rToe != None:
						lTPos = lToe.position
						rTPos = rToe.position
						
						rtPos.z = ((lTPos + rTPos) * 0.5).z
						
						if i == 0:
							RootZOffset = rtPos.z
							p2rZOffset = pelPos.z
						
						# z move amount
						rtPos.z -= RootZOffset
						pelPos.z -= rtPos.z
							
					# just XY axis root motion
					else:
						rtPos.z = 0
					
					pelPos.y = 0
					pelPos.x = 0
					
					newRoot.position = rtPos
			
					pelvisDum.transform = self.pelvisNode.transform
					pelvisDum.position = pelPos
	
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
	rangeMin = None
	rangeMax = None
	useManualCheckBox = None
	
	IncludeRootZCheckBox = None
	
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setWindowTitle('AnimFormatChanger')
		
		self.changer = formatToUE4()
		
		mainBox = QGroupBox("Changer", self)
		mainLayout = QVBoxLayout(mainBox)
		
		#self.rootNameLine = QLineEdit(self)
		self.rootNameLine = self.lineEditWithFocus(self)
		self.rootNameLine.setText(defaultRootNodeName)
		self.rootNameLine.setPlaceholderText("type root node name")
				
		# anim range
		self.useManualCheckBox = QCheckBox("S&etManual", self)
		self.useManualCheckBox.stateChanged.connect(self.checkBoxStateChange)
		
		rangeBox = QGroupBox("AnimationRange", self)
		rangeLayout = QHBoxLayout(rangeBox)
		
		self.rangeMin = self.lineEditWithFocus(self)
		self.rangeMin.setText('0')
		self.rangeMin.setPlaceholderText("min")
		
		self.rangeMax = self.lineEditWithFocus(self)
		self.rangeMax.setText('100')
		self.rangeMax.setPlaceholderText("max")

		self.setRangeEditWritable(True)
		
		rangeLayout.addWidget(self.rangeMin)
		rangeLayout.addWidget(self.rangeMax)
		
		self.IncludeRootZCheckBox = QCheckBox("CalcRootZ", self)
		
		# button
		btn_ChangeFormat = QPushButton("&Change", self)
		btn_ChangeFormat.clicked.connect(self.onExecuteChange)
				
		mainLayout.addWidget(self.rootNameLine)
		mainLayout.addWidget(btn_ChangeFormat)
		mainLayout.addWidget(self.useManualCheckBox)
		mainLayout.addWidget(rangeBox)
		mainLayout.addWidget(self.IncludeRootZCheckBox)
		
		self.setLayout(mainLayout)

	def checkBoxStateChange(self):
		self.setRangeEditWritable(not self.useManualCheckBox.isChecked())

	def setRangeEditWritable(self, isOn):
		self.rangeMin.setReadOnly(isOn)
		self.rangeMax.setReadOnly(isOn)

	def onExecuteChange(self):
		self.changer.setRootNode(self.rootNameLine.text())
		
		if self.changer.rootNode == None or self.changer.pelvisNode == None:
			rt.messageBox("no bone selected in scene!")
		else:
			self.changer.doChangeJobWithattime(self)
	

def openAnimFormatChangeForUE4():
	app = PySide2.QtWidgets.qApp
	if not app:
		app = QApplication([])
	
	changerWindow = formatChangerWindow()
	changerWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	changerWindow.show()
	
	_GCProtector.widgets.append(changerWindow)
