import unittest

from .config import catalog_dir, TRUE_FG_NAME, ANNOTATED_XLSX_REL_PATH
from .. import create_annotated_foreground
from ..inventory_data import MockCfGenerator

from antelope_catalog import LcCatalog


class TestMocks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = LcCatalog(catalog_dir)
        cls.fg = create_annotated_foreground(cls.cat, TRUE_FG_NAME, ANNOTATED_XLSX_REL_PATH)

    def test_mocks(self):
        price = self.cat.query('local.usepa.useeio').get('b0682037-e878-4be4-a63a-a7a81053a691')
        mass = self.fg.get_canonical('mass')
        mock = MockCfGenerator(mass, price, ANNOTATED_XLSX_REL_PATH)

        f = self.fg.get('NAS6203-4D')
        self.assertTrue(mock.characterize(f, demo=True))


if __name__ == '__main__':
    unittest.main()
