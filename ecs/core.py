class Entity:
	def __init__(self, **parameters):
		for k, v in parameters.items():
			setattr(self, k, v)
