from Queue import Queue
from threading import Thread
from collections import deque, namedtuple
from math import sqrt, atan2, cos, sin, pi
from time import sleep, time

(SEARCH_PACKAGE, PACKAGE_DELIVERED, HAVE_SHIP_PATH) = range(0, 3)
(MOVE_ARM, HOOK_UP, HOOK_DOWN, GRAB, DROP, NOTHING) = range(10, 16)
(TAKE_OFF, PASS_ON, KEEP_BUSY) = range(20,23)

Message = namedtuple('Message', ['sender', 'type', 'data'])

class Crane:

	def __init__(self, id, position, rangeSight, reach, height, neighbours, map):
		self.id = id
		self.position = position
		self.rangeSight = rangeSight
		self.reach = reach
		self.height = height
		self.angle = 0 # in radians, clockwise
		self.hookDistance = 1
		self.hookHeight   = height
		self.neighbours   = neighbours
		self.map   = map

		self.messages = Queue()
		self.tasks = deque()
		self.instructions = deque()

		self.toShip = []
		self.inWay  = {}
		self.wanted = {}

		self.thread = self.createThread()
		self.running = True
		self.thread.start()

	def moveArm(self, alfa, dist):
		pass
	
	def hookDown(self, dist):
		pass

	def hookUp(self, dist):
		pass

	def grab(self):
		pass
	
	def drop(self):
		pass

	def doNothing(self):
		for i in range(0,5):
			self.angle += 0.1
			sleep(0.01)


	def moveContainer(self, pos1, pos2):
		def calcAngleAndShift(pos, armAngle, hookDist):
			(dx, dy) = (pos[0] - self.position[0], pos[1] - self.position[1])
			rotate = ((atan2(dy,dx) - armAngle + pi) % (2*pi)) - pi
			hookShift = sqrt(dy*dy + dx*dx) - hookDist
			return (rotate, hookShift)

		(rotate1, shift1) = calcAngleAndShift(pos1, self.angle, self.hookDistance)
		(rotate2, shift2) = calcAngleAndShift(pos2, self.angle+rotate1, self.hookDistance+shift1)
		stack1Size = 1
		stack2Size = 0

		return [
			(HOOK_UP, [self.height - self.hookHeight]),
			(MOVE_ARM, [rotate1, shift1]), 
			(HOOK_DOWN, [self.height - stack1Size]),
			(GRAB, []),
			(HOOK_UP, [self.height - self.hookHeight]),
			(MOVE_ARM, [rotate2, shift2]), 
			(HOOK_DOWN, [self.height - stack2Size]),
			(DROP, [])
		]

	def takeOff(self, pos):
		def findFreePosition():
			pass
		free = findFreePosition()
		return self.moveContainer(pos, free)

	def passOn(self, pos, craneId):
		def getCommonField(craneID):
			pass
		common = getCommonField(craneId)
		return self.moveContainer(pos, common)
	
	def keepBusy(self):
		return [(NOTHING, [])]

	def informOthers(self):
		for c in self.neighbours:
			if c not in self.toShip:
				c.sendMessage(Message(self, HAVE_SHIP_PATH, []))

	def startMeasureTime(self, containerId, craneId):
		self.inWay[containerId] = (craneId, time())

	def stopMeasureTime(self, containerId, stop):
		(craneId, start) = self.inWay[containerId]
		measure = start - stop
		del (self.inWay[containerId])
		return (craneId, measure)

	def sendMessage(self, msg):
		self.messages.put(msg)

	def addNeighbour(self, n):
		self.neighbours.append(n)

	def examineSurroundings(self):
		pass

	def readMessage(self, msg):
		if msg.type == SEARCH_PACKAGE:
			pass
		elif msg.type == PACKAGE_DELIVERED:
			if msg.data.containerId in self.inWay:
				self.stopMeasureTime(msg.data.stop)
		elif msg.type == HAVE_SHIP_PATH:
			self.toShip.append(msg.sender)
			self.informOthers()

	def readMessages(self, left=5):
		while (left > 0 and not self.messages.empty()):
			self.readMessage(self.messages.get())
			left -= 1

	def doInst(self, inst):
		cmd = {
			MOVE_ARM:  self.moveArm,
			HOOK_UP:   self.hookUp,
			HOOK_DOWN: self.hookDown,
			GRAB:      self.grab,
			DROP:      self.drop,
			NOTHING:   self.doNothing
		}.get(inst[0])
		cmd(*inst[1])
	
	def decomposeTask(self, task):
		dec = {
			TAKE_OFF:  self.takeOff,
			PASS_ON:   self.passOn,
			KEEP_BUSY: self.keepBusy
		}.get(task[0])
		return dec(*task[1])

	def isInArea(self, pos):
		(x, y) = self.position
		return max(abs(pos[0]-x), abs(pos[1]-y)) <= self.reach

	def doWork(self):
		if not self.tasks:
			if self.wanted and self.toShip:
				pass
			else:
				self.tasks.append((KEEP_BUSY, []))

		if not self.instructions:
			task = self.tasks.popleft()
			inst = self.decomposeTask(task)
			self.instructions.extend(inst)

		self.doInst(self.instructions.popleft())
	
	def mainLoop(self):
		while self.running:
			self.examineSurroundings()
			self.readMessages()
			self.doWork()

	def createThread(self):
		return Thread(target=self.mainLoop, args=[])

	def stop(self):
		self.running = False

