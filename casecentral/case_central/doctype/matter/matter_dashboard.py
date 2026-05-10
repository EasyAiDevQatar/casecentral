def get_data(data=None):
	"""Do not force Sales Invoice as internal link by Matter name; links use field `matter` on SI."""
	return data or {}
