#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import sin, cos, asin, acos, sqrt
import sys

dataTypeKey = [
		u'发射导弹时载机与目标机的角度关系',
		u'发射导弹时载机与目标机的高度差（米）',
		u'发射导弹时载机真空速度（千米每小时）',
		u'发射导弹时目标机真空速度（千米每小时）',
		u'发射导弹时载机马赫数',
		u'发射导弹时目标机马赫数',
		u'发射导弹时载机过载 (g)',
		u'发射导弹时目标机过载 (g)',
		u'发射导弹时载机攻角',
		u'发射导弹时目标机攻角',
		u'发射导弹时载机与目标机距离关系（千米）',
		u'空',
		u'发射导弹时载机滚转角',
		u'发射导弹时目标机滚转角',
		u'导弹命中时目标机速度（千米每小时）',
		u'导弹命中时目标机高度（米）',
		u'导弹命中时目标机与载机角度关系',
		u'导弹命中时目标机与载机高度关系（米）',
		u'导弹命中时目标机与载机距离关系（千米）',
		u'空',
		u'导弹脱靶时目标机速度（千米每小时）',
		u'导弹脱靶时目标机高度（米）',
		u'导弹脱靶时角度关系',
		u'导弹脱靶时高度关系（米）',
	]

fighterType = [u'所有飞机']
missileType = [u'所有导弹']

def gpsDistance(x, y):
	
	earthR = 6378.1
	PI = 3.14159265
	roundDegree = 360.0
	
	length = abs(x[0] - y[0]) / roundDegree * 2 * PI * earthR 
	width = abs(x[1] - y[1]) / roundDegree * 2 * PI * earthR * cos(x[0])
	height = abs(x[2] - y[2])
	
	return sqrt(width ** 2 + length ** 2 + height ** 2)

def gpsLocation(items):
	
	x = y = z = 0
	if items[1] != '?'and len(items[1]) != 0:
		x = float(items[2])
	if items[2] != '?'and len(items[2]) != 0:
		y = float(items[1])
	if items[3] != '?'and len(items[3]) != 0:
		z = float(items[3])
	return [x + LongitudeOffset, y + LatitudeOffset, z / 1000.0]

def findRecent(missileID, frame):
	
	missileLocation = []
	fighterLocation = []
	for line in frame:
		items = line[:-1].split(',')
		if items[0] == missileID:
			missileLocation = gpsLocation(items)
			break
	if len(missileLocation) == 0:
		return []
	minRecent = 100000.0
	for line in frame:
		items = line[:-1].split(',')
		if items[0] in fightersID:
			fighterLocation = gpsLocation(items)
			recent = gpsDistance(missileLocation, fighterLocation)
			if recent < minRecent:
				minRecent = recent
				fighterID = items[0]
	if minRecent == 100000.0 or minRecent > 1:
		return []
	else:
		return [missileID, fighterID,]

def getFighterName(fighterID):
	
	for fighter in fighters:
		if fighter[0] == fighterID:
			return fighter[1]
	return 'Not Found'

def getKeyFrame(i):
	
	if len(frames) < 3 or (i < 0 or i > len(frames)):
		return []
	if i == 0:
		return [frames[i], frames[i + 1], frame[i + 2]]
	elif i == len(frames) - 1:
		return [frames[i - 3], frames[i - 2], frames[i - 1]]
	else:
		return [frames[i - 2], frames[i - 1], frames[i + 1]]

def getTime(offset):
	
	now = MissionTime + float(offset)
	hour = int(now / 3600)
	minute = int((now - 3600 * hour) / 60)
	second = int(now - 3600 * hour - minute * 60)
	last = int((now - 3600 * hour - minute * 60 - second) * 100)
	return '%2d:%2d:%2d.%2d' % (hour, minute, second, last)

def calculateAngle(x, y):
	
	offset = 0
	negative = 1
	if y[0] < x[0]:
		offset = 90
	if y[1] < x[1]:
		negative = -1
	z = [x[0], y[1], 0]
	x[2] = 0
	y[2] = 0
	xy = gpsDistance(x, y)
	xz = gpsDistance(x, z)
	return negative * (asin(xz / xy) * 57.296 + offset)
	

