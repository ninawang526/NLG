from processData import *

# Fills message "name", "topic", and "arguments" fields from arguments given;
# calculates "tone" and "direction". Returns NLGMessage object.

class NLGMessage():

	def __init__(self, name, topic, type, arguments={}):
		assert isinstance(name, str)
		assert isinstance(topic, str)
		assert isinstance(type, str)
		assert isinstance(arguments, dict)

		self.name = name
		self.topic = topic
		self.arguments = arguments

		if type == "description":
			self.tone = self.analyzeDescriptionTone(topic, arguments)
		elif type == "comparison":
			self.tone = self.analyzeComparisonTone(topic, arguments)
			self.direction = self.analyzeDirection(arguments)
		else:
			self.tone = "neutral"


	# Decide if data for a description represents positive or negative info
	def analyzeDescriptionTone(self, topic, data):
		try:
			usage = data["usage"]
		except KeyError as error:
			raise Exception("Provide %s usage" %(topic))

		# THESE ARE ARBITRARY VALUES
		if topic == "filler":
			if usage > 1.3:
				return "negative"
			return "positive"
		elif topic == "pace":
			if usage > IDEAL_WPM_MAX or usage < IDEAL_WPM_MIN:
				return "negative"
			return "positive"
		elif topic == "energy":
			if usage > IDEAL_VOCAL_VARIATIONS_MAX or usage < IDEAL_VOCAL_VARIATIONS_MIN:
				return "negative"
			return "positive"
		else:
			raise Exception("Unrecognized topic: %s" %(topic))


	# Decide if data for a comparison represents positive or negative info
	def analyzeComparisonTone(self, topic, data):
		try:
			current = data["current"]
			average = data["average"]
		except KeyError as error:
			raise Exception("Provide %s current/average" %(topic))

		if topic == "filler":
			if current > average:
				return "negative"
			return "positive"

		elif topic == "pace":
			current_magnitude = magnitude(current, IDEAL_WPM_MIN, IDEAL_WPM_MAX)
			avg_magnitude = magnitude(average, IDEAL_WPM_MIN, IDEAL_WPM_MAX)
			if current_magnitude > avg_magnitude:
				return "negative"
			return "positive"

		elif topic == "energy":
			current_magnitude = magnitude(current, IDEAL_VOCAL_VARIATIONS_MIN, IDEAL_VOCAL_VARIATIONS_MAX)
			avg_magnitude = magnitude(average, IDEAL_VOCAL_VARIATIONS_MIN, IDEAL_VOCAL_VARIATIONS_MAX)
			if current_magnitude > avg_magnitude:
				return "negative"
			return "positive"
		else:
			raise Exception("Unrecognized topic: %s" %(topic))


	def analyzeDirection(self, data):
		try:
			current = data["current"]
			average = data["average"]
		except KeyError as error:
			raise Exception("Provide %s current/average" %(topic))

		if current < average:
			return "negative"
		return "positive"


if __name__ == '__main__':
	args = {"current": 3, "average": 5}
	FillerCompareMsg = NLGMessage('FillerCompareMsg','filler', 'comparison', args)
	print FillerCompareMsg.name
	print FillerCompareMsg.topic
	print FillerCompareMsg.tone
	print FillerCompareMsg.direction
