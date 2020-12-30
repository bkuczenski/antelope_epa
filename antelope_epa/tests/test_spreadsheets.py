import unittest
import os

from ..exceptions import MissingEpaForegroundEnvVar
from ..validation import validate_folder

from antelope_core import LcCatalog


class SpreadsheetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = os.getenv('EPA_FOREGROUND')
        if cls.folder is None:
            print('Target is equivalent to https://github.com/USEPA/LCAproductsystemassembly_resources/tree/master/data')
            raise MissingEpaForegroundEnvVar('please export EPA_FOREGROUND to point to data folder',
                                             'clone https://github.com/USEPA/LCAproductsystemassembly_resources',
                                             'export EPA_FOREGROUND=LCAproductsystemassembly_resources/data')

    def _tgt(self, arg):
        return os.path.join(self.folder, arg)

    def test_landing_gear(self):
        m = list(validate_folder(self._tgt('LandingGear')))
        self.assertEqual(len(m), 8)

    def test_pcb(self):
        m = list(validate_folder(self._tgt('PrintedCircuitBoard')))
        self.assertEqual(len(m), 1)

    def test_ccdmrf(self):
        cat = LcCatalog.make_tester()
        res = cat.new_resource('epa.ccdmrf', self._tgt('CDDMRF'), 'OpenLcaJsonLdArchive', interfaces=('ex'))
        self.assertTrue(res.check(cat))


if __name__ == '__main__':
    unittest.main()
