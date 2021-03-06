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
        list_of_known_errors = ["US13: Siblings Allen /Leffe/ and Ava /Leffe/'s births are 68 days apart",
                                "US13: Siblings Bill /Leffe/ and Lauren /Leffe/'s births are 59 days apart",
                                "US13: Siblings Jimmy /James/ and Jackie /James/'s births are 45 days apart",
                                "US13: Siblings Lauren /Leffe/ and Bill /Leffe/'s births are 59 days apart",
                                "US13: Siblings Thirteen /Fif/ and Fifteen /Fif/'s births are 5 days apart",
                                "US13: Siblings Thirteen /Fif/ and Fourteen /Fif/'s births are 5 days apart"]
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

    def test_no_marriage_to_siblings(self):
        """US18: Test: Makes sure no_marriage_to_siblings finds all individuals married to one of their siblings"""
        list_of_known_errors = ["US18: Gorl /Sib/ cannot be married to their sibling Boyle /Sib/"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_no_marriage_to_cousin(self):
        """US19: Tests to ensure that no_marriage_to_cousin finds all individuals married to their cousin"""
        list_of_known_errors =["US19: Curr /Two/ cannot be married to their cousin Cuz /One/",
                                "US19: Currt /Two/ cannot be married to their cousin Cuzt /Two/"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_creepy_aunts_and_uncles(self):
        """US20: Tests to ensure that aunts and uncles should not marry their nieces or nephews"""
        list_of_known_errors = ["US20: Niece /Pigsty/ is married to their aunt or uncle"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_correct_gender_role(self):
        """US21: Tests to ensure husband in family should be male and wife in family should be female"""
        list_of_known_errors = ["US21: The husband in the Par family, (Martha /Par/), is a female!",
                                "US21: The husband in the Switcheroo family, (James /Switcheroo/), is a female!",
                                "US21: The wife in the Johnson family, (Sammy /Johnson/), is a male!",
                                "US21: The wife in the Par family, (Far /Par/), is a male!",
                                "US21: The wife in the Switcheroo family, (Jenny /Switcheroo/), is a male!",]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_unique_ids(self):
        """US22: Tests to ensure that all IDS are unique"""
        list_of_known_errors = ["US22: The individual ID: I52, already exists, this ID is not unique",
                                "US22: The family ID: F1, already exists, this ID is not unique"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_unique_names_and_bdays(self):
        """US23: Tests to ensure there are no individuals with the same name and birthdate"""
        list_of_known_errors = ["US23: An idividual with the name: Ava /Leffe/, and birthday: 1961-01-01, already exists!",
                                "US23: An idividual with the name: Allen /Leffe/, and birthday: 1961-03-10, already exists!"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_unique_spouses_in_family(self):
        """US24: Tests to ensure that there are no duplicate family entries, with the same
            spouses (by name) and marriage dates"""
        list_of_known_errors = [
            "US24: The family with spouses Future /Trunks/ and Mai /Trunks/ married on 2045-03-15 occurs more than once in the GEDCOM file.",
            "US24: The family with spouses John /Leffe/ and Ava /Leffe/ married on 1980-02-11 occurs more than once in the GEDCOM file."
            ]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_unique_children_in_family(self):
        """US25: Tests to ensure that there are no duplicate children within the same family
            with the same name and the same birthdate"""
        list_of_known_errors = [
            "US25: There is more than one child with the name Lauren /Leffe/ and birthdate 1921-03-08 in family F18",
            "US25: There is more than one child with the name Sloham /Jog/ and birthdate 1990-01-17 in family F24"
            ]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_list_ages(self):
        """US27: Tests to ensure that people's ages are properly being calculated when listed in
            the GEDCOM table"""
        list_of_known_errors = [
            "US27: John /Old/ calculated age is 1000 == 1000 years old",
            "US27: Jess /Eff/ calculated age is 51 == 51 years old"
        ]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)
        #Tests Exception (without birthday) - Raises AttributeError
        test_ind_dict = {1 : Individual(), 2: Individual()} #creates dictionary of individuals
        test_ind_dict[1].name, test_ind_dict[1].deat = "NoBirth /DateGuy/", datetime.datetime.strptime("9 MAR 1001", "%d %b %Y").date()
        test_ind_dict[2].name = "NoBirth /OrDeath/"
        with self.assertRaises(AttributeError):
            test_ind_dict[1].update_age()
        with self.assertRaises(AttributeError):
            test_ind_dict[2].update_age()

    def test_order_siblings_oldest_to_youngest(self):
        """US28: Tests to ensure that siblings are ordered from oldest to youngest"""
        list_of_known_errors = [
            "US28: The children in family F15 from oldest to youngest are ['Jimmy /James/', 'Jackie /James/', 'Jacob /James/']",
            "US28: The children in family F20 from oldest to youngest are ['Ava /Leffe/', 'Allen /Leffe/']",
            "US28: The children in family F25 from oldest to youngest are ['Gorl /Sib/', 'Boyle /Sib/']"
        ]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_list_deceased(self):
        """US29: Tests to ensure that all deceased individuals are listed"""
        list_of_known_errors = ["US29: Future /Trunks/ is deceased","US29: James /Nicholas/ is deceased",
        "US29: Jessica /Joseline/ is deceased", "US29: John /Old/ is deceased",
        "US29: Johnny /James/ is deceased", "US29: Mark /Eff/ is deceased",
        "US29: Peter /Tosh/ is deceased", "US29: Stevie /Wonder/ is deceased", "US29: Troy /Johnson/ is deceased"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_list_living_married(self):
        """US30: Tests to ensure that all individuals who are alive and still married are listed"""
        list_of_known_errors = ["US30: Emily /Deere/ is alive and married", "US30: Future /Trunks/ is alive and married",
        "US30: Jane /Leffe/ is alive and married", "US30: Jen /Smith/ is alive and married",
        "US30: Joe /Shmoe/ is alive and married", "US30: John /Leffe/ is alive and married",
        "US30: Johnson /Deere/ is alive and married", "US30: Mai /Trunks/ is alive and married",
        "US30: Mary /Shmoe/ is alive and married", "US30: Matt /Smith/ is alive and married",
        "US30: Sammy /Johnson/ is alive and married", "US30: Troy /Johnson/ is alive and married"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_list_living_single(self):
        """US31: Tests to ensure that all individuals who are alive, single, and over 30 are listed"""
        list_of_known_errors = ["US31: Allen /Leffe/ is single and alive",
                                "US31: Ava /Leffe/ is single and alive",
                                "US31: Far /Par/ is single and alive",
                                "US31: Lauren /Leffe/ is single and alive",
                                "US31: Martha /Par/ is single and alive"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def list_multiple_births(self):
        """US32: Tests to ensure that all families who have had multiple births are listed"""
        list_of_known_errors = ["US32: The /Fif/ family has had 2 children born at the same time",
                                "US32: The /Fif/ family has had 4 children born at the same time",
                                "US32: The /Fif/ family has had 6 children born at the same time",
                                "US32: The /Leffe/ family has had 2 children born at the same time",
                                "US32: The /Quick/ family has had 2 children born at the same time"]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

    def test_list_anniversaries(self):
        """US39: Tests to ensure that all anniversaries to occur in the next 30 days are listed"""
        list_of_known_errors = ["US39: Art /Versity/ and Ann /Versity/ have an anniversary coming within the next 30 days."]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)
            
    def test_invalid_dates(self):
        """US42: Tests to ensure that all invalid dates are detected and rejected"""
        list_of_known_errors = ["US42: -5 JAN 2014 is an illegitimate date for Jim /John/'s and Jan /Jobs/'s divorce. The date has been adjusted to the nearest valid date.",
                                "US42: 30 FEB 1990 is an illegitimate date for Jim /John/'s birthday. The date has been adjusted to the nearest valid date.",
                                "US42: 32 DEC 2012 is an illegitimate date for Jim /John/'s and Jan /Jobs/'s marriage. The date has been adjusted to the nearest valid date.",
                                "US42: 32 MAY 2015 is an illegitimate date for Jim /John/'s death. The date has been adjusted to the nearest valid date."]
        for error in list_of_known_errors:
            self.assertIn(error, self.all_errors)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
