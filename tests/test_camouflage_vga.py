import unittest
import atomseeker

import datetime


def trans_int_to_iso_language_code(n):
    """transform 16-bit value to ISO Language Code
    see <https://developer.apple.com/library/content/documentation/QuickTime/QTFF/QTFFChap4/qtff4.html#//apple_ref/doc/uid/TP40000939-CH206-27005> for detail
    """

    return "%c%c%c" % [chr(((n >> 10) & 0x1f) + 0x60), chr(((n >> 5) & 0x1f) + 0x60), chr((n & 0x1f) + 0x60)]


class TestCamoflageVga(unittest.TestCase):

    def get_list(self, atom_list, atom_type):
        """get list of atoms which type are `atom_type'"""

        return [atom for atom in atom_list if atom.type == atom_type]

    def get_moov(self):
        """get moov-atom"""

        moov_list = self.get_list(self.parsed, 'moov')
        self.assertEqual(len(moov_list), 1)

        return moov_list[0]

    def get_mvhd(self):
        """get mvhd-atom"""

        moov = self.get_moov()

        mvhd_list = self.get_list(moov.children, 'mvhd')
        self.assertEqual(len(mvhd_list), 1)

        return mvhd_list[0]

    def get_trak(self):
        """get trak-atom"""

        moov = self.get_moov()

        trak_list = self.get_list(moov.children, 'trak')
        self.assertEqual(len(trak_list), 1)

        return trak_list[0]

    def get_mdia(self):
        """get mdia-atom"""

        trak = self.get_trak()

        mdia_list = self.get_list(trak.children, 'mdia')
        self.assertEqual(len(mdia_list), 1)

        return mdia_list[0]

    def setUp(self):

        with open("tests/samples/camouflage_vga.mp4", 'rb') as f:
            self.parsed = atomseeker.atom.parse_atoms(f)

    def test_ftyp(self):

        ftyp_list = self.get_list(self.parsed, 'ftyp')
        self.assertEqual(len(ftyp_list), 1)

        ftyp = ftyp_list[0]
        self.assertEqual(ftyp.elements['Major_Brand'], "isom")
        self.assertEqual(ftyp.elements['Minor_Version'], 512)
        self.assertIn('isom', ftyp.elements['Compatible_Brands'])
        self.assertIn('mp41', ftyp.elements['Compatible_Brands'])

    def test_mdat(self):

        mdat_list = self.get_list(self.parsed, 'mdat')
        self.assertEqual(len(mdat_list), 1)

        mdat = mdat_list[0]

    def test_mvhd(self):

        mvhd = self.get_mvhd()

        self.assertEqual(mvhd.elements['Creation_time'].date,
                         datetime.datetime(1904, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))

        self.assertEqual(mvhd.elements['Matrix_structure'].a, 1.0)
        self.assertEqual(mvhd.elements['Matrix_structure'].b, 0.0)
        self.assertEqual(mvhd.elements['Matrix_structure'].u, 0.0)
        self.assertEqual(mvhd.elements['Matrix_structure'].c, 0.0)
        self.assertEqual(mvhd.elements['Matrix_structure'].d, 1.0)
        self.assertEqual(mvhd.elements['Matrix_structure'].v, 0.0)
        self.assertEqual(mvhd.elements['Matrix_structure'].x, 0.0)
        self.assertEqual(mvhd.elements['Matrix_structure'].y, 0.0)
        self.assertEqual(mvhd.elements['Matrix_structure'].w, 1.0)

    def test_mdhd(self):

        mdia = self.get_mdia()

        mdhd_list = self.get_list(mdia.children, 'mdhd')
        self.assertEqual(len(mdhd_list), 1)
        mdhd = mdhd_list[0]

        self.assertEqual(mdhd.elements['Creation_time'].date,
                         datetime.datetime(1904, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(
            trans_int_to_iso_language_code(mdhd.elements['Language']), 'und')
        self.assertEqual(mdhd.elements['Quality'], 0)
