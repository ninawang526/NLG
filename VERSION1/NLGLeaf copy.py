from queue import *
from NLGMessage import *

class NLGLeaf():
	# connector: sequence, elaboration, contrast, message
	def __init__(self, topic, type, connector, message=None):
		assert (type == 'root' or type == 'nucleus' or type == 'satellite')
		assert (connector == 'sequence' or connector == 'elaboration' or connector == "causal"
				or connector == 'contrast' or connector == 'message' or connector == "paragraph")

		self.topic = topic
		self.type = type
		self.connector = connector
		self.message = message
		self.children = []
		self.positivityScore = self.getPositivityScore()
		self.parent = None


	def addChild(self, node):
		assert isinstance(node, NLGLeaf)
		self.children.append(node)
		self.positivityScore = self.getPositivityScore()
		node.parent = self


	def getPositivityScore(self):
		positivityScore = 0
		if len(self.children) == 0 and self.connector == "message":
			if self.message.tone == "positive":
				positivityScore = 1

		for item in self.children:
			if item.connector == "message":
				if item.message.tone == "positive":
					positivityScore = positivityScore + 1
			else:
				positivityScore = positivityScore + item.positivityScore

		return positivityScore


	# DFS
	def getOrderedMessages(self):
		global tree
		tree = []

		initial_root = self
		self.DFSTraverse(initial_root)

		results = []
		for root in tree:
			if root.message is not None:
				results.append(root)

		return results


	def DFSTraverse(self, root):
		tree.append(root)

		if root.children is None:
			return

		for child in root.children:
			self.DFSTraverse(child)


	# BFS printing
	def printTree(self):
		global q
		q = Queue()

		global tree
		tree = []

		initial_root = self
		self.BFSTraverse(initial_root)

		for root in tree:
			if root.message is None:
				print ("(%s , %s, %d)" %(root.topic, root.connector, root.positivityScore))
			else:
				print ("(%s , %s, %s, %d)" %(root.topic, root.connector, root.message.name, root.positivityScore))


	def BFSTraverse(self, root):
		tree.append(root)

		for leaf in root.children:
			q.put(leaf)

		if q.empty():
			return
		nextRoot = q.get()
		self.BFSTraverse(nextRoot)
