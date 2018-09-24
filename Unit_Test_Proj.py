import unittest
from GedcomProject import AnalyzeGEDCOM, Family, Individual, CheckForErrors
import datetime
import os

class ProjectTest(unittest.TestCase):
    """Tests that our GEDCOM parser is working properly"""
    def test_marr_div_before_death(self):
        """Tests that the marr_div_before_death method works properly, the first tests assertraises tests a bad 
        GEDCOM file, the following four checks are just based off fake dictionary info added"""
        with self.assertRaises(ValueError):
            AnalyzeGEDCOM("Bad_GEDCOM_test_data.ged", False)    #File contains both marr and div before death
        test_ind_dict = {1 : Individual(), 2: Individual()}
        test_ind_dict[1].name, test_ind_dict[1].deat, test_ind_dict[1].fams = "Fake Person 1", None, 1 
        test_ind_dict[2].name, test_ind_dict[2].deat, test_ind_dict[2].fams = "Fake Person 2", datetime.datetime.strptime("9 MAR 1998", "%d %b %Y").date(), 1
        test_fam_dict = {1: Family()}
        test_fam_dict[1].marr, test_fam_dict[1].husb, test_fam_dict[1].wife, test_fam_dict[1].div = datetime.datetime.strptime("9 MAR 2000", "%d %b %Y").date(), 1, 2, "NA"
        with self.assertRaises(ValueError):     #Wife is dead before Marr
            CheckForErrors(test_ind_dict, test_fam_dict)
        test_ind_dict[1].name, test_ind_dict[1].deat, test_ind_dict[1].fams = "Fake Person 1", None, 1 
        test_ind_dict[2].name, test_ind_dict[2].deat, test_ind_dict[2].fams = "Fake Person 2", datetime.datetime.strptime("9 MAR 2001", "%d %b %Y").date(), 1
        test_fam_dict[1].marr, test_fam_dict[1].husb, test_fam_dict[1].wife, test_fam_dict[1].div = datetime.datetime.strptime("9 MAR 2000", "%d %b %Y").date(), 1, 2, datetime.datetime.strptime("10 MAR 2003", "%d %b %Y").date()
        with self.assertRaises(ValueError):     #Wife is dead before div
            CheckForErrors(test_ind_dict, test_fam_dict)
        test_ind_dict[1].name, test_ind_dict[1].deat, test_ind_dict[1].fams = "Fake Person 1", datetime.datetime.strptime("9 MAR 1998", "%d %b %Y").date(), 1 
        test_ind_dict[2].name, test_ind_dict[2].deat, test_ind_dict[2].fams = "Fake Person 2", datetime.datetime.strptime("9 MAR 1998", "%d %b %Y").date(), 1
        test_fam_dict[1].marr, test_fam_dict[1].husb, test_fam_dict[1].wife, test_fam_dict[1].div = datetime.datetime.strptime("9 MAR 2000", "%d %b %Y").date(), 1, 2, "NA"
        with self.assertRaises(ValueError):     #Husb and Wife are dead before Marr
            CheckForErrors(test_ind_dict, test_fam_dict)
        test_ind_dict[1].name, test_ind_dict[1].deat, test_ind_dict[1].fams = "Fake Person 1", datetime.datetime.strptime("9 MAR 2001", "%d %b %Y").date(), 1 
        test_ind_dict[2].name, test_ind_dict[2].deat, test_ind_dict[2].fams = "Fake Person 2", None, 1
        test_fam_dict[1].marr, test_fam_dict[1].husb, test_fam_dict[1].wife, test_fam_dict[1].div = datetime.datetime.strptime("9 MAR 2000", "%d %b %Y").date(), 1, 2, "NA"
        diff = (test_fam_dict[1].marr - test_ind_dict[1].deat).days 
        self.assertEqual(CheckForErrors(test_ind_dict, test_fam_dict).marr_div_before_death(), None)  
        #Here the husb is dead but after marriage, this should have no errors and run through the function and return None


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)