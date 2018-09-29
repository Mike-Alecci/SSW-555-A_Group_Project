import unittest
from GedcomProject import AnalyzeGEDCOM, Family, Individual, CheckForErrors
import datetime
import os

def gen_individual(self, name, sex, birt, deat):
    """Generates an Individual object and returns it.
    Parameters: name, sex, birt, deat"""
    person = Individual()
    person.name = name
    person.sex = sex
    person.birt = datetime.datetime.strptime(birt, "%d %b %Y").date()
    if deat != None:
        person.deat = datetime.datetime.strptime(deat, "%d %b %Y").date()
        person.alive = True
    else:
        person.alive = False
    return person

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

    def test_birth_before_death(self):
        """US03: Unit Test: to ensure that birth occurs before the death of an individual"""
        test_ind_dict = {}
        # Test 1: Date of death is after date of birth, NO ERROR
        test_ind_dict[1] = gen_individual(self, "Fake Person", "M", "26 FEB 1998", "26 FEB 1999")
        try:
            CheckForErrors(test_ind_dict, {}, False).birth_before_death()
        except ValueError:
            self.fail("test_birth_before_death() failed!")
        # Test 2: Date of death is before date of birth, ERROR
        test_ind_dict[1] = gen_individual(self, "Fake Person", "M", "26 FEB 1999", "26 FEB 1998")
        with self.assertRaises(ValueError):
            CheckForErrors(test_ind_dict, {}, False).birth_before_death()
        # Test 3: Date of death is same day as birth, NO ERROR
        test_ind_dict[1] = gen_individual(self, "Fake Person", "M", "26 FEB 1998", "26 FEB 1998")
        try:
            CheckForErrors(test_ind_dict, {}, False).birth_before_death()
        except ValueError:
            self.fail("test_birth_before_death() failed!")
        # Test 4: Date of death is 1 day after birth, NO ERROR
        test_ind_dict[1] = gen_individual(self, "Fake Person", "M", "26 FEB 1998", "27 FEB 1998")
        try:
            CheckForErrors(test_ind_dict, {}, False).birth_before_death()
        except ValueError:
            self.fail("test_birth_before_death() failed!")
        # Test 5: Date of death is 1 day before birth, ERROR
        test_ind_dict[1] = gen_individual(self, "Fake Person", "M", "27 FEB 1998", "26 FEB 1998")
        with self.assertRaises(ValueError):
            CheckForErrors(test_ind_dict, {}, False).birth_before_death()

    #def test_marr_before_div(self):
    #    """US04: Unit Test: to ensure that marriage dates come before divorce dates"""


    #def test_num_errors(self):
    #    """This checks to ensure the program did not catch any errors that we didn't test against"""
    #    self.assertEqual(len(self.all_errors), self.num_of_errors)

    def test_birth_before_marriage(self):
        """Tests to see if birth_before_marriage function is working properly
            Will raise exceptions if birth is before marriage or 9
            months after the divorce of the parents"""
        #Tests child is born 1 month before parents are married
        test_ind_dict = {1 : Individual()} #creates dictionary of individuals
        test_fam_dict = {1: Family()}
        test_ind_dict[1].name, test_ind_dict[1].famc, test_ind_dict[1].birt = "Fake Child", 1, datetime.datetime.strptime("9 MAR 2001", "%d %b %Y").date()
        test_fam_dict[1].husb = Individual()
        test_fam_dict[1].wife = Individual()
        test_fam_dict[1].chil = test_ind_dict[1]
        test_fam_dict[1].marr = datetime.datetime.strptime("9 JUN 2001", "%d %b %Y").date()
        with self.assertRaises(ValueError): 
            CheckForErrors(test_ind_dict, test_fam_dict).birth_before_marriage()

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
