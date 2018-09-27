import unittest
from GedcomProject import AnalyzeGEDCOM, Family, Individual, CheckForErrors
import datetime
import os

class ProjectTest(unittest.TestCase):
    """Tests that our GEDCOM parser is working properly"""
    
    def __init__(self, *args, **kwargs):
        super(ProjectTest, self).__init__(*args, **kwargs)
        cwd = os.path.dirname(os.path.abspath(__file__)) #gets directory of the file
        file_name = cwd + "\Bad_GEDCOM_test_data.ged"
        self.all_errors = AnalyzeGEDCOM(file_name, False, False).all_errors #done in this method so it only happens once
        #self.num_of_errors

    def test_marr_div_before_death(self):
        """Tests that the marr_div_before_death method works properly, the list of known errors is manually hard coded.
        It contains all of the errors we have intentionally put into the file and ensures the file catches them"""
        list_of_known_errors = ["Either Mark /Eff/ or Jess /Eff/ were married or divorced after they died", "Either Troy /Johnson/ or Sammy /Johnson/ were married or divorced after they died"]
        #self.num_of_errors += len(list_of_known_errors)
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)
        

    def test_normal_age(self):
        """Tests that the normal_age method works properly, the first tests assertraises tests a bad 
        inputs, the following checks are just based off fake dictionary info added"""
        #Tests age is 1000
        test_ind_dict = {1 : Individual()} #creates dictionary of individuals
        test_ind_dict[1].name, test_ind_dict[1].deat, test_ind_dict[1].birt = "Fake Person", datetime.datetime.strptime("9 MAR 2001", "%d %b %Y").date(), datetime.datetime.strptime("9 MAR 1001", "%d %b %Y").date() 
        test_ind_dict[1].update_age()
        with self.assertRaises(ValueError): 
            CheckForErrors(test_ind_dict, {}, False).normal_age()
        #Tests age is 150
        test_ind_dict[1].name, test_ind_dict[1].deat, test_ind_dict[1].birt = "Fake Person", datetime.datetime.strptime("9 MAR 2000", "%d %b %Y").date(), datetime.datetime.strptime("9 MAR 1850", "%d %b %Y").date() 
        test_ind_dict[1].update_age()
        with self.assertRaises(ValueError):     
            CheckForErrors(test_ind_dict, {}, False).normal_age()
        #Tests age is 149
        test_ind_dict[1].name, test_ind_dict[1].deat, test_ind_dict[1].birt = "Fake Person", datetime.datetime.strptime("9 MAR 2000", "%d %b %Y").date(), datetime.datetime.strptime("9 MAR 1851", "%d %b %Y").date() 
        test_ind_dict[1].update_age()
        self.assertEqual(test_ind_dict[1].age, 149)
        #Tests no birthdate
        test_ind_dict[1].name, test_ind_dict[1].deat, test_ind_dict[1].birt = "Fake Person", None, "1,1,2009" 
        with self.assertRaises(AttributeError):
            test_ind_dict[1].update_age()
            CheckForErrors(test_ind_dict, {}, False).normal_age()
        #Tests 200 years old with no death date
        test_ind_dict[1].name, test_ind_dict[1].deat, test_ind_dict[1].birt = "Fake Person", None, datetime.datetime.strptime("9 MAR 1818", "%d %b %Y").date() 
        test_ind_dict[1].update_age()
        with self.assertRaises(ValueError):
            CheckForErrors(test_ind_dict, {}, False).normal_age()

    #def test_num_errors(self):
    #    """This checks to ensure the program did not catch any errors that we didn't test against"""
    #    self.assertEqual(len(self.all_errors), self.num_of_errors)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)