# Athanasios Roudis 5098 , Stylianos Simantirakis 5127
import argparse

def lex():
    commandList = ["main", "def", "global", "if", "else", "elif", "while", "print", "return", "input", "and", "or", "not","int"]
    global f
    global line
    token = "start"
    word = ""
    number = ""
    state = 0
    while token != "":
        token = f.read(1)
      #  #print("reading",token)
        if state == 0:
            if token == "\n":
                line += 1
            if token == " " or token == "\n" or token == "\r" or token == "\t" or token == "\v" or token == "":
                state = 0
            elif token.isalpha():
                word = token
                state = 1
            elif token.isdigit():
                number = token
                state = 2
            elif token == "=":
                state = 3
            elif token == "<":
                state = 4
            elif token == ">":
                state = 5
            elif token == "!":
                state = 6
            elif token == "#":
                state = 7
            elif token == "+":
                return (["addtoken",line])
            elif token == "-":
                return (["subtoken",line])
            elif token == "*":
                return (["multoken",line])
            elif token == "/":
                state = 14
            elif token == "%":
                return (["modtoken",line])
            elif token == ",":
                return (["commatoken",line])
            elif token == ":":
                return (["anwkatwtoken",line])
            elif token == ")":
                return (["rightpartoken",line])
            elif token == "(":
                return (["leftpartoken",line])
            else:
                print("Invalid character:", token, "at line", line)
                break
            continue         
        if state==3:
            if token == '=':
                return (["isothtatoken",line])
            else:
                f.seek(f.tell() - 1)
                return (["ana8eshtoken",line])
        if state==4:
            if token == '=':
                return (["mikisotoken",line])
            else:
                f.seek(f.tell() - 1)
                return (["mikroterotoken",line])  
        if state==5:
            if token == '=':
                return (["megisotoken",line])
            else:
                f.seek(f.tell() - 1)
                return (["megaluterotoken",line])
        if state==6:
            if token == '=':
                return (["diaforotoken",line])
            else:
                print("Invalid character, expected '=' after '!' not :", token, "at line", line)
                break             
        if state == 7:
            if token == '#':
                state = 8
            elif token == "{":
                return (["anoigmatoken",line])
            elif token == "}":
                return (["kleisimotoken",line])
            elif token == "i":
                state = 9
            elif token == "d":
                state = 10
            else:
                print("Invalid character ", token, "is not expected after a '#' at line", line)
                break
            continue                  
        if state == 8:
            if token == '#':
                state = 13
            continue
        if state == 9:
            if token == "n":
                state = 11
            else:
                print("Invalid character i"+token, "is not expected after a '#' at line", line) 
                break
            continue
        if state == 10:
            if token == "e":
                state = 12
            else:
                print("Invalid character d"+token, "is not expected after a '#' at line", line)
                break
            continue      
        if state == 11:
            if token == "t":
                return (["intdeftoken",line])
            else:
                print("Invalid character in"+token, "is not expected after a '#' at line", line)
                break                  
        if state == 12:
            if token == "f":
                return (["defitoken",line])
            else:
                print("Invalid character de"+token, "is not expected after a '#' at line", line)
                break         
        if state == 13:
            if token == "#":
                state = 0
            else:
                state = 8
            continue
        if state == 14:
            if token == '/':
                return (["divtoken",line])
            else:
                print("Invalid character, expected '/' after '/' not : ", token, "at line", line)
                break
        if state == 1:
            tepIndex = f.tell() -1
            while token.isalpha() or token.isdigit():
                word += token
                tepIndex = f.tell()
                token = f.read(1)
            f.seek(tepIndex)
            if word in commandList:
                return(["commandtoken", line, word])
            else:
                if len(word)<=30:
                    return(["anagnoristikotoken", line, word])
                else:
                    print("At line ",line, "the number of letters has passed the limit of 30 letters")
                    print("Compilation fails")
                    exit()
        if state == 2 :           
            while token.isdigit():
                number+=token
                token = f.read(1)
            f.seek(f.tell() -1)
            if int(number)>=-32767  and int(number)<=32767 :
                return (["numbertoken", line, int(number)])
            else:
                print("At line ",line,"number out of the limits of -32767 and 32767")
                print("Compilation fails")
                exit()
    return (["EOFtoken",line])        

