from Queue import Queue
from threading import Thread, Timer
from collections import deque, namedtuple
from time import sleep, time
from message import Message
import time
import threading
import thread

class Ship:

	def __init__(self, cranes, crates, topRow, bottomRow, timeInterval):
		self.topRow = topRow  # top row of the ship (ship's bow)
		self.bottomRow = bottomRow  # bottom row of the ship (ship's stern)
		self.timeInterval = timeInterval
		self.cranes = cranes
		self.crates = crates
		self.neededCrates = []
		self.running = True
		self.messages = Queue()
		self.createThread().start()

	def readMessage(self, msg):
		print "SHIP: crane", msg.sender.id, "sent message:", msg.data
		if msg.type == Message.PACKAGE_LOADED:
			t = time.time()
			self.neededCrates.remove(msg.data)
			for c in self.cranes:
				c.addMessage(Message(self, Message.PACKAGE_DELIVERED, [msg.data, t]))

	def readMessages(self, left=5):
		while (left > 0 and not self.messages.empty()):
			self.readMessage(self.messages.get())
			left -= 1  
		
	def mainLoop(self):
		part = 4
		a = 0
		b = len(self.crates) % part
		lastSendTime = time.time()
		while (self.running):
			if b <= len(self.crates) and time.time() - lastSendTime >= self.timeInterval:
				msg = Message(self, Message.SEARCH_PACKAGE, self.crates[a:b])
				self.neededCrates += self.crates[a:b]
				a = b
				b = b + part
				for i in xrange(len(self.cranes)):
					self.cranes[i].addMessage(msg)
				lastSendTime = time.time()
			self.readMessages()
		
	def createThread(self):
		return Thread(target=self.mainLoop, args=[])

	def addMessage(self, msg):
		self.messages.put(msg)

	def stop(self):
		self.running = False


