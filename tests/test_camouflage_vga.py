import unittest
import atomseeker

import datetime


class TestCamoflageVga(unittest.TestCase):

    def get_list(self, atom_list, atom_type):
        """get list of atoms which type are `atom_type'"""

        return [atom for atom in atom_list if atom.type == atom_type]

    def get_moov(self):
        """get moov-atom"""

        moov_list = self.get_list(self.parsed, 'moov')

        assert len(moov_list) == 1

        return moov_list[0]

    def get_mvhd(self):
        """get mvhd-atom"""

        moov = self.get_moov()

        mvhd_list = self.get_list(moov.children, 'mvhd')

        assert len(mvhd_list) == 1

        return mvhd_list[0]

    def get_trak(self):
        """get trak-atom"""

        moov = self.get_moov()

        trak_list = self.get_list(moov.children, 'trak')

        assert len(trak_list) == 1

        return trak_list[0]

    def get_mdia(self):
        """get mdia-atom"""

        trak = self.get_trak()

        mdia_list = self.get_list(trak.children, 'mdia')

        assert len(mdia_list) == 1

        return mdia_list[0]

    def setUp(self):

        with open("tests/samples/camouflage_vga.mp4", 'rb') as f:
            self.parsed = atomseeker.atom.parse_atoms(f)

    def test_ftyp(self):

        ftyp_list = self.get_list(self.parsed, 'ftyp')

        assert len(ftyp_list) == 1

        ftyp = ftyp_list[0]

        assert ftyp.elements['Major_Brand'] == "isom"
        assert ftyp.elements['Minor_Version'] == 512

        assert 'isom' in ftyp.elements['Compatible_Brands']
        assert 'mp41' in ftyp.elements['Compatible_Brands']

    def test_mdat(self):

        mdat_list = self.get_list(self.parsed, 'mdat')

        assert len(mdat_list) == 1

        mdat = mdat_list[0]

    def test_mvhd(self):

        mvhd = self.get_mvhd()

        assert (mvhd.elements['Creation_time'].date ==
                datetime.datetime(1904, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))

        mvhd.elements['Matrix_structure'].a == 1.0
        mvhd.elements['Matrix_structure'].b == 0.0
        mvhd.elements['Matrix_structure'].u == 0.0
        mvhd.elements['Matrix_structure'].c == 0.0
        mvhd.elements['Matrix_structure'].d == 1.0
        mvhd.elements['Matrix_structure'].v == 0.0
        mvhd.elements['Matrix_structure'].x == 0.0
        mvhd.elements['Matrix_structure'].y == 0.0
        mvhd.elements['Matrix_structure'].w == 1.0

    def test_mdhd(self):

        mdia = self.get_mdia()

        mdhd_list = self.get_list(mdia.children, 'mdhd')
        assert len(mdhd_list) == 1

        mdhd = mdhd_list[0]

        assert (mdhd.elements['Creation_time'].date == datetime.datetime(
            1904, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))
        assert mdhd.elements['Language'].__str__() == 'und'
        assert mdhd.elements['Quality'] == 0
