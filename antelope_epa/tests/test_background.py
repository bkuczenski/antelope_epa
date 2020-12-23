import unittest
import os

from .config import catalog_dir, USEEIO_REF, USLCI_REF, ELCD_REF

from antelope_catalog import LcCatalog
from lcatools.interfaces import UnknownOrigin


def _fetch_uslci(cat):
    from antelope_catalog.data_sources.local import make_config
    us = make_config('uslci')

    for res in us.make_resources(USLCI_REF):
        cat.add_resource(res)


def _fetch_useeio(cat):
    cat.new_resource(USEEIO_REF, None, 'OpenLcaJsonLdArchive',
                     interfaces=('inventory', 'quantity'), static=False,
                     download={
                         'url': 'https://pasteur.epa.gov/uploads/10.23719/1375574/USEEIOv1.1-JSONLD-foropenlca.zip',
                         'md5sum': 'dda25b5f25fe4112e592029373525773'},
                     config={'hints': [('context', 'air', 'to air'), ('context', 'water', 'to water')]})


def _fetch_elcd(cat):
    elcd_file = os.path.join(catalog_dir, 'archives', 'ELCD3.2-excerpt.zip')
    cat.new_resource(ELCD_REF, elcd_file, 'IlcdArchive', interfaces=('inventory', 'quantity'))


class TestBackground(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = LcCatalog(catalog_dir)

    def test_uslci(self):
        try:
            q = self.cat.query(USLCI_REF)
        except UnknownOrigin:
            _fetch_uslci(self.cat)
            q = self.cat.query(USLCI_REF)
        self.assertEqual(q.get('0aaf1e13-5d80-37f9-b7bb-81a6b8965c71').name, 'Petroleum refining, at refinery [RNA]')

    def test_useeio(self):
        try:
            q = self.cat.query(USEEIO_REF)
        except UnknownOrigin:
            _fetch_useeio(self.cat)
            q = self.cat.query(USEEIO_REF)
        usd = q.get('b0682037-e878-4be4-a63a-a7a81053a691')
        self.assertEqual(usd.name, 'Producer Price US 2013 [USD]')

    def test_elcd(self):
        try:
            q = self.cat.query(ELCD_REF)
        except UnknownOrigin:
            _fetch_elcd(self.cat)
            q = self.cat.query(ELCD_REF)
        p = q.get('e16174fe-6542-4572-90bc-8980616ebe53')
        self.assertEqual(p.reference().flow.name, 'Steel hot rolled coil')


if __name__ == '__main__':
    unittest.main()
