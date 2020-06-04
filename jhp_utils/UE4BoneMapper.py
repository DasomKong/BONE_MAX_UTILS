# UE4 BoneMapper
import pymxs
import MaxPlus

from pymxs import runtime as rt

from PySide2.QtWidgets import (QApplication, QWidget, QComboBox, QLabel, QGroupBox,
QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton)
from PySide2 import QtCore
import PySide2.QtWidgets
# for file control
import json
from collections import OrderedDict
import math

import os

orderedKeys = [
        "Root",
        "Pelvis",
        "spine_01",
        "spine_02",
        "spine_03",
        "neck_01",
        "clavicle_l",
        "UpperArm_L",
        "lowerarm_l",
        "Hand_L",
        "thumb_01_l",
        "thumb_02_l",
        "thumb_03_l",
        "index_01_l",
        "index_02_l",
        "index_03_l",
        "middle_01_l",
        "middle_02_l",
        "middle_03_l",
        "ring_01_l",
        "ring_02_l",
        "ring_03_l",
        "pinky_01_l",
        "pinky_02_l",
        "pinky_03_l",
        "clavicle_r",
        "UpperArm_R",
        "lowerarm_r",
        "Hand_R",
        "thumb_01_r",
        "thumb_02_r",
        "thumb_03_r",
        "index_01_r",
        "index_02_r",
        "index_03_r",
        "middle_01_r",
        "middle_02_r",
        "middle_03_r",
        "ring_01_r",
        "ring_02_r",
        "ring_03_r",
        "pinky_01_r",
        "pinky_02_r",
        "pinky_03_r",
        "head",
        "Thigh_L",
        "calf_l",
        "Foot_L",
        "ball_l",
        "Thigh_R",
        "calf_r",
        "Foot_R",
        "ball_r"
    ]



defaultMapperFilePath = MaxPlus.PathManager.GetScriptsDir() + "\JHP\defaultMapper.json"

class _GCProtector(object):
    widgets = []

class UE4BoneMapper:
	# save, load mapped json data
	def __init__(self):
		# find root bone or select it or type it's name
		pass

	# data from mapper widget
	def recursiveChangeNames(self, bone, nameDict):
		cnt = bone.children.count
		
		# set bone name with data by value
		bone.name = nameDict.get(bone.name)
	
		for i in range(cnt):
			self.recursiveChangeNames(bone.children[i], nameDict)
			
	def recursiveGetSelectedBoneNames(self, bone, boneArray):
		cnt = bone.children.count
		
		boneArray.append(bone.name)
		
		for i in range(cnt):
			self.recursiveGetSelectedBoneNames(bone.children[i], boneArray)
			

# ------------------------------ main ------------------------------

