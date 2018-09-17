from prettytable import PrettyTable

validTags=["INDI","NAME","SEX","BIRT","DEAT","FAMC","FAMS","MARR","HUSB","WIFE","CHIL","DIV","DATE","HEAD","TRLR","NOTE"]

def parseArgs(line):
    '''helper function for parse line that parses the arguments out a line of a GED file'''
    count=0
    i=0
    for char in line:
        if count==2:
            return line[0:i-1],line[i:]
        if char==" ":
            count+=1
        i+=1
    return line[0:i],line[i:]

def parseLine(line):
    '''parses the level, tag, and args from a line from a GED file'''
    start,args=parseArgs(line)
    level,tag=start.split(" ")
    
    return level,tag,args

def getIndis(file):
    '''Makes a dictionary of all individuals and their information'''
    input_file=open(file, 'r')

    indiDict={"":[]}
    indi=""

    for line in input_file:
        line=line.strip()
        print(line)
        level,tag,args=parseLine(line)
    
        if args=="INDI":                #if the current line starts a new individual, begin a new key in the dictionary
            indiID=tag.replace("@",'') 
        
            line=input_file.readline()
            level,tag,args=parseLine(line)        
        
            indi=args
            indiDict[indi]=[indiID]
        
        if(args!="INDI"):                #add information to current individual's key
            indiDict[indi].append(line)
        
    indiDict.pop('')
    print()
    print(indiDict)
    print()
    return(indiDict)

def getFams(file):
    '''Makes a dictionary of families and their information (individual ids)'''
    return {} #put code here
    
def makeTable(indiDict,famDict):
    '''Makes a table of individuals and their information and relationships'''
    table=PrettyTable()
    table.field_names=["ID","Name","Gender","Birthday","Age","Alive","Death","Child","Spouse"]

    for key in indiDict:    #Loops thru individual dictionary and adds necessary info to table
        alive=True
        death="NA"
        for index, line in enumerate(indiDict[key]):
            if "SEX" in line:
                level,tag,args=parseLine(line) 
                sex=args
            if  "BIRT" in line:
                level,tag,args=parseLine(indiDict[key][index+1])
                birth=args
                #use date/time function to get age
            if "DEAT" in line:
                alive=False
                level,tag,args=parseLine(indiDict[key][index+1])
                death=args
        
        table.add_row([indiDict[key][0],key,sex,birth,"age",alive,death,"",""])
    
    for key in famDict:     #loops through family dictionary and adds spouse and child information to table
        pass
            
        table.add_row([indiDict[key][0],key,sex,birth,"age",alive,death,"",""])
        
    print(table)
    

def main():
    
    filename='/Users/Eamon/Desktop/myfamily.ged'
    indisDict=getIndis(filename)
    famsDict=getFams(filename)
    
    makeTable(indisDict,famsDict) 

if __name__ == '__main__':
    main()
