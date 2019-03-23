class TimelineCriteria:
	
	def __init__(self):
		self.maxTweets = 0
		
	def setUsername(self, username):
		self.username = username
		return self
		
	def setMaxTweets(self, maxTweets):
		self.maxTweets = maxTweets
		return self