def syntax():
    global isAtLeastOneStatement
    global isAtLeastOneDeclaration
    global isAtLeastOneGlobal
    global isAtLeastOneID
    global isAtLeastOnePar
    global seekIndex
    global quadList

    def ifState(token):
        global seekIndex
        if token[0] == "commandtoken":
            if token[2] == "if" or token[2] == "elif":
                token = lex()
                if isCondition(token):
                    conditionTrue = []
                    conditionFalse = []
                    conditionTrue = backpatch(conditionTrue, nextQuad())
                    token = lex()
                    if token[0] == "anwkatwtoken":
                        token = lex()
                        if isStatement(token):
                            ifList = makeList(nextQuad())
                            quadList.append(genQuad("jump","_","_","_"))
                            conditionFalse = backpatch(conditionFalse, nextQuad())
                            seekIndex = f.tell()
                            token = lex()
                            if token[0] == "commandtoken":
                                if token[2] == "elif":
                                    ifList = backpatch(ifList,nextQuad())
                                    return ifState(token)
                                elif token[2] == "else":
                                    ifList = backpatch(ifList,nextQuad())
                                    return elseState(token)
                                else:
                                    ifList = backpatch(ifList,nextQuad())
                                    f.seek(seekIndex) 
                                    return True
                            else:
                                f.seek(seekIndex)
                                return True
                        else:
                            print ("Inside the 'if' at line:", token[1], "a statement was expected")
                            return False
                    else:
                        print ("After the 'if' at line:", token[1], "a ':' was expected")
                        return False
                else:
                    print ("After the 'if' at line:", token[1], "a condition was expected")
                    return False

    def elseState(token):
        if token[2] == "else":
            token = lex()
            if token[0] == "anwkatwtoken":
                    token = lex()
                    if isStatement(token):
                        return True
                    else:
                        print ("Inside the 'else' at line:", token[1], "a statement was expected")
                        return False
            else:
                    print ("After the 'else' at line:", token[1], "a ':' was expected")
                    return False

    def isCondition(token):
        Btrue = []
        Bfalse = []
        global seekIndex
        if isBoolTerm(token):
            Q1true = []
            Q1false = []
            Btrue = Q1true
            Bfalse = Q1false
            seekIndex = f.tell()
            token = lex()
            if token[0] == "commandtoken":
                while token[2]=="or":
                    Bfalse = backpatch(Bfalse,nextQuad())
                    seekIndex = f.tell()
                    token = lex()
                    if isBoolTerm(token) == False:
                        print("After the 'or' at line:", token[1], "a boolean term was expected")
                        return False
                    else:
                        Q2true = []
                        Q2false = []
                        Btrue = mergeList(Btrue,Q2true)
                        Bfalse = Q2false
                        f.seek(seekIndex)
                return True
            else:
                f.seek(seekIndex)
                return True
        else:
            print("At line:", token[1],"a boolean term was expected")
            return False        
    
    def isBoolTerm(token):
        Qtrue = []
        Qfalse = []
        global seekIndex
        if isBoolFactor(token):
            R1true = []
            R1false = []
            Qtrue = R1true
            Qfalse = R1false
            seekIndex = f.tell()
            token = lex()
            if token[0] == "commandtoken":
                while token[2]=="and":
                    Qtrue = backpatch(Qtrue,nextQuad())
                    seekIndex = f.tell()
                    token = lex()
                    if isBoolFactor(token):
                        R2true = []
                        R2false = []
                        Qfalse = mergeList(Qfalse,R2false)
                        Qtrue = R2true
                        seekIndex = f.tell()
                        token = lex()
                        if token[0]!= "commandtoken":
                            break
                    else:
                        print("After the 'and' at line:", token[1], "a boolean factor was expected")
                        return False
                f.seek(seekIndex)
                return True
            else:
                f.seek(seekIndex)
                return True
        else:
            print("At line:", token[1],"a boolean factor was expected")
            return False               

    def isBoolFactor(token):
        Rtrue = []
        Rfalse = []
        if token[0] == "commandtoken":
            if token[2] == "not":
                token = lex()
                if isCondition(token):
                    Btrue = []
                    Bfalse = []
                    Rtrue = Bfalse
                    Rfalse = Btrue
                    return True
                else:
                    print("At line:", token[1],"a boolean factor was expected after 'not")
                    return False
            elif isExpression(token):
                E1place = 1 #pairnei ti timi apo to Expression
                token = lex()
                if token[0] in relOpList:
                    relOp = token[0]
                    token = lex()
                    if isExpression(token):
                        E2place = 2 #pairnei ti timi apo to Expression
                        Rtrue = makeList(nextQuad())
                        quadList.append(genQuad(relOp, E1place,E2place,"_"))
                        Rfalse = makeList(nextQuad())
                        quadList.append(genQuad("jump","_","_","_"))
                        return True
                    else:
                        print("At line", token[1], "an expression was expected after a relationship opperand")
                        return False
            else:
                return False
        elif isExpression(token):
            token = lex()
            if token[0] in relOpList:
                token = lex()
                if isExpression(token):
                    return True
                else:
                    print("At line", token[1], "an expression was expected after a relationship opperand")
                    return False
            else:
                print("At line", token[1], "a relationship opperand was expected")
                return False
        elif isCondition(token):
            Btrue = []
            Bfalse = []
            Rtrue = Btrue
            Rfalse = Bfalse
            return True
        else:
            return False
            

    def isExpression(token):
        Eplace = 0
        global seekIndex
        seekIndex = f.tell()
        if isOptionalSign(token):
            token = lex()       
        if isTerm(token):
            T1place = 1
            seekIndex = f.tell()
            token = lex()
            while token[0] == "addtoken" or token[0] == "subtoken":
                operand = token[0]
                token = lex()
                if isTerm(token):
                    T2place = 2
                    w = newTemp()
                    quadList.append(genQuad(operand,T1place,T2place,w))
                    T1place = w
                    seekIndex = f.tell()
                    token = lex()
                else:
                    print("At line", token[1], "a term was expected after an add or sub opperand. Instead found:", token[0])
                    return False
            f.seek(seekIndex)
            Eplace = T1place
            return True
        else:
            f.seek(seekIndex)      
            return False
    
    def isOptionalSign(token):
        global seekIndex       
        if token[0] == "addtoken" or token[0] == "subtoken":
            return True
        else:
            return False
   
    def isTerm(token):
        Tplace = 0
        global seekIndex
        if isFactor(token):
            F1place = 1
            seekIndex = f.tell()
            token = lex()
            while token[0] == "multoken" or token[0] == "modtoken" or token[0] == "divtoken":
                operand = token[0]
                token = lex()
                if isFactor(token):
                    F2place = 2
                    w = newTemp()
                    quadList.append(genQuad(operand,F1place,F2place))
                    F1place = w
                    seekIndex = f.tell()
                    token = lex()
                else:
                    print("At line", token[1], "a factor was expected after a multiplication or division opperand. Instead found: ",token[0])
                    return False
            f.seek(seekIndex)
            Tplace = F1place
            return True
        else:
            return False
        
    def isFactor(token):
        Fplace = 0
        global seekIndex
        if token[0] == "numbertoken":
            Fplace = token[2]
            return True        
        elif token[0] == "anagnoristikotoken":
            seekIndex = f.tell()
            tempSeekIndex = seekIndex
            if functionCall(token):
                return True
            else:
                f.seek(tempSeekIndex)
            token = lex()
            if idTail(token):
                return True
            else:
                IDplace = 1
                Fplace = IDplace
                f.seek(tempSeekIndex)
                return True       
        elif token[0] == "leftpartoken":
            token = lex()
            if isExpression(token):
                Eplace = 2
                Fplace = Eplace
                token = lex()
                if token[0] == "rightpartoken":
                    return True
                else:
                    print("At line", token[1], "a ')' was expected")
                    return False
            else:
                print("At line", token[1], "an expression was expected")
                return False          
        else:
            return False          

    def idTail(token):
        if parList(token):
            return True
        else:
            return False

    def parList(token):
        global seekIndex
        global isAtLeastOnePar
        if isExpression(token):
            isAtLeastOnePar = True
            seekIndex = f.tell()
            token=lex()
            while token[0] == "commatoken":
                seekIndex = f.tell()
                token = lex()
                if parList(token):
                    seekIndex = f.tell()
                    token=lex()
                    continue
                else:
                    print("At line", token[1], "an expression was expected after the ','")
                    return False
            f.seek(seekIndex)
            return isAtLeastOnePar
        else:
            f.seek(seekIndex)
            return False
        
    def isStatement(token):
        if isSimpleStatement(token):
            return True
        elif isStructuredStatement(token):
            return True
        else:
            return False

    def isSimpleStatement(token):
        if isAssignmentStat(token):
            return True
        elif isPrintStat(token):
            return True
        elif isReturnStat(token):
            return True
        else:
            return False
        
    def isAssignmentStat(token):
        if token[0] == "anagnoristikotoken":
            token = lex()
            if token[0] == "ana8eshtoken":
                token = lex()               
                if isExpression(token):
                    return True
                elif token[0] == "commandtoken":
                    if token[2] == "int":
                        token = lex()
                        if token[0] == "leftpartoken":
                            token = lex()
                            if token[0] == "commandtoken":
                                if token[2] == "input":
                                    token = lex()
                                    if token[0] == "leftpartoken":
                                        token = lex()
                                        if token[0] == "rightpartoken":
                                            token = lex()
                                            if token[0] == "rightpartoken":
                                                return True
                                            else:
                                                print("At line", token[1], "a ')' was expected")
                                                return False
                                        else:
                                            print("At line", token[1], "a ')' was expected")
                                            return False
                                    else:
                                        print("At line", token[1], "a '(' was expected")
                                        return False
                                else:
                                    return False
                            else:
                                return False
                        else:
                            print("At line", token[1], "a '(' was expected")
                            return False
                    else:
                        return False
                else:
                    print("At line", token[1], "either an expression or 'int(input()) was expected after the '='")
                    return False
            else:
                return False
        else:
            return False           
    
    def isReturnStat(token):
        if token[0] == "commandtoken":
            if token[2] == "return":
                token = lex()
                if isExpression(token):
                    return True
                else:
                    print("At line", token[1], "an expression was expected after the 'return' command")
                    return False
            else:
                return False
        else:
            return False
            
    def isStructuredStatement(token):
        if ifState(token):
            return True
        elif whileState(token):
            return True
        else:
            return False
        
    def whileState(token):
        if token[0] == "commandtoken":
            if token[2] == "while":
                condQuad = nextQuad()
                token = lex()
                if isCondition(token):
                    conditionTrue = []
                    conditionFalse = []
                    conditionTrue = backpatch(conditionTrue, nextQuad())
                    token = lex()
                    if token[0] == "anwkatwtoken":
                        token = lex()
                        if token[0] == "anoigmatoken":
                            token = lex()
                            if statements(token):
                                token = lex()
                                if token[0] == "kleisimotoken":
                                    quadList.append(genQuad("jumb","_","_",condQuad))
                                    conditionFalse = backpatch(conditionFalse,nextQuad())
                                    return True
                                else:
                                    print("At line", token[1] ,"a '#}' was expected to close a '#{ found earlier for the while loop")
                                    return False
                            else:
                                print("At line", token[1], "a statement was expected after the ':'")
                                return False
                        else: 
                            print("At line", token[1], "a '#{' was expected after the 'while'")
                            return False
                    else:
                        print("At line", token[1], "a ':' was expected")
                        return False
                else:
                    print("At line", token[1], "a condition was expected after the 'while' command")
                    return False
            else:
                return False
        else:
            return False
        
    def startRule():
        token=lex()
        if declarations(token):
            token=lex()            
            while isDefFunctions(token):
                token=lex()
            if callMainPart(token):
                return True
            else:
                exit()
        else:
            print("At line", token[1]," declarations was expected")
            exit()

    def isPrintStat(token):
        if token[0] == "commandtoken":
            if token[2] == "print":
                token = lex()
                if token[0] == "leftpartoken":
                    token = lex()
                    if isExpression(token):
                        token = lex()
                        if token[0] == "rightpartoken":
                            return True
                        else:
                            ("At line", token[1]," a ')' was expected")
                            return False
                    elif functionCall(token):
                        token = lex()
                        if token[0] == "rightpartoken":
                            return True  
                        else:
                            ("At line", token[1]," a ')' was expected")
                            return False     
                    else:
                        print("At line", token[1], "an expression or a call function was expected after the 'print' command")
                        return False
                else:
                    ("At line", token[1]," a '(' was expected after the 'print' command")
                    return False
            else:
                return False
        else:
            return False
            
    def isIdList(token):
        global seekIndex
        global isAtLeastOneID
        if token[0]=="anagnoristikotoken":
            isAtLeastOneID = True
            seekIndex = f.tell()
            token=lex()
            if token[0]=="commatoken":
                token=lex()
                res = isIdList(token)
                f.seek(seekIndex)
                return res            
            else:
                f.seek(seekIndex)    
                return isAtLeastOneID
        else:
            f.seek(seekIndex)
            return False
    
    def functionCall(token):
        if token[0]=="anagnoristikotoken":
            token=lex()
            if token[0]=="leftpartoken":
                token=lex()
                if idTail(token):
                    token=lex()
                    if token[0]=="rightpartoken":
                        return True
                    else:
                        print("At line", token[1], "a ) was expected ")
                        return False
                else:
                    if token[0]=="rightpartoken":
                        return True
                    else:
                        print("At line", token[1], "a ) was expected ")
                        return False
            else:
                return False
        else:
            return False
        
    def statements(token):
        global seekIndex
        global isAtLeastOneStatement
        seekIndex = f.tell()
        if isStatement(token) == False:
            f.seek(seekIndex)
            return False
        seekIndex = f.tell()
        token = lex()
        while isStatement(token):
            seekIndex = f.tell()  
            token=lex()
        f.seek(seekIndex)
        return True
    
    def declarations(token):
        global seekIndex
        global isAtLeastOneDeclaration      
        seekIndex = f.tell()  
        isAtLeastOneDeclaration = isDeclaration(token)
        token=lex()
        while isDeclaration(token) and isAtLeastOneDeclaration:
            seekIndex = f.tell()
            token = lex()
        f.seek(seekIndex)        
        return isAtLeastOneDeclaration
    
    def globalVar(token):
        global seekIndex
        global isAtLeastOneGlobal  
        seekIndex = f.tell()   
        isAtLeastOneGlobal = isGlobal(token)
        token=lex()   
        while isGlobal(token):
            seekIndex = f.tell()  
            token=lex()
        f.seek(seekIndex)                 
        return isAtLeastOneGlobal
    
    def isDeclaration(token):          
        if token[0]=="intdeftoken":
            token=lex()
            if isIdList(token):              
                return True
            else:
                print("At line", token[1], "an id was expected ")
                return False
        else:
            return False
    
    def isGlobal(token):          
        if token[0]=="commandtoken":
            if token[2]=="global":
                token=lex()
                if isIdList(token):
                    return True
                else:
                    print("At line", token[1], "an id was expected ")
                    return False
            else:
                return False
        else:
            return False
        
    def isDefFunctions(token):
        if token[0] == "commandtoken":
            if token[2] == "def":
                token=lex()
                if token[0] == "anagnoristikotoken":
                    token=lex()
                    if token[0] == "leftpartoken":
                        token = lex()
                        if isIdList(token):
                            token=lex()
                            if token[0] == "rightpartoken":
                                token = lex()
                                if token[0] == "anwkatwtoken":
                                    token = lex()
                                    if token[0] == "anoigmatoken":
                                        token = lex()
                                        if declarations(token):
                                            token = lex()
                                        while globalVar(token) == False:
                                            if isDefFunctions(token):
                                                token = lex()
                                                continue
                                            else:
                                                print ("At line", token[1], "a global was expected")
                                                exit()
                                        token = lex()
                                        if statements(token):
                                            token = lex()
                                            if token[0] == "kleisimotoken":
                                                return True
                                            else:
                                                print ("At line", token[1], "a '#}' was expected to close a '#{ found earlier")
                                                exit()
                                        else:
                                            print ("At line", token[1], "a statement was expected")
                                            exit()
                                    else:
                                        print ("At line", token[1], "a '#{' was expected")
                                        exit()
                                else:
                                    print ("At line", token[1], "a ':' was expected")
                                    exit()
                            else:
                                print ("At line", token[1], "a ')' was expected")
                                exit()
                        else:
                            print ("At line", token[1], "an id was expected")
                            exit()
                    else:
                        print ("At line", token[1], "a '(' was expected")
                        exit()
                else:
                    print ("At line", token[1], "an id was expected")
                    exit()
            else:
                return False
        else:
            return False

        
    def callMainPart(token):
        if token[0] == "defitoken":
            token = lex()
            if token[0] == "commandtoken":
                if token[2] == "main":
                    token=lex()
                    if declarations(token):
                        token=lex()
                    if statements(token):      
                            return True
                    else:
                        print ("At line", token[1], "a statement was expected")
                        exit()
                else:
                    exit()
            else:
                exit()
        else:
            return False


    def nextQuad():
        global quadNum
        quadNum += 1
        return quadNum

    def genQuad(op,x,y,z):
        quad = [op,x,y,z]
        return quad

    def newTemp():
        global tempNum
        tempNum += 1
        s = "T_"
        return s+tempNum

    def emptyList():
        return ["_","_","_","_"]

    def makeList(label):
        return [label]

    def mergeList(list1,list2):
        return list1+list2

    def backpatch(list,label):
        for x in list:
            x[-1] = label
        return list


    relOpList=["isothtatoken","mikroterotoken","megaluterotoken","mikisotoken","megisotoken","diaforotoken"]
    seekIndex = f.tell()

    


    return startRule()


isAtLeastOneStatement = False
isAtLeastOneDeclaration = False
isAtLeastOneGlobal = False
isAtLeastOneID = False
isAtLeastOnePar = False
line = 0
quadNum = -1
tempNum = -1
quadList = []

#Gia to diabasma apo ta arguments
parser = argparse.ArgumentParser(description='Compile a file.')
parser.add_argument('input_file', help='Path to the input file')

args = parser.parse_args()

fileToCompile = args.input_file

try:
    f = open(fileToCompile)   
except Exception as e:
    print(e)

syntax = syntax()
if syntax:
    print('Compilation is completed')
else:
    print('Compilation failed')
