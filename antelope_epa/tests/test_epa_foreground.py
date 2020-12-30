import unittest
import os
from antelope_foreground import ForegroundCatalog

from .config import TEST_FG_NAME, ANNOTATED_XLSX_REL_PATH

from .. import create_annotated_foreground
from ..exceptions import MissingEpaForegroundEnvVar
from ..epa_psm_antelope import EpaF18Foreground


class EpaFgTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = ForegroundCatalog.make_tester()
        try:
            cls.folder = os.path.join(os.getenv('EPA_FOREGROUND'), 'LandingGear')
        except TypeError:
            raise MissingEpaForegroundEnvVar('export EPA_FOREGROUND')

    def test_0_fg(self):
        fg = create_annotated_foreground(self.cat, TEST_FG_NAME, ANNOTATED_XLSX_REL_PATH)
        self.assertEqual(fg.count('flow'), 810)

    def test_1_properties(self):
        fg = self.cat.foreground(TEST_FG_NAME)
        f = fg.get('3M1169C3D6A')
        self.assertTrue(f.has_property('material'))
        self.assertEqual(f['material'], 'Nickel')

    def test_2_models(self):
        fg = self.cat.foreground(TEST_FG_NAME)
        efg = EpaF18Foreground(fg, self.folder)
        self.assertEqual(len(list(efg.valid_sheets)), 8)
        for sheet in efg.valid_sheets:
            efg.create_assembly(sheet)
        self.assertEqual(len([k for k in efg.models]), 8)
        self.assertEqual(fg.count('fragment'), 1528)

    def test_3_duplicates(self):
        fg = self.cat.foreground(TEST_FG_NAME)
        efg = EpaF18Foreground(fg, self.folder)
        self.assertEqual(len(list(efg.duplicate_subassemblies())), 19)
        for dup in efg.duplicate_subassemblies():
            sdup = sorted(dup, key=lambda x: not x.is_reference)  # make sure
            efg.reduce_duplicates(*sdup)

        self.assertEqual(len(list(efg.models)), 27)
        self.assertEqual(fg.count('fragment'), 1402)
        self.assertEqual(len(list(efg.duplicate_subassemblies())), 0)





