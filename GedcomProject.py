from prettytable import PrettyTable
import datetime
from collections import defaultdict
from copy import deepcopy
import os

class AnalyzeGEDCOM:
    """This class analyzes the GEDCOM file and sorts information into the family and individual classes respectively for analysis"""
    def __init__(self, file_name, create_tables = True, print_errors = True):
        self.file_name = file_name
        self.family = dict()        #dictionary with Key = FamID Value = Family class object
        self.individuals = dict()   #dictionary with Key = IndiID Value = Individual class object
        self.errors = []
        self.fam_table = PrettyTable(field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
        self.indi_table = PrettyTable(field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"])
        self.analyze()
        if create_tables:           #allows to easily toggle the print of the pretty table on and off
            self.create_pretty_tables()
        self.all_errors = CheckForErrors(self.individuals, self.family, self.errors, print_errors).all_errors

    def analyze(self):
        """This method reads in each line and determines if a new family or individual need to be made, if not then it sends the line
           to be analyzed further in analyze_info"""
        indiv, fam, previous_line, current_type = "", "", [], 0
        read_GEDCOM_file = self.read_files(self.file_name, error_mess = "A misformatted line was found!", seperator = " " )
        for line in read_GEDCOM_file:                                       #Reads each line from the generator
            if line[0] == '0' and line[1] in ["HEAD", "TRLR", "NOTE"]:      #These cases provide no information we need to analyze
                continue
            elif line[0] == '0' and line [2] == "INDI":
                current_type = 1                                            #Marker used to ensure following lines are analyzed as individual
                indiv = line[1].replace("@", "")                            #The GEDCOM file from online has @ID@ format, this replaces it
                if indiv in self.individuals.keys():                        #If there is a duplicate ID report it
                    self.errors += ["US22: The individual ID: {}, already exists, this ID is not unique".format(indiv)]
                else:
                    self.individuals[indiv] = Individual()                  #The instance of a Individual class object is created
                continue
            elif line[0] == '0' and line[2] == "FAM":
                current_type = 2                                            #Marker used to ensure following lines are analyzed as family
                fam = line[1].replace("@", "")
                if fam in self.family.keys():                               #If there is a duplicate ID report it
                    self.errors += ["US22: The family ID: {}, already exists, this ID is not unique".format(fam)]
                else:
                    self.family[fam] = Family()                             #The instance of a Family class object is created
                continue
            if current_type in [1,2]:                                       #No new Individual or Family was created, analyze line further
                self.analyze_info(line, previous_line, indiv, fam, current_type)
            previous_line = line
        for indiv in self.individuals.values():
            indiv.update_age()


    def analyze_info(self, line, previous_line, idn, fam, current_type):
        """This analyzes each line's information and stores it in the appropriate place in the appropriate class"""
        if len(line) == 2:
            return      #We only need this line when it becomes the previous line
        else:           #Populates the variables in the Individuals class and Family class
            level, tag, arg = line
            level = int(level)
            if level == 1 and tag in ["NAME", "SEX", "FAMC", "FAMS", "HUSB", "WIFE", "CHIL"]:
                arg = arg.replace("@", "")
                if current_type == 1:                      #individual analysis
                    if tag == "FAMS":
                        self.individuals[idn].fams.add(arg)
                    elif tag == "NAME":
                        self.individuals[idn].name = arg
                    elif tag == "SEX":
                        self.individuals[idn].sex = arg
                    elif tag == "FAMC":
                        self.individuals[idn].famc = arg
                elif current_type == 2:                     #family analysis
                    if tag == "HUSB":
                        self.family[fam].husb = arg
                    elif tag == "WIFE":
                        self.family[fam].wife = arg
                    elif tag == "CHIL":
                        self.family[fam].chil.add(arg)
            elif level == 2 and tag == "DATE":              #Handles dates for both INDI and FAM cases
                p_level, p_tag = previous_line
                arg = datetime.datetime.strptime(arg, "%d %b %Y").date()
                if p_level == "1" and p_tag in ["BIRT", "DEAT", "MARR", "DIV"]:
                    if current_type == 1:                   #individual analysis
                        if p_tag == "BIRT":
                            self.individuals[idn].birt = arg
                        elif p_tag == "DEAT":
                            self.individuals[idn].deat = arg
                    elif current_type == 2:                 #family analysis
                        if p_tag == "MARR":
                            self.family[fam].marr = arg
                        elif p_tag == "DIV":
                            self.family[fam].div = arg


    def create_pretty_tables(self):
        """Populates the pretty tables with all necessary summary information"""
        print("Individual Table")
        for ID, ind in self.individuals.items():
            self.indi_table.add_row([ID, ind.name, ind.sex, ind.birt, ind.age, ind.alive, ind.deat, ind.famc, ind.fams])
        print(self.indi_table)
        print("Family Table")
        for ID, fam in self.family.items():
            self.fam_table.add_row([ID, fam.marr, fam.div, fam.husb, self.individuals[fam.husb].name, fam.wife, self.individuals[fam.wife].name, fam.chil])
        print(self.fam_table)

    def read_files(self, file_name, error_mess, seperator = "\t"):
            """A generic read file generator to check bad file inputs and read line by line"""
            try:
                fp = open(file_name, 'r')
            except FileNotFoundError:
                raise FileNotFoundError ("Could not open {}".format(file_name))
            else:
                with fp:
                    for line in fp:
                        l = line.strip().split(seperator, 2)
                        yield l


class Family:
    """This stores all the pertinent information about a family"""
    def __init__(self):
        self.marr = None #date of marriage
        self.div = None #date of divorce
        self.husb = None #husband ID
        self.wife = None #wife ID
        self.chil = set() #set of children


class Individual:
    """This class stores all the pertinent information about an individual"""
    def __init__(self):
        """This captures all the relevant information for an individual, it also instantiates null values in case information is incomplete"""
        self.name = None
        self.sex = None
        self.birt = None
        self.age = None
        self.alive = True
        self.deat = None
        self.famc = None
        self.fams = set()

    def update_age(self):
        """Checks to see if INDI is dead, and finds their age"""
        self.alive = self.deat == None
        try:
            if self.alive:
                self.age = datetime.datetime.today().year - self.birt.year
            else:
                self.age = self.deat.year - self.birt.year
        except AttributeError:
            raise AttributeError("Improper records of birth/death, need proper birth/death date to calculate age")

class CheckForErrors:
    """This class runs through all the user stories and looks for possible errors in the GEDCOM data"""
    def __init__(self, ind_dict, fam_dict, errors, print_errors):
        """This instantiates variables in this class to the dictionaries of families and individuals from
        the AnalyzeGEDCOM class, it also calls all US methods while providing an option to print all errors"""
        self.individuals = ind_dict
        self.family = fam_dict
        self.all_errors = errors
        self.dates_before_curr() #US01
        self.indi_birth_before_marriage() #US02
        self.birth_before_death() #US03
        self.marr_before_div() #US04
        self.marr_div_before_death() #US05 & US06
        self.normal_age() #US07
        self.birth_before_marriage() #US08
        self.brith_before_death_of_parents() #US09
        self.spouses_too_young() #US10
        self.no_bigamy() #US11
        self.parents_too_old() #US12
        self.sibling_spacing() #US13
        self.too_many_births()
        self.too_many_siblings() #US15
        self.no_marriage_to_descendants()#US17
        self.no_marriage_to_siblings() #US18
        self.no_marriage_to_cousin() #US19
        self.creepy_aunts_and_uncles() #US20
        self.correct_gender_role() #US21
        self.unique_names_and_bdays() #US23
        self.unique_spouses_in_family() #US24
        self.unique_children_in_family() #US25

        if print_errors == True:
            self.print_errors()

    def date_difference(self, d1, d2):
        """Returns true if the difference between the two dates is positive: [d1 - d2]"""
        return (d1 - d2).days

    def dates_before_curr(self):
        """US01: Tests to ensure any dates do not occur after current date"""
        for fam in self.family.values():
            marrDate=fam.marr
            divDate=fam.div
            if(marrDate>datetime.datetime.now().date()):
                self.all_errors+=["US01: The marriage of {} and {} cannot occur after the current date.".format(self.individuals[fam.husb].name, self.individuals[fam.wife].name)]
            if(divDate != None and divDate>datetime.datetime.now().date()):
                self.all_errors+=["US01: The divorce of {} and {} cannot occur after the current date.".format(self.individuals[fam.husb].name, self.individuals[fam.wife].name)]

        for indi in self.individuals.values():
            birthday=indi.birt
            deathDay=indi.deat
            if(birthday>datetime.datetime.now().date()):
                self.all_errors+=["US01: The birth of {} cannot occur after the current date.".format(indi.name)]
            if(deathDay != None and deathDay>datetime.datetime.now().date()):
                self.all_errors+=["US01: The death of {} cannot occur after the current date.".format(indi.name)]

    def indi_birth_before_marriage(self):
        """US02: Tests to ensure a married individual was not born after their marriage"""
        for fam in self.family.values():
            birth_husb = self.individuals[fam.husb].birt
            birth_wife = self.individuals[fam.wife].birt
            marr_date = fam.marr

            if(birth_husb>marr_date and birth_wife>marr_date):
                self.all_errors += ["US02: {}'s birth can not occur after their date of marriage".format(self.individuals[fam.husb].name)
                             + " and " + "{}'s birth can not occur after their date of marriage".format(self.individuals[fam.wife].name)]

            elif(birth_husb>marr_date):
                self.all_errors += ["US02: {}'s birth can not occur after their date of marriage".format(self.individuals[fam.husb].name)]
            elif(birth_wife>marr_date):
                self.all_errors += ["US02: {}'s birth can not occur after their date of marriage".format(self.individuals[fam.wife].name)]

    def birth_before_death(self):
        """US03: Tests to ensure that birth occurs before the death of an individual"""
        for person in self.individuals.values():
            if person.deat != None and self.date_difference(person.deat, person.birt) < 0:
                self.all_errors += ["US03: {}'s death can not occur before their date of birth".format(person.name)]

    def marr_before_div(self):
        """US04: Tests to ensure that marriage dates come before divorce dates"""
        for fam in self.family.values():
            if fam.div != None and self.date_difference(fam.div, fam.marr) < 0:
                self.all_errors += ["US04: {} and {}'s divorce can not occur before their date of marriage".format(self.individuals[fam.husb].name, self.individuals[fam.wife].name)]

    def marr_div_before_death(self):
        """US05 & US06: This tests to make sure that no one was married or divorced after they died"""
        for fam in self.family.values():
            deat_husb = self.individuals[fam.husb].deat
            deat_wife = self.individuals[fam.wife].deat
            marr_date, div_date = fam.marr, fam.div
            check_husb_m, check_husb_d, check_wife_d, check_wife_m = 1, 1, 1, 1 #Let the if else statements assign these their proper values
            if deat_husb == None and deat_wife == None:
                break          #We do not need to analyze further if both are alive
            elif div_date == None:      #We will now consider the case the two were still married when one/both spouse died
                if deat_husb != None:
                    check_husb_m = (deat_husb - marr_date).days
                else:
                    check_wife_m = (deat_wife - marr_date).days
            elif div_date != None:  #We will now consider they did divorce, we still have to check marriage again here
                if deat_husb != None:
                    check_husb_m = (deat_husb - marr_date).days
                    check_husb_d = (deat_husb - div_date).days
                else:
                    check_wife_m = (deat_wife - marr_date).days
                    check_wife_d = (deat_wife - div_date).days
            if check_husb_m < 0 or check_wife_m < 0 or check_husb_d < 0 or check_wife_d < 0:
                self.all_errors += ["US05 & US06: Either {} or {} were married or divorced after they died".format(self.individuals[fam.husb].name, self.individuals[fam.wife].name)]

    def normal_age(self):
        """US07: Checks to make sure that the person's age is less than 150 years old"""
        for individual in self.individuals.values():
            if individual.age == None:
                print(individual.name)
            if individual.age >= 150:
                self.all_errors += ["US07: {}'s age calculated ({}) is over 150 years old".format(individual.name, individual.age)]

    def birth_before_marriage(self):
        """US08: This checks to see if someone was born before the parents were married
            or 9 months after divorce"""
        for individual in self.individuals.values():
            birth_date = individual.birt #each individual birthday
            if individual.famc != None:
                marriage_date = self.family[individual.famc].marr #each family (that child is in) marraige date
                divorce_date = self.family[individual.famc].div #divorce date of parents
                if divorce_date != None:
                    diff_divorce_and_birth_date = (birth_date.year - divorce_date.year) * 12 + birth_date.month - divorce_date.month
                if (birth_date - marriage_date).days <= 0:
                    self.all_errors += ["US08: {} was born before their parents were married".format(individual.name)]
                elif divorce_date != None and diff_divorce_and_birth_date >= 9:
                    self.all_errors += ["US08: {} was born {} months after their parents were divorced".format(individual.name, diff_divorce_and_birth_date)]

    def brith_before_death_of_parents(self):
        "US09: Checks to see if someone was born before their parent died"
        for individual in self.individuals.values():
            birth_date = individual.birt #each individual birthday
            if individual.famc != None:
                fatherID = self.family[individual.famc].husb #father ID
                motherID = self.family[individual.famc].wife #mother ID
                father_death = self.individuals[fatherID].deat
                mother_death = self.individuals[motherID].deat
                if father_death != None:
                    father_difference = (birth_date.year - father_death.year) * 12 + birth_date.month - father_death.month
                    if father_difference >= 9:
                        self.all_errors += ["US09: {} was born {} months after father died".format(individual.name, father_difference)]
                if mother_death != None:
                    mother_difference = (birth_date - mother_death).days
                    if mother_difference >= 0:
                        self.all_errors += ["US09: {} was born after mother died".format(individual.name)]

    def spouses_too_young(self):
        """US10: Checks to make sure that each spouse of a family is older than 14 years old when
        they get married"""
        for individual in self.individuals.values():
            if len(individual.fams) > 0:
                for family in individual.fams:
                    marriage_date = self.family[family].marr
                    marriage_difference = marriage_date.year - individual.birt.year
                    if marriage_difference <= 14:
                        self.all_errors += ["US10: {} was only {} years old when they got married".format(individual.name, marriage_difference)]

    def no_bigamy(self):
        """US11: Tests to ensure marriage does not occur during marriage with someone else"""
        for fam in self.family.values():
            if len(self.individuals[fam.husb].fams) <= 1 and len(self.individuals[fam.husb].fams):
                continue           #If they are only a spouse in one family no need to continue, same for not being a spouse
            if len(self.individuals[fam.husb].fams) > 1:      #checks if husb is a bigamist
                count = 0
                for spouse in sorted(self.individuals[fam.husb].fams):   #want to ensure the set is ordered
                    curr_marr_date = self.family[spouse].marr
                    curr_div_date = self.family[spouse].div
                    if count == 0:
                        prev_marr_date = self.family[spouse].marr
                        prev_div_date = self.family[spouse].div
                        count += 1
                        continue
                    if prev_div_date == None:
                        self.add_errors_if_new("US11: {} is practing bigamy".format(self.individuals[fam.husb].name))
                    elif (curr_marr_date - prev_marr_date).days > 0 and (curr_marr_date - prev_div_date).days < 0:
                        self.add_errors_if_new("US11: {} is practing bigamy".format(self.individuals[fam.husb].name))
                    prev_marr_date = self.family[spouse].marr
                    prev_div_date = self.family[spouse].div
            if len(self.individuals[fam.wife].fams) > 1:       #checks if wife is a bigamist
                count = 0
                for spouse in sorted(self.individuals[fam.wife].fams):
                    curr_marr_date = self.family[spouse].marr
                    curr_div_date = self.family[spouse].div
                    if count == 0:
                        prev_marr_date = self.family[spouse].marr
                        prev_div_date = self.family[spouse].div
                        count += 1
                        continue
                    if prev_div_date == None:
                        self.add_errors_if_new("US11: {} is practing bigamy".format(self.individuals[fam.wife].name))
                    elif (curr_marr_date - prev_marr_date).days > 0 and (curr_marr_date - prev_div_date).days < 0:
                        self.add_errors_if_new("US11: {} is practing bigamy".format(self.individuals[fam.wife].name))
                    prev_marr_date = self.family[spouse].marr
                    prev_div_date = self.family[spouse].div

    def parents_too_old(self):
        """US12: This method tests to ensure that parents in a family are not too old.
        Mother should be less than 60 years older than children.
        Father should be less than 80 years older than children."""
        for indi in self.individuals.values():
            if indi.famc == None:                   #No need to continue if they are not a child
                continue
            if self.individuals[self.family[indi.famc].husb].age > (indi.age + 80): #check the father
                self.all_errors += ["US12: {} is over 80 years older than his child {}".format(self.individuals[self.family[indi.famc].husb].name, indi.name)]
            if self.individuals[self.family[indi.famc].wife].age > (indi.age + 60): #check the mother
                self.all_errors += ["US12: {} is over 60 years older than his child {}".format(self.individuals[self.family[indi.famc].wife].name, indi.name)]

    def sibling_spacing(self):
        """US13: Makes sure that birth dates of siblings should be more than 8 months apart
        or less than 2 days apart (twins may be born one day apart, e.g. 11:59 PM and 12:02 AM the following calendar day)"""
        for fam in self.family.values():
            childIDLstCopy = deepcopy(list(fam.chil))
            childIDLstCopy.sort() #needs to be sorted since every time the program runs, the order of the children set changes

            for i in range(len(childIDLstCopy)):
                for j in range(i + 1, len(childIDLstCopy)):
                    child1 = self.individuals[childIDLstCopy[i]]
                    child2 = self.individuals[childIDLstCopy[j]]
                    daysApart = abs(child1.birt - child2.birt).days
                    monthsApart = abs((child1.birt.year - child2.birt.year) * 12 + child1.birt.month - child2.birt.month)
                    if daysApart > 2 and monthsApart < 8 :
                        self.all_errors += ["US13: Siblings {} and {}'s births are ".format(child1.name, child2.name) + str(daysApart) + " days apart"]


    def too_many_births(self):
        """US14: Makes sure that no more than five siblings should be born at the same time"""
        for fam in self.family.values():
            childIDLstCopy = deepcopy(list(fam.chil))
            childIDLstCopy.sort() #needs to be sorted since every time the program runs, the order of the children set changes

            birthDayDict = {}
            for i in range(len(childIDLstCopy)):
                child = self.individuals[childIDLstCopy[i]]
                if child.birt not in birthDayDict:
                    birthDayDict[child.birt] = 1
                else:
                    birthDayDict[child.birt] = birthDayDict[child.birt] + 1
            for key in birthDayDict:
                if birthDayDict[key] > 5:
                    familyName = str(self.individuals[fam.husb].name).split()[-1]
                    self.all_errors += ["US14: The {} family has more than five children born at the same time".format(familyName)]


    def too_many_siblings(self):
        """US15: Tests to ensure that there are fewer than 15 siblings in a family"""
        for fam in self.family.values():
            if len(fam.chil)>=15:
                familyName = str(self.individuals[fam.husb].name).split()[-1]
                self.all_errors+=["US15: The {} family has 15 or more siblings".format(familyName)]

    def descendants_help(self, initial_indi, current_indi ):
        """Recursive helper for US17"""
        if(len(current_indi.fams)>0):
            for fam in current_indi.fams:
                if (self.individuals[self.family[fam].husb] == initial_indi or self.individuals[self.family[fam].wife] == initial_indi):
                    self.all_errors+=["US17: {} cannot be married to their descendant {}".format(initial_indi.name, current_indi.name)]
                for child in self.family[fam].chil:
                    self.descendants_help(initial_indi,self.individuals[child])

    def no_marriage_to_descendants(self):
        """US17: Tests to ensure that individuals and their descendants do not marry each other"""
        for person in self.individuals.values(): #Traverse all individuals and do a top down search of all descendants
            if(len(person.fams)>0):
                for fam in person.fams:
                    for child in self.family[fam].chil:
                        self.descendants_help(person,self.individuals[child])

    def no_marriage_to_siblings(self):
        """US18: Tests to ensure that individuals do not marry their siblings"""
        for person in self.individuals.values():
            if(len(person.fams)>0):
                for fam in person.fams:
                    tempHusb = self.family[fam].husb
                    tempWife = self.family[fam].wife
                    if(person.famc != None):
                        if(tempHusb in self.family[person.famc].chil and self.individuals[self.family[fam].husb] != person):
                            self.all_errors +=["US18: {} cannot be married to their sibling {}".format(person.name, self.individuals[self.family[fam].husb].name)]
                        elif(tempWife in self.family[person.famc].chil and self.individuals[self.family[fam].wife] != person):
                            self.all_errors +=["US18: {} cannot be married to their sibling {}".format(person.name, self.individuals[self.family[fam].wife].name)]
                            
    def no_marriage_to_cousin(self):
        """US19: Tests to ensure that individuals do not marry their first cousins"""
        couples = []
        for fam in self.family.values():
            mom = fam.wife
            dad = fam.husb
            for currIndi in fam.chil:
                if self.individuals[mom].famc != None:
                    for auntUncle in self.family[self.individuals[mom].famc].chil:    #mom's siblings
                        for cousin in self.get_childrenID(auntUncle):                   #cousin's on mom's side
                            if self.get_spouse(cousin) == currIndi and [currIndi,cousin] not in couples:
                                self.all_errors+=["US19: {} cannot be married to their cousin {}".format(self.individuals[currIndi].name, self.individuals[cousin].name)]
                                couples.append([cousin,currIndi])
                if self.individuals[dad].famc != None:
                    for auntUncle in self.family[self.individuals[dad].famc].chil:  #dad's siblings
                        for cousin in self.get_childrenID(auntUncle):               #cousins on dad's side
                            if self.get_spouse(cousin) == currIndi and [currIndi,cousin] not in couples:
                                self.all_errors+=["US19: {} cannot be married to their cousin {}".format(self.individuals[currIndi].name, self.individuals[cousin].name)]
                                couples.append( [cousin,currIndi])

    def get_childrenID(self, indi_ID):
        """returns a list of children IDs of the given individual ID"""
        childrenLst = []
        #an indivual can remarry and therefore have multiple families, hence the loop
        for family in self.individuals[indi_ID].fams:
            if len(self.family[family].chil) != 0:
                childrenLst += self.family[family].chil
        return childrenLst

    def get_spouse(self, indi_ID):
        """returns the current spouse of the given individual ID"""
        for family in self.individuals[indi_ID].fams:
            if self.family[family].div == None:
                if self.individuals[indi_ID].sex == "M":
                    return self.family[family].wife
                else:
                    return self.family[family].husb

    def creepy_aunts_and_uncles(self):
        """US20: Ensures that aunts and uncles should not marry their nieces or nephews"""
        #go through set of children from each family,
        # then go through children of each sibling to make sure they are not married to the other siblings
        for fam in self.family.values():
            siblingIDs = fam.chil #set of sibling IDs
            if len(siblingIDs) != 0: #if there are siblings
                for sib in siblingIDs: #string for the sibling ID
                    for child in self.get_childrenID(sib):
                        if self.get_spouse(child) in siblingIDs:
                            self.all_errors += ["US20: {} is married to their aunt or uncle".format(self.individuals[child].name)]



    def correct_gender_role(self):
        """US21: Husband in family should be male and wife in family should be female"""
        for fam in self.family.values():
            familyName = str(self.individuals[fam.husb].name).split()[-1].strip("/")
            husband = self.individuals[fam.husb]
            wife = self.individuals[fam.wife]
            if husband.sex == "F":
                self.all_errors += ["US21: The husband in the {} family, ({}), is a female!".format(familyName, husband.name)]
            if wife.sex == "M":
                self.all_errors += ["US21: The wife in the {} family, ({}), is a male!".format(familyName, wife.name)]


    def unique_names_and_bdays(self):
        """US23: Tests to ensure there are no individuals with the same name and birthdate"""
        names_and_bdays = []
        for person in self.individuals.values():
            if (person.name, person.birt) in names_and_bdays:
                self.all_errors += ["US23: An idividual with the name: {}, and birthday: {}, already exists!".format(person.name, person.birt)]
            else:
                names_and_bdays += [(person.name, person.birt)]

    def unique_spouses_in_family(self):
        """US24: Checks to see if only one family has spouses with the same names
            and marriage dates. Will indicate if there is more than one family with same spouses
            and marriage date"""
        unique_families = [] # input in the form (husband name, wife name, marriage date)
        for family in self.family.values():
            husb_name = self.individuals[family.husb].name
            wife_name = self.individuals[family.wife].name
            if (husb_name, wife_name, family.marr) in unique_families:
                self.all_errors += ["US24: The family with spouses {} and {} married on {} occurs more than once in the GEDCOM file.".format(husb_name, wife_name, family.marr)]
            else:
                unique_families += [(husb_name, wife_name, family.marr)]

    def unique_children_in_family(self):
        """US25: Checks to make sure that each child in a family has a unique name and birthdate"""
        for ID, family in self.family.items():
            unique_child_names = []
            for child in family.chil:
                child_name = self.individuals[child].name
                child_bday = self.individuals[child].birt
                if (child_name, child_bday) in unique_child_names:
                    self.all_errors += ["US25: There is more than one child with the name {} and birthdate {} in family {}".format(child_name, child_bday, ID)]
                else:
                    unique_child_names += [(child_name, child_bday)]

    def add_errors_if_new(self, error):
        """This method is here to add errors to the error list if they do not occur, in order to ensure no duplicates.
            Some user stories may flag duplicate errors and this method eliminates the issue."""
        if error not in self.all_errors:
            self.all_errors += [error]

    def print_errors(self):
        """After all error messages have been compiled into the list of errors the program prints them all out"""
        if len(self.all_errors) == 0:
            print("Congratulations this GEDCOM file has no known errors!")
        else:
            for error in sorted(self.all_errors):
                print(error)

def main():
    """This method runs the program"""
    cwd = os.path.dirname(os.path.abspath(__file__)) #gets directory of the file
    #file_name = cwd + r"\GEDCOM_FamilyTree.ged"
    file_name = cwd + r"\Bad_GEDCOM_test_data.ged"
    AnalyzeGEDCOM(file_name)

if __name__ == '__main__':
    main()