def attackAngle(missile, way):
	
	a = b = []
	if way == 0:
		points = getKeyFrame(missile[4])
		for line in points[1]:
			items = line[:-1].split(',')
			if items[0] == missile[2]:
				a = gpsLocation(items)
				break
		for line in points[2]:
			items = line[:-1].split(',')
			if items[0] == missile[2]:
				b = gpsLocation(items)
				break
	elif len(missile) == 9:
		points = getKeyFrame(missile[8])
		for line in points[1]:
			items = line[:-1].split(',')
			if items[0] == missile[5]:
				a = gpsLocation(items)
				break
		for line in points[2]:
			items = line[:-1].split(',')
			if items[0] == missile[5]:
				b = gpsLocation(items)
	if not len(a) or not len(b):
		return False
	recent = gpsDistance(a, b)
	return asin((b[2] - a[2]) / recent) * 57.296

def angleRelation(missile, time, way, isHit):
	
	if len(missile) != 9:
		return False
	if time == 0:
		points = getKeyFrame(missile[4])
	elif missile[7] == isHit:
		points = getKeyFrame(missile[8] - 2)
	else:
		return False
	if len(points) == 0:
		return False
	a = b = c = []
	if way == 0:
		for line in points[1]:
			items = line[:-1].split(',')
			if items[0] == missile[2]:
				a = gpsLocation(items)
			elif items[0] == missile[5]:
				b = gpsLocation(items)
		for line in points[2]:
			items = line[:-1].split(',')
			if items[0] == missile[2]:
				c = gpsLocation(items)
	else:
		for line in points[1]:
			items = line[:-1].split(',')
			if items[0] == missile[5]:
				a = gpsLocation(items)
			elif items[0] == missile[2]:
				b = gpsLocation(items)
		for line in points[2]:
			items = line[:-1].split(',')
			if items[0] == missile[5]:
				c = gpsLocation(items)
	if not len(a) or not len(b) or not len(c):
		return False
	a[2] = b[2] = c[2] = 0
	angleAB = calculateAngle(a, b)
	angleAC = calculateAngle(a, c)
	angle = angleAC - angleAB
	if angle > 180:
		return angle - 360
	elif angle < -180:
		return angle + 360
	else:
		return angle

def calculateSpeed(missile, time, way, isHit):
	
	if time == 0:
		points = getKeyFrame(missile[4])
	elif way == 1:
		if len(missile) != 9:
			return False
		elif missile[7] == isHit:
			points = getKeyFrame(missile[8] - 2)
		else:
			return False
	if len(points) == 0:
		return False
	if way == 0:
		fighterID = missile[2]
	else:
		if len(missile) != 9:
			return False
		fighterID = missile[5]
	a = b = []
	time1 = time2 = 0
	for line in points[0]:
		if line[0] == '#':
			time1 = float(line[1:-1])
		items = line[:-1].split(',')
		if items[0] == fighterID:
			a = gpsLocation(items)
	for line in points[2]:
		if line[0] == '#':
			time2 = float(line[1:-1])
		items = line[:-1].split(',')
		if items[0] == fighterID:
			b = gpsLocation(items)
	if not len(a) or not len(b):
		return False
	if not time1 or not time2:
		return False
	ab = gpsDistance(a, b)
	return abs(ab * 1000 / (time2 - time1)) * 3.6

def speedMach(missile, way):
	
	speed = calculateSpeed(missile, 0, way, 0)
	return speed / 1225.0

def heightDiff(missile, way, isHit):
	
	if len(missile) != 9:
		return False
	if way == 1 and missile[7] != isHit:
		return False
	attackHeight = 0.0
	targetHeight = 0.0
	for line in frames[missile[4] + 1]:
		items = line[:-1].split(',')
		if items[0] == missile[2]:
			if items[3] != '?' and len(items[3]) != 0:
				attackHeight = float(items[3])
		elif items[0] == missile[5]:
			if items[3] != '?' and len(items[3]) != 0:
				targetHeight = float(items[3])
	if attackHeight == 0.0 or targetHeight == 0.0:
		return False
	if way == 0:
		return attackHeight - targetHeight
	else:
		return targetHeight - attackHeight

def calculateHight(missile, way, isHit):
	
	if way == 0:
		points = getKeyFrame(missile[4])
		for line in points[1]:
			items = line[:-1].split(',')
			if items[0] == missile[2]:
				return float(items[3])
	elif len(missile) == 9 and missile[7] == isHit:
		points = getKeyFrame(missile[8] - 2)
		for line in points[1]:
			items = line[:-1].split(',')
			if items[0] == missile[5]:
				return float(items[3])
	return False

