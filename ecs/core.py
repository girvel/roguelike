class Entity:
	"""Entity represents any object inside the game"""

	def __init__(self, **attributes):
		"""
		Args:
			**attributes: entity's future attributes in format
		"""
		for k, v in attributes.items():
			setattr(self, k, v)

	def __delitem__(self, key):
		return delattr(self, key)

	def __getitem__(self, item):
		return getattr(self, item)

	def __setitem__(self, item, value):
		return setattr(self, item, value)

	def __contains__(self, item):
		return hasattr(self, item)

	def __repr__(self):
		return f'Entity(name={getattr(self, "name", None)})'

	def __iter__(self):
		for attr_name in dir(self):
			if not attr_name.startswith('__') or not attr_name.endswith('__'):
				yield attr_name, getattr(self, attr_name)


def add(system, entity):
	assert all(hasattr(system, a) for a in (
		'process', 'ecs_targets', 'ecs_requirements'
	))

	for member_name, requirements in system.ecs_requirements.items():
		if all(p in entity for p in requirements):
			system.ecs_targets[member_name].add(entity)

def remove(system, entity):
	for targets in system.ecs_targets.values():
		targets.remove(entity)


def update(system):
	keys = list(system.ecs_targets.keys())

	def _update(members):
		i = len(members)
		if i == len(keys):
			system.process(**members)
			return

		if len(system.ecs_targets[keys[i]]) > 0:
			for target in system.ecs_targets[keys[i]]:
				members[keys[i]] = target
				_update(members)

			del members[keys[i]]

	return _update({})


def create_system(protosystem) -> Entity:
	"""Creates system from an annotated function

	Args:
		protosystem: function annotated in ECS style

	Returns:
		New entity with `process`, `ecs_targets` and `ecs_requirements` fields
	"""

	return Entity(
		process=protosystem,
		ecs_targets={
			member_name: set() for member_name in protosystem.__annotations__
		},
		ecs_requirements={
			member_name: set(annotation.split(', '))
			for member_name, annotation
			in protosystem.__annotations__.items()
		}
	)


class OwnedEntity(Entity):
	"""Represents an entity, that belongs to some metasystem"""
	def __init__(self, metasystem, /, **attributes):
		self.ecs_metasystem = metasystem
		super().__init__(**attributes)

	def __setattr__(self, key, value):
		super().__setattr__(key, value)
		self.ecs_metasystem.add(self, key)

	def __delattr__(self, item):
		super().__delattr__(item)
		self.ecs_metasystem.remove(self, item)


class Metasystem(Entity):
	ecs_targets = {
		'system': set(),
	}

	ecs_requirements = {
		'system': {'process'}
	}

	def process(self, system):
		update(system)

	def add(self, entity, new_attribute=None):
		if new_attribute is None:  # this should be moved to .create
			return OwnedEntity(self, **dict(entity))

		add(self, entity)
		for system in self.ecs_targets["system"]:
			if any(new_attribute in r for r in system.ecs_requirements.values()):
				add(system, entity)

		return entity

	def remove(self, entity, deleted_attribute=None):
		systems = self.ecs_targets["system"]

		if deleted_attribute is None:
			remove(self, entity)
			entity.ecs_metasystem = None
		else:
			systems = [
				s for s in systems
				if deleted_attribute in s.ecs_requirements
			]

		for system in systems:
			remove(system, entity)

		return entity

	def update(self):
		update(self)
