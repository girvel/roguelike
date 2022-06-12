"""Ecs is an entity-component-system framework that manages the game cycle.

In this interpretation entities are dynamic objects, components are entities'
fields, and systems are functions that take entities as an argument and
brute-force through all their possible combinations. Also there is a
metasystem, which is a system that launches other systems and is basically a
facade for all important interactions with the game.
"""

from .core import Entity, Metasystem

__all__ = [e.__name__ for e in [
  Entity, Metasystem,
]]
