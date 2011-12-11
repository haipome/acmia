#!/usr/bin/python
# -*- coding: utf-8 -*-

import cPickle
import os
import sys
from analyze import acmiAnalyze, dataTypeKey, fighterType, missileType, data2text
from PyQt4 import QtCore, QtGui

conf = 	{
		'winWidth' : 900,
		'winHeight' : 600,
		'cntStart' : 27,
		'comboWidth' : 85,
		'comboHeight' : 30,
		'comboGap' : 9,
		'btnStart' : 63,
		'btnWidth' : 180,
		'btnHeight' : 35,
		'btnNumber' : 12,
		'btnGap' : 5,
		'lineOut' : 5,
		'lineWidth' : 40,
		'lineHeight' : 25,
		'part' : 10,
		'textMove' : 8,
	}

butMsg = [
		u'导弹发射时角度高度统计',
		u'导弹发射时真空速度统计',
		u'导弹发射时马赫数统计',
		u'导弹发射时过载数据统计',
		u'导弹发射时俯仰角数据统计',
		u'导弹发射时相对距离统计',
		u'导弹发射时滚转角统计',
		u'命中时目标机高度速度统计',
		u'命中时相对角度高度统计',
		u'命中时相对距离统计',
		u'脱靶时目标机高度速度统计',
		u'脱靶时相对高度和角度统计',
	]

colors = [
		QtGui.QColor(97, 158, 132),
		QtGui.QColor(89, 166, 154),
		QtGui.QColor(83, 154, 172),
		QtGui.QColor(75, 128, 180),
		QtGui.QColor(68, 80, 187),
		QtGui.QColor(90, 61, 194),
		QtGui.QColor(132, 53, 202),
		QtGui.QColor(172, 47, 208),
		QtGui.QColor(218, 37, 186),
		QtGui.QColor(228, 27, 98),
	]

