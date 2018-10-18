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

    def test_dates_before_curr(self):
        """US01: Unit Test: to ensure that all dates occur before the current date"""
        list_of_known_errors=["US01: The marriage of Future /Trunks/ and Mai /Trunks/ cannot occur after the current date.",
                              "US01: The divorce of Future /Trunks/ and Mai /Trunks/ cannot occur after the current date.",
                              "US01: The birth of Future /Trunks/ cannot occur after the current date.",
                              "US01: The birth of Mai /Trunks/ cannot occur after the current date.",
                              "US01: The death of Future /Trunks/ cannot occur after the current date."]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_indi_birth_before_marriage(self):
        """US02: Unit Test: to ensure that birth of an individual occurs before their marriage"""
        list_of_known_errors = ["US02: Johnny /Sway/'s birth can not occur after their date of marriage",
                                "US02: Missy /Kennedy/'s birth can not occur after their date of marriage",
                                "US02: Bobby /Bourne/'s birth can not occur after their date of marriage and Bella /Bourne/'s birth can not occur after their date of marriage" ]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_birth_before_death(self):
        """US03: Unit Test: to ensure that birth occurs before the death of an individual"""
        list_of_known_errors = ["US03: James /Nicholas/'s death can not occur before their date of birth",
                                "US03: Peter /Tosh/'s death can not occur before their date of birth"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_marr_before_div(self):
        """US04: Unit Test: to ensure that marriage dates come before divorce dates"""
        list_of_known_errors = [
            "US04: Johnson /Deere/ and Emily /Deere/'s divorce can not occur before their date of marriage"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_marr_div_before_death(self):
        """US05 & US06: Tests that the marr_div_before_death method works properly, the list of known errors is manually hard coded.
        It contains all of the errors we have intentionally put into the file and ensures the file catches them"""
        list_of_known_errors = ["US05 & US06: Either Mark /Eff/ or Jess /Eff/ were married or divorced after they died",
                                "US05 & US06: Either Troy /Johnson/ or Sammy /Johnson/ were married or divorced after they died"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_normal_age(self):
        """US07: Tests that the normal_age method works properly"""
        list_of_known_errors = [
            "US07: John /Old/'s age calculated (1000) is over 150 years old",
            "US07: Jackie /Old/'s age calculated (168) is over 150 years old"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_birth_before_marriage(self):
        """US08: Tests to see if birth_before_marriage function is working properly
            Will raise exceptions if birth is before marriage or 9
            months after the divorce of the parents"""
        #Tests child is born 1 month before parents are married
        list_of_known_errors = [
            "US08: Jimmy /Shmoe/ was born before their parents were married",
            "US08: Sammy /Shmoe/ was born 60 months after their parents were divorced"]
        #self.num_of_errors += len(list_of_known_errors)
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_birth_before_death_of_parents(self):
        """US09: Test if someone was born before their parent died"""
        list_of_known_errors = [
            "US09: Jimmy /James/ was born 10 months after father died",
            "US09: Jacob /James/ was born 61 months after father died",
            "US09: Jacob /James/ was born after mother died",
            "US09: Jackie /James/ was born 12 months after father died"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_spouses_too_young(self):
        """US10: Tests that the parents do not get married to each other when they are
        younger than 14 years old"""
        list_of_known_errors = [
            "US10: Bobby /Bourne/ was only -1 years old when they got married",
            "US10: Ann /Joene/ was only 13 years old when they got married",
            "US10: Nick /Jackson/ was only 9 years old when they got married"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_no_bigamy(self):
        """US11: Tests to see if no_bigamy function is working properly, catches all bigamists"""
        list_of_known_errors = ["US11: Matt /Smith/ is practing bigamy", "US11: Jen /Smith/ is practing bigamy"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_parents_too_old(self):
        """US12: Tests that parents are not too old relative to their children,
        Dad less than 80 years older and moter less than 60 years older"""
        list_of_known_errors = ["US12: John /Old/ is over 80 years older than his child Jessica /Old/",
                                "US12: Jackie /Old/ is over 60 years older than his child Jessica /Old/"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_sibling_spacing(self):
        """US13: Tests thatbirth dates of siblings should be more than 8 months apart or less than 2 days apart
        (twins may be born one day apart, e.g. 11:59 PM and 12:02 AM the following calendar day)"""
        list_of_known_errors = ["US13: Siblings One /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Two /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Three /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Four /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Five /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Six /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Seven /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Eight /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Nine /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Ten /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings El /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Twelve /Fif/ and Thirteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Thirteen /Fif/ and Fourteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Thirteen /Fif/ and Fifteen /Fif/'s births are only 5 days apart",
                                "US13: Siblings Allen /Leffe/ and Ava /Leffe/'s births are only 9 days apart"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_too_many_births(self):
        """US14: Tests that no more than five siblings should be born at the same time"""
        list_of_known_errors = ["US14: The /Fif/ family has more than five children born at the same time"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_too_many_siblings(self):
        """US15: Test: Makes sure too_many_siblings function works properly"""
        list_of_known_errors = ["US15: The /Fif/ family has 15 or more siblings"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_no_marriage_to_descendents(self):
        """US17: Test: Makes sure no_marriage_to_siblings finds all individiuals married to one fof their descendants"""
        list_of_known_errors = ["US17: John /Leffe/ cannot be married to their descendant Ava /Leffe/"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