class BoneMapperWindow(QWidget):
	class mapperWidget:
		rootWindow = None
		label = None
		combobox = None
		
		def __init__(self, root, labelName):
			self.rootWindow = root
			
			self.label = QLabel(self.rootWindow)
			self.label.setText(labelName)
			
			self.combobox =	QComboBox(self.rootWindow)
			
		
		def addLayout(self, group, row, column):
			group.addWidget(self.label, row, column)
			group.addWidget(self.combobox, row+1, column)
		
		def clear(self):
			self.combobox.clear()
		
		def setBoneNameItems(self, boneNode):
			nameArray = []
			self.rootWindow.boneMapperFunc.recursiveGetSelectedBoneNames(boneNode, nameArray)
			
			src = self.getTargetName().lower()
			
			for name in nameArray:
				self.combobox.addItem(name)
				
				if name.lower().find(src) != -1:
					self.combobox.setCurrentText(name)
				
				
		def getSelectedName(self):
			return self.combobox.currentText()
		
		def getTargetName(self):
			return self.label.text()
		
		def setSelectedName(self, name):
			if self.combobox.findText(name) == -1:
				self.combobox.addItem(name)
			self.combobox.setCurrentText(name)
			
	
	mapperWidgets = {}
	boneMapperFunc = None
	
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setWindowTitle('BoneMapper')
		
		self.boneMapperFunc = UE4BoneMapper()
		
		self.createBoneMapperUI(orderedKeys)
		
		self.applyMapperData(defaultMapperFilePath)
	
	def findBonesFromSelection(self):
		if rt.selection.count == 0:
			rt.messageBox("No Object Selected!")
			return
		
		for val in self.mapperWidgets.values():
			val.clear()
			val.setBoneNameItems(rt.selection[0])
	
	def checkIfSameBoneSelected(self):
		namesList = [val.getSelectedName() for val in self.mapperWidgets.values()]
		
		count = len(namesList)
		for i in range(count - 1):
			for j in range(i + 1, count):
				if namesList[i] == namesList[j]:
					return True
		
		return False
	
	def doBoneMapper(self):
		if rt.selection.count == 0:
			rt.messageBox("select Root Bone!")
		elif self.checkIfSameBoneSelected():
			rt.messageBox("same Bones are Selecetd!")
		else:
			# source : target . ex ) Bip001 Pelvis : (ue4)Pelvis
			# to find with key
			nameDict = {}
		
			for x in self.mapperWidgets.values():
				nameDict[x.getSelectedName()] = x.getTargetName()
					
			self.boneMapperFunc.recursiveChangeNames(rt.selection[0], nameDict)

	def createBoneMapperUI(self, ue4FormatStrArray):
		
		# create mapper UI
		mapper_box = QGroupBox("Mapper", self)
		groupBoxLayOut = QGridLayout(mapper_box)
		
		totalCnt = len(ue4FormatStrArray)
		div = 6.0
		
		cnt = int(math.ceil(totalCnt / div))
				
		for i in range(cnt):
			row = groupBoxLayOut.rowCount()
			
			self.mapperWidgets[ue4FormatStrArray[i]] = self.mapperWidget(self, ue4FormatStrArray[i])
			self.mapperWidgets[ue4FormatStrArray[i]].addLayout(groupBoxLayOut, row, 0)
			
			
			for j in range(1, int(div)):
				newCnt = i + cnt * j
				
				if newCnt  < totalCnt:
					self.mapperWidgets[ue4FormatStrArray[newCnt]] = self.mapperWidget(self, ue4FormatStrArray[newCnt])
					self.mapperWidgets[ue4FormatStrArray[newCnt]].addLayout(groupBoxLayOut, row, j)
		
		# create function button
		func_box = QGroupBox("function",self)
		hfuncboxlayout = QHBoxLayout(func_box)
		
		btn_setBones = QPushButton("findBones", self)
		btn_setBones.clicked.connect(self.findBonesFromSelection)
		
		btn_changeBoneName = QPushButton("SetBoneNames", self)
		btn_changeBoneName.clicked.connect(self.doBoneMapper)
		
		hfuncboxlayout.addWidget(btn_setBones)
		hfuncboxlayout.addWidget(btn_changeBoneName)
		
		# create file managing button
		file_box = QGroupBox("file",self)
		hboxlayout = QHBoxLayout(file_box)
		
		btn_save = QPushButton("&Save", self)
		btn_save.clicked.connect(self.saveFile)
		
		btn_load = QPushButton("&Load", self)
		btn_load.clicked.connect(self.loadFile)
		
		hboxlayout.addWidget(btn_save)
		hboxlayout.addWidget(btn_load)
		
		# set main layout
		main_layout = QVBoxLayout()
		main_layout.addWidget(mapper_box)
		main_layout.addWidget(func_box)
		main_layout.addWidget(file_box)
		
		self.setLayout(main_layout)
		
	def saveFile(self):
		filePath = rt.getSaveFileName(caption="Save Mapper File as", types="Json(*.json)|*.json")
		# order key : boneName save
		if filePath == None:
			return
			
		jsonData = OrderedDict()
		
		for i in range(len(orderedKeys)):
			jsonData[orderedKeys[i]] = self.mapperWidgets.get(orderedKeys[i]).getSelectedName()
		
		with open(filePath, 'w') as make_file:
			# python 2, json indent set with non-negative integer
			json.dump(jsonData, make_file, ensure_ascii=False, indent=5)
		
		rt.messageBox("Save Success!")

	
	def loadFile(self):
		filePath = rt.getOpenFileName(caption="Open Mapper File", types="Json(*.json)|*.json")
		
		self.applyMapperData(filePath)

	def applyMapperData(self, filePath):
		# bone name -> mapperWidget set text
		
		if os.access(filePath, os.W_OK):
			load = None
			
			with open(filePath, 'r') as json_data:
				load= json.load(json_data)
		
			load_keys = load.keys()
		
			for i in range(len(load_keys)):
				self.mapperWidgets.get(load_keys[i]).setSelectedName(load.get(load_keys[i]))
		else:
			rt.messageBox("there's no filePath name \"" + filePath + "\"")


# ------------------------------ main max ------------------------------
def openBoneMapperWindow():
	app = PySide2.QtWidgets.qApp
	if not app:
		app = QApplication([])
		
	mapperWindow = BoneMapperWindow()
	mapperWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	mapperWindow.show()
	#mapperWindow.adjustSize()
	
	_GCProtector.widgets.append(mapperWindow)
