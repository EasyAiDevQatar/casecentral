def get_data(data=None):
	data = data or {}
	data.setdefault("internal_links", {})
	data["internal_links"]["Sales Invoice"] = "name"
	return data