def calculateOverLoad(points, missile, way, ID):
	
	keys = []
	for point in points:
		for line in point:
			items = line[:-1].split(',')
			if items[0] == ID:
				keys.append(gpsLocation(items))
	if len(keys) != 3:
		return False
	
	a = gpsDistance(keys[1], keys[0])
	b = gpsDistance(keys[1], keys[2])
	c = gpsDistance(keys[0], keys[2])
	if c >= (a + b):
		return 0
	R = (a * b * c) / sqrt((a + b + c) * (a + b - c) * (b + c - a) * (a + c - b))
	V = calculateSpeed(missile, 0, way, 0)
	
	return (((V / 3.6) ** 2) / (abs(R) * 1000)) / 9.8

def overLoad(missile, way):
	
	if way == 0:
		points = getKeyFrame(missile[4])
		return calculateOverLoad(points, missile, way, missile[2])
	elif len(missile) == 9:
		points = getKeyFrame(missile[8] -2)
		return calculateOverLoad(points, missile, way, missile[5])
	else:
		return False

def distance(missile, time, isHit):
	
	if len(missile) != 9:
		return False
	if time == 0:
		points = getKeyFrame(missile[4])
	elif missile[7] == isHit:
		points = getKeyFrame(missile[8] - 2)
	else:
		return False
	if len(points) == 0:
		return False
	a = b = []
	for line in points[1]:
		items = line[:-1].split(',')
		if items[0] == missile[2]:
			a = gpsLocation(items)
		elif items[0] == missile[5]:
			b = gpsLocation(items)
	if not len(a) or not len(b):
		return False
	return gpsDistance(a, b)

def rollAngle(missile, way):
	
	if way == 0:
		fighterID = missile[2]
		points = getKeyFrame(missile[4])
	elif len(missile) == 9:
		fighterID = missile[5]
		points = getKeyFrame(missile[4])
	else:
		return False
	if len(points) == 0:
		return False
	for line in points[1]:
		items = line[:-1].split(',')
		if items[0] == fighterID:
			if items[4] != '?' and len(items[4]) != 0:
				return float(items[4])
	return False

