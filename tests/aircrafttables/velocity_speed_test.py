# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Unit tests for aircraft velocity speed tables and functions.
'''

##############################################################################
# Imports


import inspect
import unittest
import warnings

import numpy as np

from itertools import chain, imap

from flightdatautilities import aircrafttables as at, units as ut
from flightdatautilities import masked_array_testutils as ma_test
from flightdatautilities.aircrafttables.interfaces import VelocitySpeed

from flightdatautilities.aircrafttables import velocity_speed as vs


##############################################################################
# Test Configuration


def setUpModule():
    at.configure(package='flightdatautilities.aircrafttables')


##############################################################################
# Decorators


def _generate_tests(generator):
    '''
    A class decorator to generate test cases.
    '''

    ref = vs.VSPEED_MODEL_MAP, vs.VSPEED_SERIES_MAP, vs.VSPEED_FAMILY_MAP
    ref = imap(lambda d: d.itervalues(), ref)
    ref = set(c for c in chain.from_iterable(ref))

    def class_decorator(cls):
        '''
        Adds tests to ``cls`` generated by ``generator()``.
        '''
        for f, name, obj in generator():
            test = lambda self, obj=obj, ref=ref, f=f: f(self, obj, ref)
            test.__name__ = 'test__%s' % name
            setattr(cls, test.__name__, test)
        return cls

    return class_decorator


##############################################################################
# Helpers


def _velocity_speed_tables_integrity_test_generator():
    '''
    Generates test methods for velocity speed tables integrity tests.
    '''

    def test(self, cls, ref):
        # Check whether the class is referenced for lookup:
        self.assertIn(cls, ref, 'Velocity speed table not referenced for lookup!')

        # Check that the minimum speed option is valid:
        self.assertIsInstance(cls.minimum_speed, (type(None), float, int), 'Invalid minimum speed type.')
        if cls.minimum_speed is not None:
            # Require that minimum speed is at least 80 kt...
            self.assertGreaterEqual(cls.minimum_speed, 80, 'Invalid minimum speed defined.')

        # Check that the weight scale option is valid:
        self.assertIsInstance(cls.weight_scale, (float, int), 'Invalid weight scale type.')
        self.assertGreaterEqual(cls.weight_scale, 1, 'Invalid weight scale defined.')

        # Check that the weight unit option is valid:
        self.assertIsInstance(cls.weight_unit, (type(None), basestring), 'Invalid weight unit type.')
        self.assertIn(cls.weight_unit, (ut.KG, ut.LB, ut.TONNE, None), 'Invalid weight unit defined.')

        # Warn about weight scale and unit issues:
        if cls.weight_scale == 1000 and cls.weight_unit == ut.KG:
            warnings.warn('Should use units in tonnes, not thousands of '
                          'kilograms: %s' % cls.__name__)

        # Warn about weight scale and unit issues:
        if cls.source is None or not len(cls.source.strip()):
            warnings.warn('Should define source of velocity speed table '
                          'information: %s' % cls.__name__)

        # Ensure that we have some form of table to lookup in:
        self.assertTrue(len(cls.tables) or len(cls.fallback), 'No velocity speed tables defined.')
        self.assertLessEqual(set(cls.tables.keys()), set(('v2', 'vref', 'vapp', 'vmo', 'mmo')), 'Unknown velocity speed type in tables.')
        self.assertLessEqual(set(cls.fallback.keys()), set(('v2', 'vref', 'vapp')), 'Unknown velocity speed type in fallback tables.')

        # If we have standard tables, we must have a weight unit:
        if len(cls.tables.keys()) and set(cls.tables.keys()) & set(('v2', 'vref', 'vapp')):
            self.assertIsNot(cls.weight_unit, None, 'Must have a weight unit for standard tables.')

        # Check the integrity of values in the standard tables:
        for name, table in cls.tables.iteritems():

            if name in ('v2', 'vref', 'vapp'):
                self.assertTrue('weight' in table, 'Weight not in %s table.' % name)
                weights = list(table['weight'])
                self.assertEqual(weights, sorted(weights), 'Weights in %s table not ordered.' % name)
                self.assertTrue(all(w > 0 for w in weights), 'Weights in %s table cannot be negative.' % name)
                self.assertGreater(len(table), 1, 'No flap/conf rows in %s table.' % name)
                lengths = map(len, table.itervalues())
                self.assertEqual(len(set(lengths)), 1, 'Row lengths mismatch in %s table.' % name)
                t = all(isinstance(k, basestring) for k in table.iterkeys())
                self.assertTrue(t, 'Expected flap/conf string keys in %s table.' % name)
                t = all(isinstance(v, tuple) for v in table.itervalues())
                self.assertTrue(t, 'Expected tuple values in %s table.' % name)
                t = all(isinstance(v, (type(None), int, float)) for v in chain.from_iterable(table.itervalues()))
                self.assertTrue(t, 'Invalid velocity speed types in %s table.' % name)
                t = all((v is None or 80 <= v < 500) for v in chain.from_iterable(b for a, b in table.iteritems() if not a == 'weight'))
                self.assertTrue(t, 'Invalid velocity speed values in %s table.' % name)
                # Require that value is in a sensible range...
                t = all((v is None or 80 <= v < 500) for v in chain.from_iterable(b for a, b in table.iteritems() if not a == 'weight'))
                self.assertTrue(t, 'Invalid velocity speed values in %s table.' % name)
                ##### Require that speed values increase with weight...
                ####from itertools import izip, tee
                ####for k, v in table.iteritems():
                ####    if k == 'weight':
                ####        continue
                ####    a, b = tee(z for z in v if z is not None)
                ####    next(b, None)
                ####    t = all(a <= b for a, b in izip(a, b))
                ####    self.assertTrue(t, 'Invalid velocity speed values in %s table - shouldn\'t decrease.' % name)
                continue

            if name in ('vmo', 'mmo'):
                if isinstance(table, dict):
                    self.assertTrue('altitude' in table, 'Altitude not in %s table.' % name)
                    self.assertTrue('speed' in table, 'Speed not in %s table.' % name)
                    altitudes = list(table['altitude'])
                    self.assertEqual(altitudes, sorted(altitudes), 'Altitudes in %s table not ordered.' % name)
                    self.assertTrue(all(a >= 0 for a in altitudes), 'Altitudes in %s table cannot be negative.' % name)
                    self.assertEqual(len(table), 2, 'Unexpected entries in %s table.' % name)
                    lengths = map(len, table.itervalues())
                    self.assertEqual(len(set(lengths)), 1, 'Row lengths mismatch in %s table.' % name)
                    t = all(isinstance(v, tuple) for v in table.itervalues())
                    self.assertTrue(t, 'Expected tuple values in %s table.' % name)
                    values = table['speed']
                else:
                    self.assertIsInstance(table, (type(None), int, float))
                    values = [table]
                if name == 'vmo':
                    # Require that value is in a sensible range...
                    t = all((v is None or 80 <= v < 500) for v in values)
                    self.assertTrue(t, 'Invalid velocity speed values in %s table.' % name)
                if name == 'mmo':
                    # Probably sensible until we monitor supersonic aircraft!
                    t = all((v is None or 0.000 <= v < 1.000) for v in values)
                    self.assertTrue(t, 'Invalid velocity speed values in %s table.' % name)
                continue

        # Check the integrity of values in the fallback tables:
        for name, table in cls.fallback.iteritems():

            if name in ('v2', 'vref', 'vapp'):
                self.assertFalse('weight' in table, 'Weight must not be in %s fallback table.' % name)
                self.assertGreater(len(table), 0, 'No flap/conf rows in %s fallback table.' % name)
                t = all(isinstance(k, basestring) for k in table.iterkeys())
                self.assertTrue(t, 'Expected flap/conf string keys in %s fallback table.' % name)
                t = all(isinstance(v, (type(None), int, float)) for v in table.itervalues())
                self.assertTrue(t, 'Invalid velocity speed types in %s fallback table.' % name)
                # Require that value is in a sensible range...
                t = all((v is None or 80 <= v < 500) for v in table.itervalues())
                self.assertTrue(t, 'Invalid velocity speed values in %s table.' % name)

    f = lambda x: inspect.isclass(x) \
        and issubclass(x, VelocitySpeed) \
        and not x == VelocitySpeed

    for name, cls in inspect.getmembers(vs, f):
        yield test, 'velocity_speed_table__%s' % name.lower(), cls


##############################################################################
# Test Cases


class TestVelocitySpeed(unittest.TestCase):

    def setUp(self):
        self.vs = VelocitySpeed()
        self.vs.weight_unit = ut.TONNE
        self.vs.tables = {
            'v2': {
                'weight': (100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                     '5': (127, 134, 139, 145, 151, 156, 161, 166, 171, 176),
                    '15': (122, 128, 134, 139, 144, 149, 154, 159, 164, 168),
                    '20': (118, 124, 129, 134, 140, 144, 149, 154, 159, 164),
            },
            'vref': {
                'weight': (100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                     '5': (114, 121, 128, 134, 141, 147, 153, 158, 164, 169),
                    '15': (109, 116, 122, 129, 131, 135, 146, 151, 157, 162),
                    '20': (105, 111, 118, 124, 130, 135, 141, 147, 152, 158),
            },
            'vapp': {
                'weight': (100, 110, 120, 130, 140, 150, 160, 170, 180, 190),
                     '5': (114, 121, 128, 134, 141, 147, 153, 158, 164, 169),
                    '15': (109, 116, 122, 129, 131, 135, 146, 151, 157, 162),
                    '20': (105, 111, 118, 124, 130, 135, 141, 147, 152, 158),
            },
            'vmo': {
                'altitude': (  0, 12000, 29000, 41000),
                   'speed': (335,   335,   310,   310),
            },
            'mmo': 0.800,
        }
        self.vs.fallback = {
            'v2': {'5': 122, '15': 117, '20': 113},
            'vref': {'5': 109, '15': 104, '20': 100},
            'vapp': {'5': 109, '15': 104, '20': 100},
        }

    def test__v2(self):
        # Test where weight argument is a single value:
        self.assertEquals(self.vs.v2('5', 165000), 164)
        self.assertEquals(self.vs.v2('15', 120000), 134)
        self.assertEquals(self.vs.v2('20', 145000), 142)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(120, 130, 2) * 1000
        weight[2] = np.ma.masked
        v2_05 = np.ma.array((139, 140, 141, 143, 144))
        v2_15 = np.ma.array((134, 135, 136, 137, 138))
        v2_20 = np.ma.array((129, 130, 131, 132, 133))
        v2_05[2] = np.ma.masked
        v2_15[2] = np.ma.masked
        v2_20[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.v2('5', weight), v2_05)
        ma_test.assert_masked_array_equal(self.vs.v2('15', weight), v2_15)
        ma_test.assert_masked_array_equal(self.vs.v2('20', weight), v2_20)

    def test__v2__minimum_speed(self):
        self.vs.minimum_speed = 125
        # Test where weight argument is a single value:
        self.assertEquals(self.vs.v2('15', 100500), 125)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 110, 2) * 1000
        weight[2] = np.ma.masked
        v2_15 = np.ma.array((125, 125, 125, 126, 127))
        v2_15[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.v2('15', weight), v2_15)

    def test__v2__out_of_range(self):
        # Test where weight argument is a single value:
        self.assertIs(self.vs.v2('20', 95000), np.ma.masked)
        self.assertIs(self.vs.v2('20', 99999), np.ma.masked)
        self.assertIs(self.vs.v2('20', 190001), np.ma.masked)
        self.assertIs(self.vs.v2('20', 195000), np.ma.masked)
        self.assertIsNot(self.vs.v2('20', 100000), np.ma.masked)
        self.assertIsNot(self.vs.v2('20', 190000), np.ma.masked)
        self.assertEquals(self.vs.v2('20', 100000), 118)
        self.assertEquals(self.vs.v2('20', 190000), 164)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(95, 200, 20) * 1000
        v2_15 = np.ma.array((0, 131, 142, 152, 162, 0))
        v2_15[0] = np.ma.masked
        v2_15[5] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.v2('15', weight), v2_15)

    def test__v2__fallback__weight_not_recorded(self):
        self.assertTrue('20' in self.vs.tables['v2'])
        self.assertTrue('20' in self.vs.fallback['v2'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.v2('20'), 113)
        self.assertIsNot(self.vs.v2('20'), np.ma.masked)
        # Test where weight argument is a masked array:
        # Note: Pass in masked zeroed array of desired shape to get array.
        weight = np.ma.repeat(0, 6)
        weight.mask = True
        v2_20 = np.ma.repeat(113, 6)
        v2_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.v2('20', weight), v2_20)

    def test__v2__fallback__weight_fully_masked(self):
        self.assertTrue('20' in self.vs.tables['v2'])
        self.assertTrue('20' in self.vs.fallback['v2'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.v2('20', np.ma.masked), 113)
        self.assertIsNot(self.vs.v2('20', np.ma.masked), np.ma.masked)
        # Test where weight argument is a masked array:
        # Note: Array with fallback using weight array shape if fully masked.
        weight = np.ma.repeat(120, 6) * 1000
        weight.mask = True
        v2_20 = np.ma.repeat(113, 6)
        v2_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.v2('20', weight), v2_20)

    def test__v2__fallback__detent_in_fallback_only(self):
        del self.vs.tables['v2']['20']
        self.assertFalse('20' in self.vs.tables['v2'])
        self.assertTrue('20' in self.vs.fallback['v2'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.v2('20'), 113)
        self.assertIsNot(self.vs.v2('20'), np.ma.masked)
        self.assertEqual(self.vs.v2('20', 100000), 113)
        self.assertIsNot(self.vs.v2('20', 100000), np.ma.masked)
        self.assertEqual(self.vs.v2('20', 120000), 113)
        self.assertIsNot(self.vs.v2('20', 120000), np.ma.masked)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 200, 10) * 1000
        weight[5] = np.ma.masked
        v2_20 = np.ma.repeat(113, weight.size)
        v2_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.v2('20', weight), v2_20)

    def test__v2__fallback__detent_not_available(self):
        del self.vs.tables['v2']['20']
        del self.vs.fallback['v2']['20']
        self.assertFalse('20' in self.vs.tables['v2'])
        self.assertFalse('20' in self.vs.fallback['v2'])
        # Test where weight argument is a single value:
        self.assertIs(self.vs.v2('20'), np.ma.masked)
        self.assertIs(self.vs.v2('20', 100000), np.ma.masked)
        self.assertIs(self.vs.v2('20', 120000), np.ma.masked)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 200, 10) * 1000
        weight[5] = np.ma.masked
        v2_20 = np.ma.repeat(0, weight.size)
        v2_20.mask = True
        ma_test.assert_masked_array_equal(self.vs.v2('20', weight), v2_20)

    def test__v2__fallback__no_weight_based_table(self):
        del self.vs.tables['v2']
        self.assertFalse('v2' in self.vs.tables)
        self.assertTrue('20' in self.vs.fallback['v2'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.v2('20'), 113)
        self.assertIsNot(self.vs.v2('20'), np.ma.masked)
        self.assertEqual(self.vs.v2('20', 100000), 113)
        self.assertIsNot(self.vs.v2('20', 100000), np.ma.masked)
        self.assertEqual(self.vs.v2('20', 120000), 113)
        self.assertIsNot(self.vs.v2('20', 120000), np.ma.masked)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 200, 10) * 1000
        weight[5] = np.ma.masked
        v2_20 = np.ma.repeat(113, weight.size)
        v2_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.v2('20', weight), v2_20)

    def test__v2__weight_unit__invalid(self):
        invalid = set(ut.available()) - set((None, ut.KG, ut.LB, ut.TONNE))
        for unit in invalid:
            self.vs.weight_unit = unit
            self.assertRaises(KeyError, self.vs.v2, '15', 120000)

    def test__v2__weight_scale__1000_lb(self):
        self.vs.weight_scale = 1000
        self.vs.weight_unit = ut.LB
        # Test where weight argument is a single value:
        self.assertIs(self.vs.v2('20', 43091), np.ma.masked)
        self.assertIs(self.vs.v2('20', 88451), np.ma.masked)
        self.assertIsNot(self.vs.v2('20', 54431), np.ma.masked)
        self.assertAlmostEqual(self.vs.v2('20', 54431), 129, places=3)
        # Test where weight argument is a masked array:
        weight = np.ma.array((43091, 52163, 61239, 70307, 79379, 88451))
        v2_15 = np.ma.array((0, 131, 142, 152, 162, 0))
        v2_15[0] = np.ma.masked
        v2_15[5] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.v2('15', weight), v2_15)

    def test__vref(self):
        # Test where weight argument is a single value:
        self.assertEquals(self.vs.vref('5', 120000), 128)
        self.assertEquals(self.vs.vref('15', 120000), 122)
        self.assertEquals(self.vs.vref('20', 145000), 132)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(120, 130, 2) * 1000
        weight[2] = np.ma.masked
        vref_05 = np.ma.array((128, 129, 130, 132, 133))
        vref_15 = np.ma.array((122, 123, 125, 126, 128))
        vref_20 = np.ma.array((118, 119, 120, 122, 123))
        vref_05[2] = np.ma.masked
        vref_15[2] = np.ma.masked
        vref_20[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vref('5', weight), vref_05)
        ma_test.assert_masked_array_equal(self.vs.vref('15', weight), vref_15)
        ma_test.assert_masked_array_equal(self.vs.vref('20', weight), vref_20)

    def test__vref__minimum_speed(self):
        self.vs.minimum_speed = 112
        # Test where weight argument is a single value:
        self.assertEquals(self.vs.vref('15', 100500), 112)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 110, 2) * 1000
        weight[2] = np.ma.masked
        vref_15 = np.ma.array((112, 112, 112, 113, 115))
        vref_15[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vref('15', weight), vref_15)

    def test__vref__out_of_range(self):
        # Test where weight argument is a single value:
        self.assertIs(self.vs.vref('20', 95000), np.ma.masked)
        self.assertIs(self.vs.vref('20', 99999), np.ma.masked)
        self.assertIs(self.vs.vref('20', 190001), np.ma.masked)
        self.assertIs(self.vs.vref('20', 195000), np.ma.masked)
        self.assertIsNot(self.vs.vref('20', 100000), np.ma.masked)
        self.assertIsNot(self.vs.vref('20', 190000), np.ma.masked)
        self.assertEquals(self.vs.vref('20', 100000), 105)
        self.assertEquals(self.vs.vref('20', 190000), 158)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(95, 200, 20) * 1000
        vref_15 = np.ma.array((0, 119, 130, 140, 154, 0))
        vref_15[0] = np.ma.masked
        vref_15[5] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vref('15', weight), vref_15)

    def test__vref__fallback__weight_not_recorded(self):
        self.assertTrue('20' in self.vs.tables['vref'])
        self.assertTrue('20' in self.vs.fallback['vref'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.vref('20'), 100)
        self.assertIsNot(self.vs.vref('20'), np.ma.masked)
        # Test where weight argument is a masked array:
        # Note: Pass in masked zeroed array of desired shape to get array.
        weight = np.ma.repeat(0, 6)
        weight.mask = True
        vref_20 = np.ma.repeat(100, 6)
        vref_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.vref('20', weight), vref_20)

    def test__vref__fallback__weight_fully_masked(self):
        self.assertTrue('20' in self.vs.tables['vref'])
        self.assertTrue('20' in self.vs.fallback['vref'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.vref('20', np.ma.masked), 100)
        self.assertIsNot(self.vs.vref('20', np.ma.masked), np.ma.masked)
        # Test where weight argument is a masked array:
        # Note: Array with fallback using weight array shape if fully masked.
        weight = np.ma.repeat(120, 6) * 1000
        weight.mask = True
        vref_20 = np.ma.repeat(100, 6)
        vref_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.vref('20', weight), vref_20)

    def test__vref__fallback__detent_in_fallback_only(self):
        del self.vs.tables['vref']['20']
        self.assertFalse('20' in self.vs.tables['vref'])
        self.assertTrue('20' in self.vs.fallback['vref'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.vref('20'), 100)
        self.assertIsNot(self.vs.vref('20'), np.ma.masked)
        self.assertEqual(self.vs.vref('20', 100000), 100)
        self.assertIsNot(self.vs.vref('20', 100000), np.ma.masked)
        self.assertEqual(self.vs.vref('20', 120000), 100)
        self.assertIsNot(self.vs.vref('20', 120000), np.ma.masked)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 200, 10) * 1000
        weight[5] = np.ma.masked
        vref_20 = np.ma.repeat(100, weight.size)
        vref_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.vref('20', weight), vref_20)

    def test__vref__fallback__detent_not_available(self):
        del self.vs.tables['vref']['20']
        del self.vs.fallback['vref']['20']
        self.assertFalse('20' in self.vs.tables['vref'])
        self.assertFalse('20' in self.vs.fallback['vref'])
        # Test where weight argument is a single value:
        self.assertIs(self.vs.vref('20'), np.ma.masked)
        self.assertIs(self.vs.vref('20', 100000), np.ma.masked)
        self.assertIs(self.vs.vref('20', 120000), np.ma.masked)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 200, 10) * 1000
        weight[5] = np.ma.masked
        vref_20 = np.ma.repeat(0, weight.size)
        vref_20.mask = True
        ma_test.assert_masked_array_equal(self.vs.vref('20', weight), vref_20)

    def test__vref__fallback__no_weight_based_table(self):
        del self.vs.tables['vref']
        self.assertFalse('vref' in self.vs.tables)
        self.assertTrue('20' in self.vs.fallback['vref'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.vref('20'), 100)
        self.assertIsNot(self.vs.vref('20'), np.ma.masked)
        self.assertEqual(self.vs.vref('20', 100000), 100)
        self.assertIsNot(self.vs.vref('20', 100000), np.ma.masked)
        self.assertEqual(self.vs.vref('20', 120000), 100)
        self.assertIsNot(self.vs.vref('20', 120000), np.ma.masked)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 200, 10) * 1000
        weight[5] = np.ma.masked
        vref_20 = np.ma.repeat(100, weight.size)
        vref_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.vref('20', weight), vref_20)

    def test__vref__weight_unit__invalid(self):
        invalid = set(ut.available()) - set((None, ut.KG, ut.LB, ut.TONNE))
        for unit in invalid:
            self.vs.weight_unit = unit
            self.assertRaises(KeyError, self.vs.vref, '15', 120000)

    def test__vref__weight_scale__1000_lb(self):
        self.vs.weight_scale = 1000
        self.vs.weight_unit = ut.LB
        # Test where weight argument is a single value:
        self.assertIs(self.vs.vref('20', 43091), np.ma.masked)
        self.assertIs(self.vs.vref('20', 88451), np.ma.masked)
        self.assertIsNot(self.vs.vref('20', 54431), np.ma.masked)
        self.assertAlmostEqual(self.vs.vref('20', 54431), 118, places=3)
        # Test where weight argument is a masked array:
        weight = np.ma.array((43091, 52163, 61239, 70307, 79379, 88451))
        vref_15 = np.ma.array((0, 119, 130, 141, 154, 0))
        vref_15[0] = np.ma.masked
        vref_15[5] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vref('15', weight), vref_15)

    def test__vapp(self):
        # Test where weight argument is a single value:
        self.assertEquals(self.vs.vapp('5', 120000), 128)
        self.assertEquals(self.vs.vapp('15', 120000), 122)
        self.assertEquals(self.vs.vapp('20', 145000), 132)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(120, 130, 2) * 1000
        weight[2] = np.ma.masked
        vapp_05 = np.ma.array((128, 129, 130, 132, 133))
        vapp_15 = np.ma.array((122, 123, 125, 126, 128))
        vapp_20 = np.ma.array((118, 119, 120, 122, 123))
        vapp_05[2] = np.ma.masked
        vapp_15[2] = np.ma.masked
        vapp_20[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vapp('5', weight), vapp_05)
        ma_test.assert_masked_array_equal(self.vs.vapp('15', weight), vapp_15)
        ma_test.assert_masked_array_equal(self.vs.vapp('20', weight), vapp_20)

    def test__vapp__minimum_speed(self):
        self.vs.minimum_speed = 112
        # Test where weight argument is a single value:
        self.assertEquals(self.vs.vapp('15', 100500), 112)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 110, 2) * 1000
        weight[2] = np.ma.masked
        vapp_15 = np.ma.array((112, 112, 112, 113, 115))
        vapp_15[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vapp('15', weight), vapp_15)

    def test__vapp__out_of_range(self):
        # Test where weight argument is a single value:
        self.assertIs(self.vs.vapp('20', 95000), np.ma.masked)
        self.assertIs(self.vs.vapp('20', 99999), np.ma.masked)
        self.assertIs(self.vs.vapp('20', 190001), np.ma.masked)
        self.assertIs(self.vs.vapp('20', 195000), np.ma.masked)
        self.assertIsNot(self.vs.vapp('20', 100000), np.ma.masked)
        self.assertIsNot(self.vs.vapp('20', 190000), np.ma.masked)
        self.assertEquals(self.vs.vapp('20', 100000), 105)
        self.assertEquals(self.vs.vapp('20', 190000), 158)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(95, 200, 20) * 1000
        vapp_15 = np.ma.array((0, 119, 130, 140, 154, 0))
        vapp_15[0] = np.ma.masked
        vapp_15[5] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vapp('15', weight), vapp_15)

    def test__vapp__fallback__weight_not_recorded(self):
        self.assertTrue('20' in self.vs.tables['vapp'])
        self.assertTrue('20' in self.vs.fallback['vapp'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.vapp('20'), 100)
        self.assertIsNot(self.vs.vapp('20'), np.ma.masked)
        # Test where weight argument is a masked array:
        # Note: Pass in masked zeroed array of desired shape to get array.
        weight = np.ma.repeat(0, 6)
        weight.mask = True
        vapp_20 = np.ma.repeat(100, 6)
        vapp_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.vapp('20', weight), vapp_20)

    def test__vapp__fallback__weight_fully_masked(self):
        self.assertTrue('20' in self.vs.tables['vapp'])
        self.assertTrue('20' in self.vs.fallback['vapp'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.vapp('20', np.ma.masked), 100)
        self.assertIsNot(self.vs.vapp('20', np.ma.masked), np.ma.masked)
        # Test where weight argument is a masked array:
        # Note: Array with fallback using weight array shape if fully masked.
        weight = np.ma.repeat(120, 6) * 1000
        weight.mask = True
        vapp_20 = np.ma.repeat(100, 6)
        vapp_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.vapp('20', weight), vapp_20)

    def test__vapp__fallback__detent_in_fallback_only(self):
        del self.vs.tables['vapp']['20']
        self.assertFalse('20' in self.vs.tables['vapp'])
        self.assertTrue('20' in self.vs.fallback['vapp'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.vapp('20'), 100)
        self.assertIsNot(self.vs.vapp('20'), np.ma.masked)
        self.assertEqual(self.vs.vapp('20', 100000), 100)
        self.assertIsNot(self.vs.vapp('20', 100000), np.ma.masked)
        self.assertEqual(self.vs.vapp('20', 120000), 100)
        self.assertIsNot(self.vs.vapp('20', 120000), np.ma.masked)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 200, 10) * 1000
        weight[5] = np.ma.masked
        vapp_20 = np.ma.repeat(100, weight.size)
        vapp_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.vapp('20', weight), vapp_20)

    def test__vapp__fallback__detent_not_available(self):
        del self.vs.tables['vapp']['20']
        del self.vs.fallback['vapp']['20']
        self.assertFalse('20' in self.vs.tables['vapp'])
        self.assertFalse('20' in self.vs.fallback['vapp'])
        # Test where weight argument is a single value:
        self.assertIs(self.vs.vapp('20'), np.ma.masked)
        self.assertIs(self.vs.vapp('20', 100000), np.ma.masked)
        self.assertIs(self.vs.vapp('20', 120000), np.ma.masked)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 200, 10) * 1000
        weight[5] = np.ma.masked
        vapp_20 = np.ma.repeat(0, weight.size)
        vapp_20.mask = True
        ma_test.assert_masked_array_equal(self.vs.vapp('20', weight), vapp_20)

    def test__vapp__fallback__no_weight_based_table(self):
        del self.vs.tables['vapp']
        self.assertFalse('vapp' in self.vs.tables)
        self.assertTrue('20' in self.vs.fallback['vapp'])
        # Test where weight argument is a single value:
        self.assertEqual(self.vs.vapp('20'), 100)
        self.assertIsNot(self.vs.vapp('20'), np.ma.masked)
        self.assertEqual(self.vs.vapp('20', 100000), 100)
        self.assertIsNot(self.vs.vapp('20', 100000), np.ma.masked)
        self.assertEqual(self.vs.vapp('20', 120000), 100)
        self.assertIsNot(self.vs.vapp('20', 120000), np.ma.masked)
        # Test where weight argument is a masked array:
        weight = np.ma.arange(100, 200, 10) * 1000
        weight[5] = np.ma.masked
        vapp_20 = np.ma.repeat(100, weight.size)
        vapp_20.mask = False
        ma_test.assert_masked_array_equal(self.vs.vapp('20', weight), vapp_20)

    def test__vapp__weight_unit__invalid(self):
        invalid = set(ut.available()) - set((None, ut.KG, ut.LB, ut.TONNE))
        for unit in invalid:
            self.vs.weight_unit = unit
            self.assertRaises(KeyError, self.vs.vapp, '15', 120000)

    def test__vapp__weight_scale__1000_lb(self):
        self.vs.weight_scale = 1000
        self.vs.weight_unit = ut.LB
        # Test where weight argument is a single value:
        self.assertIs(self.vs.vapp('20', 43091), np.ma.masked)
        self.assertIs(self.vs.vapp('20', 88451), np.ma.masked)
        self.assertIsNot(self.vs.vapp('20', 54431), np.ma.masked)
        self.assertAlmostEqual(self.vs.vapp('20', 54431), 118, places=3)
        # Test where weight argument is a masked array:
        weight = np.ma.array((43091, 52163, 61239, 70307, 79379, 88451))
        vapp_15 = np.ma.array((0, 119, 130, 141, 154, 0))
        vapp_15[0] = np.ma.masked
        vapp_15[5] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vapp('15', weight), vapp_15)

    def test__vmo__none(self):
        self.vs.tables['vmo'] = None
        # Test where altitude argument is a single value:
        self.assertIs(self.vs.vmo(00000), np.ma.masked)
        self.assertIs(self.vs.vmo(10000), np.ma.masked)
        self.assertIs(self.vs.vmo(20000), np.ma.masked)
        self.assertIs(self.vs.vmo(30000), np.ma.masked)
        self.assertIs(self.vs.vmo(40000), np.ma.masked)
        # Test where altitude argument is a masked array:
        altitude = np.ma.arange(0, 50, 10) * 1000
        vmo = np.ma.repeat(0, 5)
        vmo.mask = True
        ma_test.assert_masked_array_equal(self.vs.vmo(altitude), vmo)

    def test__vmo__fixed(self):
        self.vs.tables['vmo'] = 350
        # Test where altitude argument is a single value:
        self.assertEqual(self.vs.vmo(00000), 350)
        self.assertEqual(self.vs.vmo(10000), 350)
        self.assertEqual(self.vs.vmo(20000), 350)
        self.assertEqual(self.vs.vmo(30000), 350)
        self.assertEqual(self.vs.vmo(40000), 350)
        # Test where altitude argument is a masked array:
        altitude = np.ma.arange(0, 50, 10) * 1000
        altitude[2] = np.ma.masked
        vmo = np.ma.repeat(350, 5)
        vmo.mask = False
        ma_test.assert_masked_array_equal(self.vs.vmo(altitude), vmo)

    def test__vmo__stepped(self):
        self.vs.tables['vmo'] = {
            'altitude': (  0, 20000, 20000, 40000),
               'speed': (350,   350,   300,   300),
        }
        # Test where altitude argument is a single value:
        self.assertEqual(self.vs.vmo(00000), 350)
        self.assertEqual(self.vs.vmo(19999), 350)
        self.assertEqual(self.vs.vmo(20000), 300)
        self.assertEqual(self.vs.vmo(20001), 300)
        self.assertEqual(self.vs.vmo(40000), 300)
        # Test where altitude argument is a masked array:
        altitude = np.ma.arange(0, 50, 10) * 1000
        altitude[2] = np.ma.masked
        vmo = np.ma.array([350] * 2 + [300] * 3)
        vmo[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vmo(altitude), vmo)

    def test__vmo__interpolated(self):
        self.vs.tables['vmo'] = {
            'altitude': (  0, 20000, 40000),
               'speed': (350,   330,   310),
        }
        # Test where altitude argument is a single value:
        self.assertEqual(self.vs.vmo(00000), 350)
        self.assertEqual(self.vs.vmo(10000), 340)
        self.assertEqual(self.vs.vmo(20000), 330)
        self.assertEqual(self.vs.vmo(30000), 320)
        self.assertEqual(self.vs.vmo(40000), 310)
        # Test where altitude argument is a masked array:
        altitude = np.ma.arange(0, 50, 10) * 1000
        altitude[2] = np.ma.masked
        vmo = np.ma.arange(350, 300, -10)
        vmo[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.vmo(altitude), vmo)

    def test__mmo__none(self):
        self.vs.tables['mmo'] = None
        # Test where altitude argument is a single value:
        self.assertIs(self.vs.mmo(00000), np.ma.masked)
        self.assertIs(self.vs.mmo(10000), np.ma.masked)
        self.assertIs(self.vs.mmo(20000), np.ma.masked)
        self.assertIs(self.vs.mmo(30000), np.ma.masked)
        self.assertIs(self.vs.mmo(40000), np.ma.masked)
        # Test where altitude argument is a masked array:
        altitude = np.ma.arange(0, 50, 10) * 1000
        mmo = np.ma.repeat(0, 5)
        mmo.mask = True
        ma_test.assert_masked_array_equal(self.vs.mmo(altitude), mmo)

    def test__mmo__fixed(self):
        self.vs.tables['mmo'] = 0.850
        # Test where altitude argument is a single value:
        self.assertEqual(self.vs.mmo(00000), 0.850)
        self.assertEqual(self.vs.mmo(10000), 0.850)
        self.assertEqual(self.vs.mmo(20000), 0.850)
        self.assertEqual(self.vs.mmo(30000), 0.850)
        self.assertEqual(self.vs.mmo(40000), 0.850)
        # Test where altitude argument is a masked array:
        altitude = np.ma.arange(0, 50, 10) * 1000
        altitude[2] = np.ma.masked
        mmo = np.ma.repeat(0.850, 5)
        mmo.mask = False
        ma_test.assert_masked_array_equal(self.vs.mmo(altitude), mmo)

    def test__mmo__stepped(self):
        self.vs.tables['mmo'] = {
            'altitude': (    0, 20000, 20000, 40000),
               'speed': (0.850, 0.850, 0.800, 0.800),
        }
        # Test where altitude argument is a single value:
        self.assertEqual(self.vs.mmo(00000), 0.850)
        self.assertEqual(self.vs.mmo(19999), 0.850)
        self.assertEqual(self.vs.mmo(20000), 0.800)
        self.assertEqual(self.vs.mmo(20001), 0.800)
        self.assertEqual(self.vs.mmo(40000), 0.800)
        # Test where altitude argument is a masked array:
        altitude = np.ma.arange(0, 50, 10) * 1000
        altitude[2] = np.ma.masked
        mmo = np.ma.array([0.850] * 2 + [0.800] * 3)
        mmo[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.mmo(altitude), mmo)

    def test__mmo__interpolated(self):
        self.vs.tables['mmo'] = {
            'altitude': (    0, 20000, 40000),
               'speed': (0.860, 0.830, 0.800),
        }
        # Test where altitude argument is a single value:
        self.assertEqual(self.vs.mmo(00000), 0.860)
        self.assertEqual(self.vs.mmo(10000), 0.845)
        self.assertEqual(self.vs.mmo(20000), 0.830)
        self.assertEqual(self.vs.mmo(30000), 0.815)
        self.assertEqual(self.vs.mmo(40000), 0.800)
        # Test where altitude argument is a masked array:
        altitude = np.ma.arange(0, 50, 10) * 1000
        altitude[2] = np.ma.masked
        mmo = np.ma.arange(860, 785, -15) / 1000.0
        mmo[2] = np.ma.masked
        ma_test.assert_masked_array_equal(self.vs.mmo(altitude), mmo)


@_generate_tests(_velocity_speed_tables_integrity_test_generator)
class TestVelocitySpeedTablesIntegrity(unittest.TestCase):
    pass
