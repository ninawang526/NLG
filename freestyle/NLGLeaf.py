from queue import *
from NLGMessage import *

class NLGLeaf():
	# connector: sequence, elaboration, contrast, message
	def __init__(self, topic, type, connector, message=None):
		assert (type == 'root' or type == 'nucleus' or type == 'satellite')
		assert (connector == 'sequence' or connector == 'elaboration' or connector == "description"
				or connector == 'contrast' or connector == 'addition' or connector == 'message'
				or connector == "paragraph")

		self.topic = topic
		self.type = type
		self.connector = connector
		self.message = message
		self.children = []
		self.parent = None


	def addChild(self, node):
		assert isinstance(node, NLGLeaf)
		self.children.append(node)
		#self.positivityScore = self.getPositivityScore()
		node.parent = self


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
				print ("(%s, %s)" %(root.topic, root.connector))
			else:
				print ("(%s, %s, %s)" %(root.topic, root.connector, root.message.name))


	def BFSTraverse(self, root):
		tree.append(root)

		for leaf in root.children:
			q.put(leaf)

		if q.empty():
			return
		nextRoot = q.get()
		self.BFSTraverse(nextRoot)
