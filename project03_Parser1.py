from prettytable import PrettyTable

validTags=["INDI","NAME","SEX","BIRT","DEAT","FAMC","FAMS","MARR","HUSB","WIFE","CHIL","DIV","DATE","HEAD","TRLR","NOTE"]

def parseArgs(line):
'''Parses the arguments from the line'''
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
'''Parses the level,tag, and arguments from the input line'''
    start,args=parseArgs(line)
    level,tag=start.split(" ")
    
    return level,tag,args
    

filename='/Users/Eamon/Desktop/myfamily.ged'  #update with your file path

input_file=open(filename, 'r')

indiDict={"":[]}
indi=""

for line in input_file:
    line=line.strip()
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
print(indiDict)

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
        if "DEAT" in line:
            print(key)
            alive=False
            level,tag,args=parseLine(indiDict[key][index+1])
            death=args
            
        
            
    table.add_row([indiDict[key][0],key,sex,birth,"age",alive,death,"",""])

        

print(table)