class acmia(QtGui.QMainWindow):
	
	global conf
	
	def __init__(self):
		
		super(acmia, self).__init__()
		
		self.initUI()
	
	def initUI(self):
		
		self.resize(conf['winWidth'], conf['winHeight'])
		
		self.setWindowTitle('ACMI Analysis')
		self.setWindowIcon(QtGui.QIcon('acmia.png'))
		
		self.initMenu()
		self.initButtons()
		self.initCombo()

		self.statusbar = self.statusBar()
		self.center()
	
	def initMenu(self):
		
		menubar = self.menuBar()
		
		exitAction = QtGui.QAction(QtGui.QIcon(''), u'退出', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip(u'退出程序')
		exitAction.triggered.connect(QtGui.qApp.quit)
		
		fileOpen = QtGui.QAction(QtGui.QIcon(''), u'打开', self)
		fileOpen.setShortcut('Ctrl+N')
		fileOpen.setStatusTip(u'打开 ACMI 文件')
		fileOpen.triggered.connect(self.openFile)
		
		fileMenu = menubar.addMenu(u'文件')
		fileMenu.addAction(fileOpen)
		fileMenu.addSeparator()
		fileMenu.addAction(exitAction)
		
		clearLog = QtGui.QAction(QtGui.QIcon(''), u'清空记录', self)
		clearLog.setStatusTip(u'清空所有历史记录')
		clearLog.triggered.connect(self.clearLog)
		
		resultSave = QtGui.QAction(QtGui.QIcon(''), u'输出结果', self)
		resultSave.setStatusTip(u'将结果输出为文本')
		resultSave.triggered.connect(self.result2txt)
		
		editMenu = menubar.addMenu(u'编辑')
		editMenu.addAction(resultSave)
		editMenu.addSeparator()
		editMenu.addAction(clearLog)
		
		aboutMsg = QtGui.QAction(QtGui.QIcon(''), u'关于软件', self)
		aboutMsg.setStatusTip(u'软件说明')
		aboutMsg.triggered.connect(self.about)
		
		aboutMenu = menubar.addMenu(u'关于')
		aboutMenu.addAction(aboutMsg)
	
	def initCombo(self):
		
		point1 = (0, conf['cntStart'])
		point2 = (conf['comboWidth'] + conf['comboGap'], conf['cntStart'])
		point3 = (0, conf['btnStart'] + 12 * (conf['btnHeight'] + conf['btnGap']))
		point4 = (conf['comboWidth'] + conf['comboGap'],
			conf['btnStart'] + 12 * (conf['btnHeight'] + conf['btnGap']))
		
		global combo1, combo2, combo3, combo4
		combo1 = QtGui.QComboBox(self)
		for name in fightersType:
			combo1.addItem(name)
		combo1.activated[str].connect(self.onActivated0)
		combo1.setGeometry(point1[0], point1[1],
			conf['comboWidth'], conf['comboHeight'])
		
		combo2 = QtGui.QComboBox(self)
		for name in missilesType:
			combo2.addItem(name)
		combo2.activated[str].connect(self.onActivated1)
		combo2.setGeometry(point2[0], point2[1],
			conf['comboWidth'], conf['comboHeight'])
		
		combo3 = QtGui.QComboBox(self)
		for name in fightersType:
			combo3.addItem(name)
		combo3.activated[str].connect(self.onActivated2)
		combo3.setGeometry(point3[0], point3[1],
			conf['comboWidth'], conf['comboHeight'])
		
		combo4 = QtGui.QComboBox(self)
		for name in missilesType:
			combo4.addItem(name)
		combo4.activated[str].connect(self.onActivated3)
		combo4.setGeometry(point4[0], point4[1],
			conf['comboWidth'], conf['comboHeight'])
	
	def initButtons(self):
		
		global butMsg
		
		for i in range(conf['btnNumber']):
			button =  QtGui.QPushButton(butMsg[i], self)
			button.clicked.connect(self.buttonClicked)
			button.setGeometry(0, conf['btnStart'] + i * (conf['btnHeight'] + conf['btnGap']),
				conf['btnWidth'], conf['btnHeight'])
	
	def buttonClicked(self):
		
		global titles
		
		sender = self.sender()
		self.statusBar().showMessage(sender.text())
		
		for i in range(len(butMsg)):
			if QtCore.QString(butMsg[i]) == sender.text():
				titles[0] = dataTypeKey[i * 2]
				titles[1] = dataTypeKey[i * 2 + 1]
				break
		
		self.paintRefresh()
	
	def onActivated0(self, text):
		
		global currentModles
		
		for i in range(len(fightersType)):
			if QtCore.QString(fightersType[i]) == text:
				currentModles[0] = fightersType[i]
				break
		self.paintRefresh()
		
	def onActivated1(self, text):
		
		global currentModles
		
		for i in range(len(missilesType)):
			if QtCore.QString(missilesType[i]) == text:
				currentModles[1] = missilesType[i]
				break
		self.paintRefresh()
		
	def onActivated2(self, text):
		
		global currentModles
		
		for i in range(len(fightersType)):
			if QtCore.QString(fightersType[i]) == text:
				currentModles[2] = fightersType[i]
				break
		self.paintRefresh()
		
	def onActivated3(self, text):
		
		global currentModles
		
		for i in range(len(missilesType)):
			if QtCore.QString(missilesType[i]) == text:
				currentModles[3] = missilesType[i]
				break
		self.paintRefresh()
	
	def clearLog(self):
		
		reply = QtGui.QMessageBox.question(self, u'',
			u"将清除所有的历史记录，你确定吗？", QtGui.QMessageBox.Yes | 
			QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			try:
				os.remove(logFile)
				os.remove(openFile)
				os.remove(weaponFile)
				initAcmia()
				self.paintRefresh()
				QtGui.QMessageBox.warning(self, u'', u'清除记录成功')
			except:
				QtGui.QMessageBox.warning(self, u'', u'清除记录失败')
	
	def result2txt(self):
		
		try:
			f = open(resultFile, 'w+')
			f.write(data2text(dataLog))
			f.close()
		except:
			QtGui.QMessageBox.warning(self, u'', u'结果输出失败')
			return
		QtGui.QMessageBox.warning(self, u'', u'结果保存在文件 %s 中' % resultFile)
	
	def openFile(self):
		
		global fileHistory, dataLog
		
		fnames = QtGui.QFileDialog.getOpenFileNames(self, u'按住ctrl可以选择多个文件',
			'/home', u"ACMi 文件(*.acmi)")
		fileNumber = len(fnames)
		sucessOpenNumber = 0
		sucessNumber = 0
		existeceNumber = 0
		hasError = 0
		if fileNumber == 0:
			return
		progress = QtGui.QProgressDialog(u"分析 ACMI 文件", u"取消", 0, fileNumber, self)
		progress.setWindowModality(QtCore.Qt.WindowModal)
		progress.setWindowTitle(u"数据分析")
		progress.open()
		progress.setValue(0)
		for i in range(fileNumber):
			progress.setLabelText(u"分析 ACMI 文件 %d/%d" % ((i + 1), fileNumber))
			progress.setValue(i)
			fname = str(fnames[i].toLocal8Bit())
			if progress.wasCanceled():
				break
			try:
				f = open(fname, 'r')
			except:
				continue
			sucessOpenNumber += 1
			f.seek(3)
			if fname not in fileHistory:
				try:
					analyzeData = acmiAnalyze(f)
				except:
					hasError += 1
				finally:
					fileHistory.append(fname)
					f.close()
					self.dataPlus(analyzeData, dataLog)
					save(dataLog, logFile)
					save(fileHistory, openFile)
					weaponType = [fightersType, missilesType]
					save(weaponType, weaponFile)
					sucessNumber += 1
			else:
				existeceNumber += 1
		progress.setValue(fileNumber)
		
		message = u"选择了 %d 个文件" % fileNumber
		if existeceNumber != 0:
			message += u", %d 个文件貌似已经分析过了" % existeceNumber
		if sucessOpenNumber != fileNumber:
			message += u", %d 个文件没有打开成功" % fileNumber - sucessNumber
		if sucessNumber != 0:
			message += u", %d 个文件分析成功" % sucessNumber
		# if hasError != 0:
		#	message += u", %d 个文件分析出错" % hasError
		QtGui.QMessageBox.warning(self, u'', message)
		self.paintRefresh()
	
	def paintRefresh(self):
		
		global datas, titiles, currentModles
		
		datas[0] = self.getData(titles[0], currentModles[0], currentModles[1])
		datas[1] = self.getData(titles[1], currentModles[2], currentModles[3])
		self.update()
	
	def getData(self, title, fighter, missile):
		
		global dataLog
		
		if title not in dataLog.keys():
			return []
		if fighter not in dataLog[title].keys():
			return []
		if missile not in dataLog[title][fighter].keys():
			return []
		return dataLog[title][fighter][missile]
	
	def dataPlus(self, data, dataLog):
		
		for dataType, typeData in data.items():
			if dataType not in dataLog.keys():
				dataLog[dataType] = {}
			for fighterName, fighterData in typeData.items():
				if fighterName not in dataLog[dataType].keys():
					dataLog[dataType][fighterName] = {}
					if fighterName not in fightersType:
						fightersType.append(fighterName)
						combo1.addItem(fighterName)
						combo3.addItem(fighterName)
				for missileName, missileData in fighterData.items():
					if missileName not in dataLog[dataType][fighterName].keys():
						dataLog[dataType][fighterName][missileName] = []
						if missileName not in missilesType:
							missilesType.append(missileName)
							combo2.addItem(missileName)
							combo4.addItem(missileName)
						for i in range(len(missileData)):
							dataLog[dataType][fighterName][missileName].append(missileData[i])
					else:
						for i in range(len(missileData)):
							dataLog[dataType][fighterName][missileName][i][1] += missileData[i][1]
		
	
	def about(self):
		
		QtGui.QMessageBox.about(self, u'关于软件', 
			u'作者：杨海坡\n邮箱：yang@haipo.me\n主页：www.haipo.me')
	
	def center(self):
		
		qr = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
		
	def paintEvent(self, e):
		
		qp = QtGui.QPainter()
		
		qp.begin(self)
		self.display(qp, e)
		qp.end()
	
	def display(self, qp, e):
		
		global colors, datas, titles
		
		width = self.contentsRect().width()
		height = self.contentsRect().height()
		
		pen = QtGui.QPen()
		qp.setPen(pen)
		
		center = (conf['btnWidth'], (conf['cntStart'] + height) / 2)
		
		qp.drawLine(0, height - conf['lineHeight'],
			width, height - conf['lineHeight'])
		qp.drawLine(conf['btnWidth'], conf['cntStart'], conf['btnWidth'], height)
		qp.drawLine(center[0], center[1], width, center[1])
		qp.drawLine(center[0], center[1] - conf['lineHeight'],
			width, center[1] - conf['lineHeight'])
		
		boxCenter1 = (center[0] + conf['lineWidth'], center[1] - 2 * conf['lineHeight'])
		boxCenter2 = (center[0] + conf['lineWidth'], height - 2 * conf['lineHeight'])
		boxWidth = width - conf['btnWidth'] - conf['lineWidth']
		boxHeight = (height - conf['cntStart'] - 4 * conf['lineHeight']) / 2
		
		
		qp.setPen(QtGui.QColor(0, 0, 255))
		
		qp.drawLine(center[0], boxCenter1[1],
			center[0] + boxWidth + conf['lineWidth'], boxCenter1[1])
		qp.drawLine(center[0], boxCenter2[1],
			center[0] + boxWidth + conf['lineWidth'], boxCenter2[1])
		qp.drawLine(boxCenter1[0], boxCenter1[1] - boxHeight,
			boxCenter1[0], boxCenter1[1] + conf['lineHeight'])
		qp.drawLine(boxCenter2[0], boxCenter2[1] - boxHeight,
			boxCenter2[0], boxCenter2[1] + conf['lineHeight'])
		
		qp.setPen(QtGui.QColor(153, 204, 255))
		
		stepWidth = float(boxWidth) / conf['part']
		stepHeight = float(boxHeight) / conf['part']
		
		for i in range(1, conf['part']):
			stdPoint = (boxCenter1[0] + i * stepWidth, boxCenter1[1])
			qp.drawLine(stdPoint[0], stdPoint[1] + conf['lineOut'],
				stdPoint[0], stdPoint[1] - boxHeight)
			stdPoint = (boxCenter1[0], boxCenter1[1] - i * stepHeight)
			qp.drawLine(stdPoint[0] - conf['lineOut'], stdPoint[1],
				stdPoint[0] + boxWidth, stdPoint[1])
			stdPoint = (boxCenter2[0] + i * stepWidth, boxCenter2[1])
			qp.drawLine(stdPoint[0], stdPoint[1] + conf['lineOut'],
				stdPoint[0], stdPoint[1] - boxHeight)
			stdPoint = (boxCenter2[0], boxCenter2[1] - i * stepHeight)
			qp.drawLine(stdPoint[0] - conf['lineOut'], stdPoint[1],
				stdPoint[0] + boxWidth, stdPoint[1])
		
		if len(titles) == 0:
			return
		qp.setPen(QtGui.QColor(0, 0, 0))
		qp.drawText(center[0] + conf['textMove'], center[1] - conf['textMove'], titles[0])
		qp.drawText(center[0] + conf['textMove'], 
			center[1] + boxHeight + 2 * conf['lineHeight'] - conf['textMove'], titles[1])
		
		if len(datas) == 0:
			return
		for center, data in [(boxCenter1, datas[0]), (boxCenter2, datas[1])]:
			
			if len(data) == 0:
				return
			keys = []
			values = []
			for item in data:
				keys.append(item[0])
				values.append(item[1])
			dataLen = len(values)
			dataMax = max(values)
			dataSum = sum(values)
			numberStep = dataMax // 9 + 1
			
			qp.setPen(QtGui.QColor(0, 0, 0))
			
			for i in range(1, conf['part']):
				qp.drawText(center[0] - 3 * conf['lineWidth'] / 5,
					center[1] - (2 * i - 1) * stepHeight / 2 - conf['textMove'],
					str(i * numberStep))
			for i in range(1, dataLen):
				qp.drawText(center[0]  + i * stepWidth - conf['textMove'],
					center[1] + conf['lineHeight'] - conf['textMove'],
					str(keys[i - 1]))
			for i in range(dataLen):
				unitNumber = float(values[i]) / numberStep
				unitLen = unitNumber * stepHeight
				qp.setBrush(colors[int(unitNumber)])
				qp.drawRect(center[0] + i * stepWidth,
					center[1] - unitLen, stepWidth, unitLen)
				if values[i] != 0:
					qp.drawText(center[0] + i * stepWidth + conf['textMove'],
					center[1] - unitLen - conf['textMove'],
					str(values[i]) + (' %.2f%%' % (float(values[i]) / dataSum * 100)) )



logFile = 'appdata.log'
openFile = 'fileopen.log'
weaponFile = 'weapontype.log'
resultFile = 'result.txt'

def initAcmia():
	
	global dataLog, fileHistory, datas, titles, currentModles, fightersType, missilesType
	
	dataLog = {}
	datas = []
	fileHistory = []
	titles = []
	weaponType = [[fighterType[0]], [missileType[0]]]
	
	if os.path.exists(logFile):
		f = open(logFile, 'r')
		dataLog = cPickle.load(f)
		f.close()

	if os.path.exists(openFile):
		f= open(openFile, 'r')
		fileHistory = cPickle.load(f)
		f.close()
	
	if os.path.exists(weaponFile):
		f= open(weaponFile, 'r')
		weaponType = cPickle.load(f)
		f.close()
	fightersType = weaponType[0]
	missilesType = weaponType[1]
	currentModles = [fighterType[0], missileType[0], fighterType[0], missileType[0]]
	datas = [[], []]
	titles = ['', '']

def save(data, fileName):
	f = open(fileName, 'w+')
	cPickle.dump(data, f)
	f.close()

def main():
	
	initAcmia()
	app = QtGui.QApplication(sys.argv)
	win = acmia()
	win.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()