def acmiAnalyze(f):
	
	global fighters, fightersID, missiles, missilesID
	fighters = []
	fightersID = []
	missiles = []
	missilesID = []
	
	isMissile = '40'
	isFighter = '10'
	
	global LongitudeOffset, LatitudeOffset, MissionTime
	LongitudeOffset = 0.0
	LatitudeOffset = 0.0
	MissionTime = 0
	
	line = str()
	isEOF = False
	while True:
		line = f.readline()
		if len(line) == 0:
			isEOF = True
			break
		if line[0] == '#':
			break
		if line.startswith('LatitudeOffset'):
			LatitudeOffset = float(line[:-1].split('=')[1])
		elif line.startswith('LongitudeOffset'):
			LongitudeOffset = float(line[:-1].split('=')[1])
		elif line.startswith('MissionTime'):
			MissionTime = int(line[-10:-8]) * 3600 + int(line[-7:-5]) * 60 + int(line[-4:-2])
	global frames
	frames = []
	frame = []
	while not isEOF:
		frame = []
		frame.append(line)
		while True:
			line = f.readline()
			if len(line) == 0:
				isEOF = True
				break
			if line[0] == '#':
				break
			frame.append(line)
		frames.append(frame)
	missile = []
	for i in range(len(frames)):
		for line in frames[i]:
			if line[0] == '#':
				timeOffset = float(line[1:-1])
			if line[0] == '+':
				items = line[1:-1].split(',')
				if items[2] == isMissile:
					if items[5] not in missileType:
						missileType.append(items[5])
					missilesID.append(items[0])
					if items[1] != '?':
						missile = [tems[0], items[1]]
					elif i != len(frames):
						missile = findRecent(items[0], (frames[i] + frames[i + 1]))
					if len(missile) != 0:
						missile.insert(1, items[5])
						missile.append(getFighterName(missile[2]))
						missile.append(i)
						missiles.append(missile)
				elif items[2] == isFighter:
					if items[5] not in fighterType:
						fighterType.append(items[5])
					fightersID.append(items[0])
					fighters.append([items[0], items[5]])
			elif line[0] == '!':
				items = line[1:-1].split(',')
				if items[1] in missilesID:
					missile = findRecent(items[1], (frames[i - 1] + frames[i]))
					if len(missile) != 0:
						isHit = False
						for lline in (frames[i] + frames[i + 1]):
							if lline[0] == '!':
								iitems = lline[1:-1].split(',')
								if iitems[1] == missile[1]:
									isHit = True
									break
						for item in missiles:
							if item[0] == items[1]:
								item.append(missile[1])
								item.append(getFighterName(missile[1]))
								item.append(isHit)
								item.append(i)
	
	angleDivide = [
		[-45, 0],
		[-25, 0],
		[-10, 0],
		[-5, 0],
		[0, 0],
		[5, 0],
		[10, 0],
		[25, 0],
		[45, 0],
		[60, 0],
	]
	
	heightDiffDivide = [
		[-4000, 0],
		[-3000, 0],
		[-2000, 0],
		[-1000, 0],
		[0, 0],
		[1000, 0],
		[2000, 0],
		[3000, 0],
		[4000, 0],
		[5000, 0],
	]
	
	speedDivide = [
		[400, 0],
		[500, 0],
		[600, 0],
		[700, 0],
		[900, 0],
		[1100, 0],
		[1300, 0],
		[1500, 0],
		[1800, 0],
		[2000, 0],
	]
	
	machDivide = [
		[0.3, 0],
		[0.4, 0],
		[0.5, 0],
		[0.6, 0],
		[0.8, 0],
		[1.0, 0],
		[1.2, 0],
		[1.5, 0],
		[1.8, 0],
		[2.0, 0],
	]
	
	heightDivide = [
		[1000, 0],
		[2000, 0],
		[3000, 0],
		[4000, 0],
		[5000, 0],
		[7000, 0],
		[9000, 0],
		[11000, 0],
		[13000, 0],
		[20000, 0],
	]
	
	overLoadDivide = [
		[1, 0],
		[2, 0],
		[3, 0],
		[4, 0],
		[5, 0],
		[6, 0],
		[7, 0],
		[8, 0],
		[9, 0],
		[10, 0],
	]
	
	distanceDivide = [
		[1, 0],
		[3, 0],
		[5, 0],
		[10, 0],
		[15, 0],
		[20, 0],
		[30, 0],
		[50, 0],
		[70, 0],
		[100, 0],
	]
	
	analyzeData = {}
	for dataType in dataTypeKey:
		typeData = {}
		for fighterName in fighterType:
			fighterData = {}
			for missileName in missileType:
				missileData = []
				if dataType == dataTypeKey[0]:
					missileData = anCopyOf(angleDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = angleRelation(missile, 0, 0, False)
							if value > 145 or value < -145:
								print str(missile)
							setValue(missileData, value)
				elif dataType == dataTypeKey[1]:
					missileData = anCopyOf(heightDiffDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = heightDiff(missile, 0, False)
							setValue(missileData, value)
				elif dataType == dataTypeKey[2]:
					missileData = anCopyOf(speedDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = calculateSpeed(missile, 0, 0, False)
							setValue(missileData, value)
				elif dataType == dataTypeKey[3]:
					missileData = anCopyOf(speedDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = calculateSpeed(missile, 0, 1, False)
							setValue(missileData, value)
				elif dataType == dataTypeKey[4]:
					missileData = anCopyOf(machDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = speedMach(missile, 0)
							setValue(missileData, value)
				elif dataType == dataTypeKey[5]:
					missileData = anCopyOf(machDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = speedMach(missile, 1)
							setValue(missileData, value)
				elif dataType == dataTypeKey[6]:
					missileData = anCopyOf(overLoadDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = overLoad(missile, 0)
							setValue(missileData, value)
				elif dataType == dataTypeKey[7]:
					missileData = anCopyOf(overLoadDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = overLoad(missile, 1)
							setValue(missileData, value)
				elif dataType == dataTypeKey[8]:
					missileData = anCopyOf(angleDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = attackAngle(missile, 0)
							setValue(missileData, value)
				elif dataType == dataTypeKey[9]:
					missileData = anCopyOf(angleDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = attackAngle(missile, 1)
							setValue(missileData, value)
				elif dataType == dataTypeKey[10]:
					missileData = anCopyOf(distanceDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = distance(missile, 0, False)
							setValue(missileData, value)
				elif dataType == dataTypeKey[12]:
					missileData = anCopyOf(angleDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = rollAngle(missile, 0)
							setValue(missileData, value)
				elif dataType == dataTypeKey[13]:
					missileData = anCopyOf(angleDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = rollAngle(missile, 1)
							setValue(missileData, value)
				elif dataType == dataTypeKey[14]:
					missileData = anCopyOf(speedDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = calculateSpeed(missile, 1, 1, True)
							setValue(missileData, value)
				elif dataType == dataTypeKey[15]:
					missileData = anCopyOf(heightDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = calculateHight(missile, 1, True)
							setValue(missileData, value)
				elif dataType == dataTypeKey[16]:
					missileData = anCopyOf(angleDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = angleRelation(missile, 1, 1, True)
							setValue(missileData, value)
				elif dataType == dataTypeKey[17]:
					missileData = anCopyOf(heightDiffDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = heightDiff(missile, 1, True)
							setValue(missileData, value)
				elif dataType == dataTypeKey[18]:
					missileData = anCopyOf(distanceDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = distance(missile, 1, True)
							setValue(missileData, value)
				elif dataType == dataTypeKey[20]:
					missileData = anCopyOf(speedDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = calculateSpeed(missile, 1, 1, False)
							setValue(missileData, value)
				elif dataType == dataTypeKey[21]:
					missileData = anCopyOf(heightDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = calculateHight(missile, 1, False)
							setValue(missileData, value)
				elif dataType == dataTypeKey[22]:
					missileData = anCopyOf(angleDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = angleRelation(missile, 1, 1, False)
							setValue(missileData, value)
				elif dataType == dataTypeKey[23]:
					missileData = anCopyOf(heightDiffDivide)
					for missile in missiles:
						if isContinue(missile, fighterName, missileName):
							value = heightDiff(missile, 1, False)
							setValue(missileData, value)
				if notEmpty(missileData):
					fighterData[missileName] = missileData
			if len(fighterData) != 0:
				typeData[fighterName] = fighterData
		analyzeData[dataType] = typeData
	
	return analyzeData

def setValue(data, value):
	
	j = len(data)
	if value != False:
		if value < data[0][0]:
			data[0][1] += 1
		elif value > data[j - 2][0]:
			data[j - 1][1] += 1
		else:
			for item in data:
				if value < item[0]:
					item[1] += 1
					break

def isContinue(missile, fighterName, missileName):
	
	allFighter = fighterType[0]
	allMissile = missileType[0]
	rightMissile = (missileName == allMissile or missile[1] == missileName)
	rightFighter = (fighterName == allFighter or missile[3] == fighterName)
	return rightMissile and rightFighter

def notEmpty(data):
	
	i = 0
	for item in data:
		if len(item) >= 2 and item[1] > 0:
			i += 1
	return i

def anCopyOf(divide):
	
	copy = []
	for item in divide:
		copy.append(item[:])
	return copy

def main():
	
	if len(sys.argv) == 1:
		print 'usage: filename'
		sys.exit()
	else:
		fname = sys.argv[1]
	try:
		f = open(fname, 'r')
	except:
		sys.stderr.write("File %s don't exit" % fname)
		sys.exit()
	
	
	data = acmiAnalyze(f)
	
	print '%d fighters and %d missiles appear' % (len(fightersID), len(missilesID))
	print '%d fighters and %d missiles effective' % (len(fighters), len(missiles))
	hasTarget = 0
	hasHit = 0
	for missile in missiles:
		if len(missile) == 9:
			hasTarget = hasTarget + 1
			if missile[7] == True:
				hasHit = hasHit + 1
	print '%d missiles find target and %d hit' % (hasTarget, hasHit)
	
	for dataType, typeData in data.items():
		print '%s' % dataType.encode('utf-8')
		for fighterName, fighterData in typeData.items():
			print '  %s' % fighterName.encode('utf-8')
			for missileName, missileData in fighterData.items():
				print '     %s: %s' % (missileName.encode('utf-8'), str(missileData))
	
	f.close()

if __name__ == '__main__':
	
	main()