"""
Tests taken from http://www.petrounias.org/articles/2014/09/16/pickling-python-collections-with-non-built-in-type-keys-and-cycles/

Also includes additional testing steps to assist with adding compatibility to jsonpickle
"""
from __future__ import print_function
from collections import OrderedDict
from unittest import TestCase
from jsonpickle import encode, decode


class World(object):

    def __init__(self):
        super(World, self).__init__()
        self.wizards = []

class Wizard(object):

    def __init__(self, world, name):
        self.name = name
        self.spells = OrderedDict()
        world.wizards.append(self)

    def __hash__(self):
        return hash(self.name) if hasattr(self, 'name') else id(self)

class Spell(object):

    def __init__(self, caster, target, name):
        super(Spell, self).__init__()
        self.caster = caster
        self.target = target
        self.name = name
        if not target in caster.spells:
            caster.spells[target] = []
        caster.spells[target].append(self)

    def __repr__(self):
        return """<Spell {caster} : {target} : {name} ...>""".format(
            caster = self.caster, target = self.target, name = self.name)


class MagicTestCase(TestCase):
    def test_without_pickling(self):
        world = World()
        wizard_merlin = Wizard(world, 'Merlin')
        wizard_morgana = Wizard(world, 'Morgana')
        spell_a = Spell(wizard_merlin, wizard_morgana, 'magic-missile')
        spell_b = Spell(wizard_merlin, wizard_merlin, 'stone-skin')
        spell_c = Spell(wizard_morgana, wizard_merlin, 'geas')

        self.assertEqual(wizard_merlin.spells[wizard_morgana][0], spell_a)
        self.assertEqual(wizard_merlin.spells[wizard_merlin][0], spell_b)
        self.assertEqual(wizard_morgana.spells[wizard_merlin][0], spell_c)

        # Merlin has cast Magic Missile on Morgana, and Stone Skin on himself
        self.assertEqual(wizard_merlin.spells[wizard_morgana][0].name,
            'magic-missile')
        self.assertEqual(wizard_merlin.spells[wizard_merlin][0].name,
            'stone-skin')

        # Morgana has cast Geas on Merlin
        self.assertEqual(wizard_morgana.spells[wizard_merlin][0].name, 'geas')

        # Merlin's first target was Morgana
        self.assertTrue(wizard_merlin.spells.keys()[0] in wizard_merlin.spells)
        self.assertEqual(wizard_merlin.spells.keys()[0], wizard_morgana)

        # Merlin's second target was himself
        self.assertTrue(wizard_merlin.spells.keys()[1] in wizard_merlin.spells)
        self.assertEqual(wizard_merlin.spells.keys()[1], wizard_merlin)

        # Morgana's first target was Merlin
        self.assertTrue(wizard_morgana.spells.keys()[0] in wizard_morgana.spells)
        self.assertEqual(wizard_morgana.spells.keys()[0], wizard_merlin)

        # Merlin's first spell cast with himself as target is in the dictionary,
        # first by looking up directly with Merlin's instance object...
        self.assertEqual(wizard_merlin,
            wizard_merlin.spells[wizard_merlin][0].target)

        # ...and then with the instance object directly from the dictionary keys
        self.assertEqual(wizard_merlin,
            wizard_merlin.spells[wizard_merlin.spells.keys()[1]][0].target)

        # Ensure Merlin's object is unique...
        self.assertEqual(id(wizard_merlin), id(wizard_merlin.spells.keys()[1]))

        # ...and consistently hashed
        self.assertEqual(hash(wizard_merlin),
            hash(wizard_merlin.spells.keys()[1]))


    def test_with_pickling(self):
        world = World()
        wizard_merlin = Wizard(world, 'Merlin')
        wizard_morgana = Wizard(world, 'Morgana')
        wizard_morgana_prime = Wizard(world, 'Morgana')

        self.assertEqual(wizard_morgana.__dict__, wizard_morgana_prime.__dict__)

        spell_a = Spell(wizard_merlin, wizard_morgana, 'magic-missile')
        spell_b = Spell(wizard_merlin, wizard_merlin, 'stone-skin')
        spell_c = Spell(wizard_morgana, wizard_merlin, 'geas')

        self.assertEqual(wizard_merlin.spells[wizard_morgana][0], spell_a)
        self.assertEqual(wizard_merlin.spells[wizard_merlin][0], spell_b)
        self.assertEqual(wizard_morgana.spells[wizard_merlin][0], spell_c)
        _world = encode(world)
        u_world = decode(_world)
        u_wizard_merlin = u_world.wizards[0]
        u_wizard_morgana = u_world.wizards[1]

        morgana_spells_encoded = encode(wizard_morgana.spells)
        print(morgana_spells_encoded)
        morgana_spells_decoded = decode(morgana_spells_encoded)

        self.assertEqual(morgana_spells_decoded, wizard_morgana.spells)

        morgana_encoded = encode(wizard_morgana)
        morgana_decoded = decode(morgana_encoded)

        self.assertEqual(wizard_morgana.__dict__, morgana_decoded.__dict__)

        # Merlin has cast Magic Missile on Morgana, and Stone Skin on himself
        self.assertEqual(u_wizard_merlin.spells[u_wizard_morgana][0].name,
            'magic-missile')
        self.assertEqual(u_wizard_merlin.spells[u_wizard_merlin][0].name,
            'stone-skin')

        # Morgana has cast Geas on Merlin
        self.assertEqual(u_wizard_morgana.spells[u_wizard_merlin][0].name,
            'geas')

        # Merlin's first target was Morgana
        self.assertTrue(
            u_wizard_merlin.spells.keys()[0] in u_wizard_merlin.spells)
        self.assertEqual(u_wizard_merlin.spells.keys()[0], u_wizard_morgana)

        # Merlin's second target was himself
        self.assertTrue(
            u_wizard_merlin.spells.keys()[1] in u_wizard_merlin.spells)
        self.assertEqual(u_wizard_merlin.spells.keys()[1], u_wizard_merlin)

        # Morgana's first target was Merlin
        self.assertTrue(
            u_wizard_morgana.spells.keys()[0] in u_wizard_morgana.spells)
        self.assertEqual(u_wizard_morgana.spells.keys()[0], u_wizard_merlin)

        # Merlin's first spell cast with himself as target is in the dictionary,
        # first by looking up directly with Merlin's instance object...
        self.assertEqual(u_wizard_merlin,
            u_wizard_merlin.spells[u_wizard_merlin][0].target)

        # ...and then with the instance object directly from the dictionary keys
        self.assertEqual(u_wizard_merlin,
            u_wizard_merlin.spells[u_wizard_merlin.spells.keys()[1]][0].target)

        # Ensure Merlin's object is unique...
        self.assertEqual(id(u_wizard_merlin),
            id(u_wizard_merlin.spells.keys()[1]))

        # ...and consistently hashed
        self.assertEqual(hash(u_wizard_merlin),
            hash(u_wizard_merlin.spells.keys()[1]))
