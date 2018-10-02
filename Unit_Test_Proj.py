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
    person.update_age()
    return person

class ProjectTest(unittest.TestCase):
    """Tests that our GEDCOM parser is working properly"""

    def __init__(self, *args, **kwargs):
        super(ProjectTest, self).__init__(*args, **kwargs)
        cwd = os.path.dirname(os.path.abspath(__file__)) #gets directory of the file
        file_name = cwd + "\Bad_GEDCOM_test_data.ged"
        self.all_errors = AnalyzeGEDCOM(file_name, False, False).all_errors #done in this method so it only happens once


    def test_indi_birth_before_marriage(self):
        """US02: Unit Test: to ensure that birth of an individual occurs before their marriage"""
        list_of_known_errors = ["Johnny /Sway/'s birth can not occur before their date of marriage",
                                "Missy /Kennedy/'s birth can not occur before their date of marriage",
                                "Bobby /Bourne/'s birth can not occur before their date of marriage and Bella /Bourne/'s birth can not occur before their date of marriage" ]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_marr_div_before_death(self):
        """Tests that the marr_div_before_death method works properly, the list of known errors is manually hard coded.
        It contains all of the errors we have intentionally put into the file and ensures the file catches them"""
        list_of_known_errors = ["Either Mark /Eff/ or Jess /Eff/ were married or divorced after they died", "Either Troy /Johnson/ or Sammy /Johnson/ were married or divorced after they died"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_normal_age(self):
        """US07: Tests that the normal_age method works properly"""
        list_of_known_errors = [
            "John /Old/'s age calculated (1000) is over 150 years old",
            "Jackie /Old/'s age calculated (168) is over 150 years old"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

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

    def test_marr_before_div(self):
        """US04: Unit Test: to ensure that marriage dates come before divorce dates"""
        list_of_known_errors = [
            "Johnson /Deere/ and Emily /Deere/'s divorce can not occur before their date of marriage"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    #def test_num_errors(self):
    #    """This checks to ensure the program did not catch any errors that we didn't test against"""
    #    self.assertEqual(len(self.all_errors), self.num_of_errors)

    def test_birth_before_marriage(self):
        """US08: Tests to see if birth_before_marriage function is working properly
            Will raise exceptions if birth is before marriage or 9
            months after the divorce of the parents"""
        #Tests child is born 1 month before parents are married
        list_of_known_errors = [
            "Jimmy /Shmoe/ was born before their parents were married",
            "Sammy /Shmoe/ was born 60 months after their parents were divorced"]
        #self.num_of_errors += len(list_of_known_errors)
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
