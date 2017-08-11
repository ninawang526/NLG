
# Fills message "name", "topic", and "arguments" fields from arguments given;
# calculates "tone" and "direction". Returns NLGMessage object.

class NLGMessage():

	def __init__(self, name, topic, arguments={}):
		assert isinstance(name, str)
		assert isinstance(topic, str)
		assert isinstance(arguments, dict)

		self.name = name
		self.topic = topic
		self.arguments = arguments

		if type == "description":
			self.tone = self.analyzeDescriptionTone(topic, arguments)
		else:
			self.tone = "neutral"


if __name__ == '__main__':
	args = {"current": 3, "average": 5}
	FillerCompareMsg = NLGMessage('FillerCompareMsg','filler', 'comparison', args)
	print FillerCompareMsg.name
	print FillerCompareMsg.topic
	print FillerCompareMsg.tone
	print FillerCompareMsg.direction
