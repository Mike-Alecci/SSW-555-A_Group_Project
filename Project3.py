from prettytable import PrettyTable
import datetime
from collections import defaultdict
import os

class AnalyzeGEDCOM:
    """This class analyzes the GEDCOM file and sorts information into the family and individual classes respectively for analysis"""
    def __init__(self, file_name, create_tables = True):
        self.file_name = file_name
        self.family = dict()        #dictionary with Key = FamID Value = Family class object
        self.individuals = dict()   #dictionary with Key = IndiID Value = Individual class object
        self.fam_table = PrettyTable(field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
        self.indi_table = PrettyTable(field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"])
        self.analyze()
        if create_tables:           #allows to easily toggle the print of the pretty table on and off
            self.create_pretty_tables()

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
                self.individuals[indiv] = Individual()                      #The instance of a Individual class object is created
                continue
            elif line[0] == '0' and line[2] == "FAM":                       
                current_type = 2                                            #Marker used to ensure following lines are analyzed as family
                fam = line[1].replace("@", "")
                self.family[fam] = Family()                                 #The instance of a Family class object is created
                continue
            if current_type in [1,2]:                                       #No new Individual or Family was created, analyze line further
                self.analyze_info(line, previous_line, indiv, fam, current_type)
            previous_line = line
            

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
            ind.update_info()                       #Assigns alive, and age
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
        self.marr = "NA" #date of marriage
        self.div = "NA" #date of divorce
        self.husb = "NA" #husband ID
        self.wife = "NA" #wife ID
        self.chil = set() #set of children


class Individual:
    """This class stores all the pertinent information about an individual"""
    def __init__(self):
        """This captures all the relevant information for an individual, it also instantiates null values in case information is incomplete"""
        self.name = "NA"
        self.sex = "NA"
        self.birt = None
        self.age = "NA"
        self.alive = True
        self.deat = None
        self.famc = "NA"
        self.fams = set()

    def update_info(self):
        """Checks to see if INDI is dead, and finds their age"""
        self.alive = (self.deat == None)
        try:
            if(self.alive):
                self.age = (datetime.datetime.today().year - self.birt.year)
            else:
                self.age = (self.deat.year - self.birt.year)
        except TypeError:
            raise TypeError("Improper records of birth/death")

def main():
    """This method runs the program"""
    cwd = os.path.dirname(os.path.abspath(__file__)) #gets directory of the file
    file_name = cwd + "\GEDCOM_FamilyTree.ged"
    AnalyzeGEDCOM(file_name)


if __name__ == '__main__':
    main()