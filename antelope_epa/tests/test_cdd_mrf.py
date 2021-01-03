import unittest
import os
from antelope_foreground import ForegroundCatalog
from antelope import MultipleReferences

from datetime import datetime
from .config import TEST_FG_NAME, ANNOTATED_XLSX_REL_PATH

from .. import create_annotated_foreground
from ..exceptions import MissingEpaForegroundEnvVar
from ..epa_psm_antelope import EpaBomForeground


CDD_REF = 'epa.cddmrf'
CDD_ID = '16cb496c-497f-3595-ba7d-df4e255c4b6c'
CDD_CONCRETE = '2aa21a50-e271-399b-a222-e0cd612e95e3'

class EpaCddTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = ForegroundCatalog.make_tester()
        try:
            cls.folder = os.path.join(os.getenv('EPA_FOREGROUND'), 'CDDMRF')
        except TypeError:
            raise MissingEpaForegroundEnvVar('export EPA_FOREGROUND')

    def test_0_access_resource(self):
        nr = self.cat.new_resource(CDD_REF, self.folder, 'OpenLcaJsonLdArchive', interfaces=('exchange', 'quantity'))
        self.assertTrue(nr.check(self.cat))

    def test_1_index_resource(self):
        today = datetime.now().strftime('%Y%m%d')
        self.assertEqual(self.cat.index_ref(CDD_REF), '.'.join([CDD_REF, 'index', today]))

    def test_2_access_process(self):
        p = next(self.cat.query(CDD_REF).processes())
        self.assertEqual(p.external_ref, CDD_ID)
        with self.assertRaises(MultipleReferences):
            p.reference()

    def test_3_create_fragment(self):
        p = self.cat.query(CDD_REF).get(CDD_ID)

        fg = self.cat.foreground('.'.join([CDD_REF, 'fg']))
        frag = fg.create_process_model(p, ref_flow=CDD_CONCRETE)
        fg.extend_process(frag)
