# Athanasios Roudis 5098 , Stylianos Simantirakis 5127
import argparse

class Final:
    def __init__(self, record_structure):
        self.record_structure = record_structure
        self.instructions = []

    def gnlvcode(self, var_name, reg):
        entity = self.record_structure.searchEntity(var_name)[0]
        entity_level = self.record_structure.searchEntity(var_name)[1]
        if entity is None:
            print (var_name,"has not been initialized")
            print("Running has failed")
            exit()
        current_level = len(self.record_structure.scopes)
        levels_up = current_level - entity_level
        if levels_up > 0:
            self.instructions.append(f"\tlw {reg}, -4(sp)")  
        for _ in range(1, levels_up):
            self.instructions.append(f"\tlw {reg}, -4({reg})")  
        self.instructions.append(f"\taddi {reg}, {reg}, {entity.offset}")

    def loadvr(self, v, reg):
        def increment_reg(reg):
            prefix = reg[0]  
            num = int(reg[1:])  
            return f"{prefix}{num + 1}"

        if str(v).isnumeric():
            self.instructions.append(f"\tli {reg}, {v}")
            return

        entity_level = self.record_structure.searchEntity(v)[1]
        entity = self.record_structure.searchEntity(v)[0]
        if  entity is None:
            print (v,"has not been initialized")
            print("Running has failed")
            exit()

        current_level = len(self.record_structure.scopes)

        if entity_level == 1:  
            self.instructions.append(f"\tlw {reg}, -{entity.offset}(gp)")
        elif entity_level == current_level: 
            if isinstance(entity, RecordStructure.Variable) or isinstance(entity, RecordStructure.TemporaryVariable):
                self.instructions.append(f"\tlw {reg}, -{entity.offset}(sp)")
            elif isinstance(entity, RecordStructure.RecordArgument) and entity.parMode == "CV":
                self.instructions.append(f"\tlw {reg}, -{entity.offset}(sp)")
                self.instructions.append(f"\tlw {reg}, 0({reg})")
                next_reg = increment_reg(reg)
                self.instructions.append(f"\tlw {next_reg}, 0({reg})")
        elif entity_level < current_level:  
            self.gnlvcode(v, reg)
            self.instructions.append(f"\tlw {reg}, 0({reg})")
            next_reg = increment_reg(reg)
            self.instructions.append(f"\tlw {next_reg}, 0({reg})")

    def storerv(self, v, reg):
        entity_level = self.record_structure.searchEntity(v)[1]
        entity = self.record_structure.searchEntity(v)[0]
        if  entity is None:
            print (v,"has not been initialized")
            print("Running has failed")
            exit()

        current_level = len(self.record_structure.scopes)
        if entity_level == current_level:  
            self.instructions.append(f"\tsw {reg}, -{entity.offset}(sp)")
        elif entity_level < current_level:  
            if isinstance(entity_level, RecordStructure.RecordArgument) and entity.parMode == "CV":
                self.gnlvcode(v, reg)
                self.instructions.append(f"\tsw {reg}, 0({reg})")
        elif entity_level == 1:  
            self.instructions.append(f"\tsw {reg}, -{entity.offset}(gp)")

    def end(self):
        self.instructions.append("\tli a0, 0")
        self.instructions.append("\tli a7, 93")
        self.instructions.append("\tecall")
    
    def callFun(self, funName):
        self.instructions.append(f"\tjal ra, {funName}")
    
    def retToCaller(self):
        self.instructions.append(f"\tlw ra,0(sp)")
        self.instructions.append("\tjr ra")
        
    def jump(self, jumpName):
        self.instructions.append(f"\tj {jumpName}")
    
    def label(self, labelName):
        self.instructions.append(f"{labelName}:")
    
    def move(self, r1, r2):
        self.instructions.append(f"\tmv {r1}, {r2}")
    
    def operations(self, r1, r2, r3, op):
        if op == "+":
            self.instructions.append(f"\tadd {r1}, {r2}, {r3}")
        elif op == "-":
            self.instructions.append(f"\tsub {r1}, {r2}, {r3}")
        elif op == "*":
            self.instructions.append(f"\tmul {r1}, {r2}, {r3}")
        elif op == "/":
            self.instructions.append(f"\tdiv {r1}, {r2}, {r3}")
        elif op == "not":
            self.instructions.append(f"\tnot {r1}, {r2}")
        elif op == "or":
            self.instructions.append(f"\tor {r1}, {r2}")
        elif op == "and":
            self.instructions.append(f"\tand {r1}, {r2}")

    def branch(self, r1, r2, label, con):
        if con == "==":
            self.instructions.append(f"\tbeq {r1}, {r2}, {label}")
        elif con == "!=":
            self.instructions.append(f"\tbne {r1}, {r2}, {label}")
        elif con == ">=":
            self.instructions.append(f"\tblt {r1}, {r2}, {label}")
        elif con == "<":
            self.instructions.append(f"\tbge {r1}, {r2}, {label}")
                    
    def write_instructions(self,s):
        for instr in self.instructions:
            s+=(instr + "\n")
        self.instructions = [] 
        return s

class RecordStructure:
    def __init__(self):
        self.scopes = []

    class RecordScope:
        def __init__(self, entityList, nestingLevel):
            self.entityList = entityList
            self.nestingLevel = nestingLevel

    class RecordEntity:
        def __init__(self, name):
            self.name = name

    class Variable(RecordEntity):
        def __init__(self, name,  offset):
            super().__init__(name)
            self.offset = offset

    class Function(RecordEntity):
        def __init__(self, name,  framelength,arguments):
            super().__init__(name)
            self.framelength = framelength
            self.arguments = arguments

    class TemporaryVariable(RecordEntity):
        def __init__(self, name, offset):
            super().__init__(name)
            self.offset = offset

    class RecordArgument:
        def __init__(self, parMode):
            self.parMode = parMode
            
    def addNewScope(self):
        newScope = RecordStructure.RecordScope(entityList=[], nestingLevel=len(self.scopes) + 1)
        self.scopes.append(newScope)
        return newScope

    def scopeDeletion(self, scopeIndex):
        if scopeIndex < len(self.scopes):
            self.scopes.pop(scopeIndex)


    def addNewEntity(self, scopeIndex, entityName, entity_type, **kwargs):
        if scopeIndex < len(self.scopes):
            if entity_type == 'Variable':
                newEntity = RecordStructure.Variable(name=entityName, **kwargs)
            elif entity_type == 'Function':
                newEntity = RecordStructure.Function(name=entityName, **kwargs)
            elif entity_type == 'TemporaryVariable':
                newEntity = RecordStructure.TemporaryVariable(name=entityName, **kwargs)
            else:
                return None
            self.scopes[scopeIndex].entityList.append(newEntity)
            return newEntity

    def addNewArgument(self, scopeIndex, entityIndex, argumentName, parMode, type):
        if scopeIndex < len(self.scopes) and entityIndex < len(self.scopes[scopeIndex].entityList):
            newArgument = RecordStructure.RecordArgument(parMode=parMode, type=type)
            if not hasattr(self.scopes[scopeIndex].entityList[entityIndex], "arguments"):
                self.scopes[scopeIndex].entityList[entityIndex].arguments = []
            self.scopes[scopeIndex].entityList[entityIndex].arguments.append(newArgument)
            return newArgument

    def searchEntity(self, entityName):
        for scope in self.scopes:
            for entity in scope.entityList:
                if entity.name == entityName:
                    return [entity,scope.nestingLevel]
        return None,None
    
    def printScopesToFile(self, filename="cpy.sym"):
        with open(filename, "w") as file:
            file.write("---------------------------------SYMBOL TABLE---------------------------------\n")
            for i, scope in enumerate(self.scopes, start=1):
                file.write(f"Scope {i-1}:\n")
                file.write("Entities:\n")
                for j, entity in enumerate(scope.entityList, start=1):
                    file.write(f"\tEntity {j}:\n")
                    file.write(f"\tName: {entity.name},")
                    if isinstance(entity, self.Variable):
                        file.write(f"\tOffset: {entity.offset}\n")
                    elif isinstance(entity, self.Function):
                        file.write(f"\tFrame Length: {entity.framelength},")
                        file.write(f"\tArguments:{entity.arguments}\n")
                        
                    elif isinstance(entity, self.TemporaryVariable):
                        file.write(f"\tOffset: {entity.offset}\n")
                file.write("\n")

def lex():
    commandList = ["main", "def", "global", "if", "else", "elif", "while", "print", "return", "input", "and", "or", "not","int"]
    global f
    global line
    global latestNewLine
    token = "start"
    word = ""
    number = ""
    state = 0
    while token != "":
        token = f.read(1)
        if state == 0:
            if token == "\n" and f.tell() > latestNewLine and f.tell() < 10000:
                latestNewLine = f.tell()
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
                print("Compilation failed")
                exit()
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
                print("Compilation failed")
                exit()             
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
                print("Compilation failed")
                exit()
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
                print("Compilation failed")
                break
            continue
        if state == 10:
            if token == "e":
                state = 12
            else:
                print("Invalid character d"+token, "is not expected after a '#' at line", line)
                print("Compilation failed")
                exit()
            continue      
        if state == 11:
            if token == "t":
                return (["intdeftoken",line])
            else:
                print("Invalid character in"+token, "is not expected after a '#' at line", line)
                print("Compilation failed")
                exit()                  
        if state == 12:
            if token == "f":
                return (["defitoken",line])
            else:
                print("Invalid character de"+token, "is not expected after a '#' at line", line)
                print("Compilation failed")
                exit()         
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
                print("Compilation failed")
                exit()
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
                    print("Compilation failed")
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
                print("Compilation failed")
                exit()
    return (["EOFtoken",line])        

def syntax():
    global isAtLeastOneDeclaration
    global isAtLeastOneGlobal
    global isAtLeastOneID
    global isAtLeastOnePar
    global seekIndex
    global quadList
    global recordStructure
    global scope 
    global pos
    global finalCode
    global framelen
    global functionNumber

    def ifState(token):
        global seekIndex
        if token[0] == "commandtoken":
            if token[2] == "if" or token[2] == "elif":
                token = lex()
                cond = isCondition(token)
                if cond[0]:
                    conditionTrue = cond[1]
                    conditionFalse = cond[2]
                    backpatch(conditionTrue, nextQuad())
                    token = lex()
                    if token[0] == "anwkatwtoken":
                        token = lex()
                        if isStatement(token):
                            ifList = makeList(nextQuad())
                            quadList.append(genQuad("jump","_","_","_"))
                            backpatch(conditionFalse, nextQuad())
                            seekIndex = f.tell()
                            token = lex()
                            if token[0] == "commandtoken":
                                if token[2] == "elif":
                                    x = ifState(token)
                                    backpatch(ifList,nextQuad())
                                    return x
                                elif token[2] == "else":
                                    x = elseState(token)
                                    backpatch(ifList,nextQuad())
                                    return x
                                else:
                                    backpatch(ifList,nextQuad())
                                    f.seek(seekIndex)
                                    return True
                            else:
                                backpatch(ifList,nextQuad())
                                f.seek(seekIndex)
                                return True
                        else:
                            print ("Inside the 'if' at line:", token[1], "a statement was expected")
                            print("Compilation failed")
                            exit()
                    else:
                        print ("After the 'if' at line:", token[1], "a ':' was expected")
                        print("Compilation failed")
                        exit()
                else:
                    print ("After the 'if' at line:", token[1], "a condition was expected")
                    print("Compilation failed")
                    exit()

    def elseState(token):
        if token[2] == "else":
            token = lex()
            if token[0] == "anwkatwtoken":
                    token = lex()
                    if isStatement(token):
                        return True
                    else:
                        print ("Inside the 'else' at line:", token[1], "a statement was expected")
                        print("Compilation failed")
                        exit()
            else:
                    print ("After the 'else' at line:", token[1], "a ':' was expected")
                    print("Compilation failed")
                    exit()

    def isCondition(token):
        Btrue = []
        Bfalse = []
        global seekIndex
        bterm1 = isBoolTerm(token)
        if bterm1[0]:
            Q1true = bterm1[1]
            Q1false = bterm1[2]
            Btrue = Q1true
            Bfalse = Q1false
            seekIndex = f.tell()
            token = lex()
            if token[0] == "commandtoken":
                while token[2]=="or":
                    backpatch(Bfalse,nextQuad())
                    seekIndex = f.tell()
                    token = lex()
                    bterm2 = isBoolTerm(token)
                    if bterm2[0] == False:
                        print("After the 'or' at line:", token[1], "a boolean term was expected")
                        print("Compilation failed")
                        exit()
                    else:
                        Q2true = bterm2[1]
                        Q2false = bterm2[2]
                        Btrue = mergeList(Btrue,Q2true)
                        Bfalse = Q2false
                        f.seek(seekIndex)
                return [True,Btrue,Bfalse]
            else:
                f.seek(seekIndex)
                return [True,Btrue,Bfalse]
        else:
            print("At line:", token[1],"a boolean term was expected")
            print("Compilation failed")
            exit()       
    
    def isBoolTerm(token):
        Qtrue = []
        Qfalse = []
        global seekIndex
        bfactor1 = isBoolFactor(token)
        if bfactor1[0]:
            R1true = bfactor1[1]
            R1false = bfactor1[2]
            Qtrue = R1true
            Qfalse = R1false
            seekIndex = f.tell()
            token = lex()
            if token[0] == "commandtoken":
                while token[2]=="and":
                    backpatch(Qtrue,nextQuad())
                    seekIndex = f.tell()
                    token = lex()
                    bfactor2 = isBoolFactor(token)
                    if bfactor2[0]:
                        R2true = bfactor2[1]
                        R2false = bfactor2[2]
                        Qfalse = mergeList(Qfalse,R2false)
                        Qtrue = R2true
                        seekIndex = f.tell()
                        token = lex()
                        if token[0]!= "commandtoken":
                            break
                    else:
                        print("After the 'and' at line:", token[1], "a boolean factor was expected")
                        print("Compilation failed")
                        exit()
                f.seek(seekIndex)
                return [True,Qtrue,Qfalse]
            else:
                f.seek(seekIndex)
                return [True,Qtrue,Qfalse]
        else:
            print("At line:", token[1],"a boolean factor was expected")
            print("Compilation failed")
            exit()              

    def isBoolFactor(token):      
        Rtrue = []
        Rfalse = []
        if token[0] == "commandtoken":
            expr1 = isExpression(token)
            if expr1[0]:
                E1place = expr1[1]
                token = lex()
                if token[0] in relOpList:
                    if token[0] == "isothtatoken":
                        relOp = "="
                    elif token[0] == "mikroterotoken":
                        relOp = "<"
                    elif token[0] == "megaluterotoken":
                        relOp = ">"
                    elif token[0] == "mikisotoken":
                        relOp = "<="
                    elif token[0] == "megisotoken":
                        relOp = ">="
                    else:
                        relOp = "!="
                    token = lex()
                    expr2 = isExpression(token)
                    if expr2[0]:
                        E2place = expr2[1]
                        Rtrue = makeList(nextQuad())
                        quadList.append(genQuad(relOp, E1place,E2place,"_"))
                        Rfalse = makeList(nextQuad())
                        quadList.append(genQuad("jump","_","_","_"))
                        return [True,Rtrue,Rfalse]
                    else:
                        print("At line", token[1], "an expression was expected after a relationship opperand")
                        print("Compilation failed")
                        exit()
            elif token[2] == "not":
                token = lex()
                cond = isCondition(token)
                if cond[0]:
                    Btrue = cond[1]
                    Bfalse = cond[2]
                    Rtrue = Bfalse
                    Rfalse = Btrue
                    return [True,Rtrue,Rfalse]
                else:
                    print("At line:", token[1],"a boolean factor was expected after 'not")
                    print("Compilation failed")
                    exit()
            else:
                return [False]
        else:
            expr1 = isExpression(token)
            if expr1[0]:
                E1place = expr1[1]
                token = lex()
                if token[0] in relOpList:
                    if token[0] == "isothtatoken":
                        relOp = "="
                    elif token[0] == "mikroterotoken":
                        relOp = "<"
                    elif token[0] == "megaluterotoken":
                        relOp = ">"
                    elif token[0] == "mikisotoken":
                        relOp = "<="
                    elif token[0] == "megisotoken":
                        relOp = ">="
                    else:
                        relOp = "!="
                    token = lex()
                    expr2 = isExpression(token)
                    if expr2[0]:
                        E2place = expr2[1]
                        Rtrue = makeList(nextQuad())
                        quadList.append(genQuad(relOp, E1place,E2place,"_"))
                        Rfalse = makeList(nextQuad())
                        quadList.append(genQuad("jump","_","_","_"))
                        return [True,Rtrue,Rfalse]
                    else:
                        print("At line", token[1], "an expression was expected after a relationship opperand")
                        print("Compilation failed")
                        exit()
            else:
                cond = isCondition(token)
                if cond[0]:
                    Btrue = cond[1]
                    Bfalse = cond[2]
                    Rtrue = Btrue
                    Rfalse = Bfalse
                    return [True,Rtrue,Rfalse]
                else:
                    return [False]          

    def isExpression(token):
        Eplace = 0
        global seekIndex
        global pos
        global scope
        seekIndex = f.tell()
        negSign = False
        if isOptionalSign(token):
            if token[0] == "subtoken":
                negSign = True
            token = lex()       
        term1 = isTerm(token)
        if term1[0]:
            T1place = term1[1]
            if negSign:
                y = newTemp()
                pos=pos+4
                newPos=pos
                newScope=scope-1
                recordStructure.addNewEntity(scopeIndex=newScope,entityName=y,entity_type='TemporaryVariable', offset=newPos)
                quadList.append(genQuad("-",0,T1place,y))
                T1place = y
            seekIndex = f.tell()
            token = lex()
            while token[0] == "addtoken" or token[0] == "subtoken":
                if token[0] == "addtoken":
                    operand = "+"
                else:
                    operand = "-"
                token = lex()
                term2 = isTerm(token)
                if term2[0]:
                    T2place = term2[1]
                    w = newTemp()
                    pos=pos+4
                    newPos=pos
                    newScope=scope-1
                    recordStructure.addNewEntity(scopeIndex=newScope,entityName=w,entity_type='TemporaryVariable', offset=newPos)
                    quadList.append(genQuad(operand,T1place,T2place,w))
                    T1place = w
                    seekIndex = f.tell()
                    token = lex()
                else:
                    print("At line", token[1], "a term was expected after an add or sub opperand. Instead found:", token[0])
                    print("Compilation failed")
                    exit()
            f.seek(seekIndex)
            Eplace = T1place
            return [True,Eplace]
        else:
            f.seek(seekIndex)      
            return [False]
    
    def isOptionalSign(token):
        global seekIndex       
        if token[0] == "addtoken" or token[0] == "subtoken":
            return True
        else:
            return False
   
    def isTerm(token):
        Tplace = 0
        global seekIndex
        global pos 
        global scope
        factor1 = isFactor(token)
        if factor1[0]:
            F1place = factor1[1]
            seekIndex = f.tell()
            token = lex()
            while token[0] == "multoken" or token[0] == "modtoken" or token[0] == "divtoken":
                if token[0] == "multoken":
                    operand = "*"
                elif token[0] == "divtoken":
                    operand = "/"
                else:
                    operand = "mod"
                token = lex()
                factor2 = isFactor(token)
                if factor2[0]:
                    F2place = factor2[1]
                    w = newTemp()
                    pos=pos+4
                    newPos=pos
                    newScope=scope-1
                    recordStructure.addNewEntity(scopeIndex=newScope,entityName=w,entity_type='TemporaryVariable', offset=newPos)
                    quadList.append(genQuad(operand,F1place,F2place,w))
                    F1place = w
                    seekIndex = f.tell()
                    token = lex()
                else:
                    print("At line", token[1], "a factor was expected after a multiplication or division opperand. Instead found: ",token[0])
                    print("Compilation failed")
                    exit()
            f.seek(seekIndex)
            Tplace = F1place
            return [True,Tplace]
        else:
            return [False]
        
    def isFactor(token):
        Fplace = 0
        global seekIndex
        global pos 
        global scope
        if token[0] == "numbertoken":
            Fplace = token[2]
            return [True,Fplace]        
        elif token[0] == "anagnoristikotoken":
            idName = token[2]
            seekIndex = f.tell()
            tempSeekIndex = seekIndex
            token = lex()
            if idTail(token):
                w = newTemp()
                pos=pos+4
                newPos=pos
                newScope=scope-1
                recordStructure.addNewEntity(scopeIndex=newScope,entityName=w,entity_type='TemporaryVariable', offset=newPos)
                quadList.append(genQuad("par",w,"ret","_"))
                quadList.append(genQuad("call",idName,"_","_"))
                return [True,w]
            else:
                IDplace = idName
                Fplace = IDplace
                f.seek(tempSeekIndex)
                return [True,Fplace]       
        elif token[0] == "leftpartoken":
            token = lex()
            expr = isExpression(token)
            if expr[0]:
                Eplace = expr[1]
                Fplace = Eplace
                token = lex()
                if token[0] == "rightpartoken":
                    return [True,Fplace]
                else:
                    print("At line", token[1], "a ')' was expected")
                    print("Compilation failed")
                    exit()
            else:
                print("At line", token[1], "an expression was expected")
                print("Compilation failed")
                exit()         
        else:
            return [False]

    def idTail(token):
        if token[0] == "leftpartoken":
            token = lex()
            if parList(token):
                token = lex()
                if token[0] == "rightpartoken":
                    return True
                else:
                    print("At line", token[1], "a ')' was expected")
                    print("Compilation failed")
                    exit()
            else:
                return False
        else:
            return False

    def parList(token):
        global seekIndex
        global isAtLeastOnePar
        global pos
        global scope
        expr1 = isExpression(token)
        if expr1[0]:
            E1place = expr1[1]
            a = E1place
            pos=pos+4
            newPos=pos
            newScope=scope-1
            recordStructure.addNewEntity(scopeIndex=newScope,entityName=a,entity_type='Variable', offset=newPos)
            quadList.append(genQuad("par",a,"CV","_"))
            isAtLeastOnePar = True
            seekIndex = f.tell()
            token=lex()
            while token[0] == "commatoken":
                seekIndex = f.tell()
                token = lex()
                expr2 = isExpression(token)
                if expr2[0]:
                    E2place = expr2[1]
                    b = E2place
                    pos=pos+4
                    newPos=pos
                    newScope=scope-1
                    recordStructure.addNewEntity(scopeIndex=newScope,entityName=b,entity_type='Variable', offset=newPos)
                    quadList.append(genQuad("par",b,"CV","_"))
                    seekIndex = f.tell()
                    token=lex()
                    continue
                else:
                    print("At line", token[1], "an expression was expected after the ','")
                    print("Compilation failed")
                    exit()
            f.seek(seekIndex)
            return isAtLeastOnePar
        else:
            f.seek(seekIndex)
            return True
        
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
            idPlace = token[2]
            token = lex()
            if token[0] == "ana8eshtoken":
                token = lex()
                expr = isExpression(token)
                if expr[0]:
                    Eplace = expr[1]
                    quadList.append(genQuad(":=", Eplace, "_", idPlace))
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
                                                quadList.append(genQuad("inp",idPlace,"_","_"))
                                                return True
                                            else:
                                                print("At line", token[1], "a ')' was expected")
                                                print("Compilation failed")
                                                exit()
                                        else:
                                            print("At line", token[1], "a ')' was expected")
                                            print("Compilation failed")
                                            exit()
                                    else:
                                        print("At line", token[1], "a '(' was expected")
                                        print("Compilation failed")
                                        exit()
                                else:
                                    return False
                            else:
                                return False
                        else:
                            print("At line", token[1], "a '(' was expected")
                            print("Compilation failed")
                            exit()
                    else:
                        return False
                else:
                    print("At line", token[1], "either an expression or 'int(input()) was expected after the '='")
                    print("Compilation failed")
                    exit()
            else:
                return False
        else:
            return False           
    
    def isReturnStat(token):
        if token[0] == "commandtoken":
            if token[2] == "return":
                token = lex()
                expr = isExpression(token)
                if expr[0]:
                    Eplace = expr[1]
                    quadList.append(genQuad("ret", Eplace, "_", "_"))
                    return True
                else:
                    print("At line", token[1], "an expression was expected after the 'return' command")
                    print("Compilation failed")
                    exit()
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
                cond = isCondition(token)
                if cond[0]:
                    conditionTrue = cond[1]
                    conditionFalse = cond[2]
                    backpatch(conditionTrue, nextQuad())
                    token = lex()
                    if token[0] == "anwkatwtoken":
                        token = lex()
                        if token[0] == "anoigmatoken":
                            token = lex()
                            if statements(token):
                                token = lex()
                                if token[0] == "kleisimotoken":
                                    
                                    quadList.append(genQuad("jump","_","_",condQuad))
                                    backpatch(conditionFalse,nextQuad())
                                    return True
                                else:
                                    print("At line", token[1] ,"a '#}' was expected to close a '#{ found earlier for the while loop")
                                    print("Compilation failed")
                                    exit()
                            else:
                                print("At line", token[1], "a statement was expected after the ':'")
                                print("Compilation failed")
                                exit()
                        else: 
                            print("At line", token[1], "a '#{' was expected after the 'while'")
                            print("Compilation failed")
                            exit()
                    else:
                        print("At line", token[1], "a ':' was expected")
                        print("Compilation failed")
                        exit()
                else:
                    print("At line", token[1], "a condition was expected after the 'while' command")
                    print("Compilation failed")
                    exit()
            else:
                return False
        else:
            return False
        
    def startRule():
        token=lex()
        recordStructure.addNewScope()
        
        if declarations(token):
            token=lex()            
            while isDefFunctions(token):
                token=lex()
            if callMainPart(token):
                quadList.append(genQuad("halt","_","_","_"))
                quadList.append(genQuad("end_block","main","_","_"))
                readQuadList(quadList[-1])
                return True
            else:
                exit()                                           
        else:
            print("At line", token[1]," declarations was expected")
            print("Compilation failed")
            exit()

    def isPrintStat(token):
        global seekIndex
        if token[0] == "commandtoken":
            if token[2] == "print":
                token = lex()
                if token[0] == "leftpartoken":
                    token = lex()
                    expr = isExpression(token)
                    if expr[0]:
                        Eplace = expr[1]
                        token = lex()
                        if token[0] == "rightpartoken":
                            quadList.append(genQuad("out",Eplace,"_","_"))
                            seekIndex = f.tell()
                            return True
                        else:
                            print("At line", token[1]," a ')' was expected")
                            print("Compilation failed")    
                            exit() 
                    else:
                        print("At line", token[1], "an expression was expected after the 'print' command")
                        print("Compilation failed")    
                        exit()
                else:
                    print("At line", token[1]," a '(' was expected after the 'print' command")
                    print("Compilation failed")    
                    exit()
            else:
                return False
        else:
            return False
            
    def isIdList(token):
        global seekIndex
        global isAtLeastOneID
        global pos
        global scope
        names =[]
        if token[0]=="anagnoristikotoken":
            isAtLeastOneID = True
            seekIndex = f.tell()
            names.append(token[2])
            token=lex()
            newScope=scope-1
            while token[0]=="commatoken":
                token=lex()
                if token[0]=="anagnoristikotoken":
                    names.append(token[2])
                    seekIndex = f.tell()
                    token=lex()
                else:
                    print("At line", token[1]," an id was expected")
                    print("Compilation failed")    
                    exit()
            f.seek(seekIndex)
            for x in names:
                pos=pos+4
                newPos=pos
                recordStructure.addNewEntity(scopeIndex=newScope,entityName=x,entity_type='Variable', offset=newPos)
            return [isAtLeastOneID,names] 
        else:
            f.seek(seekIndex)
            return [False,names]
        
    def statements(token):
        
        global seekIndex
        if isStatement(token) == False:
            f.seek(seekIndex)
            return False
        f.seek(seekIndex)
        token = lex()
        while isStatement(token):
            seekIndex = f.tell()
            f.seek(seekIndex)
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
            idList =isIdList(token)
            if idList[0]:              
                return True
            else:
                print("At line", token[1], "an id was expected ")
                print("Compilation failed")
                exit()
        else:
            return False
    
    def isGlobal(token):          
        if token[0]=="commandtoken":
            if token[2]=="global":
                token=lex()
                idList =isIdList(token)
                if idList[0]:
                    return True
                else:
                    print("At line", token[1], "an id was expected ")
                    print("Compilation failed")
                    exit()
            else:
                return False
        else:
            return False
        
    def isDefFunctions(token):
        global scope
        global pos
        if token[0] == "commandtoken":
            if token[2] == "def":
                token=lex()
                if token[0] == "anagnoristikotoken":
                    lastBlock.append(token[2])
                    q = token[2]
                    pos=pos+4
                    newPos=pos
                    newScope=scope-1
                    token=lex()
                    if token[0] == "leftpartoken":
                        token = lex()
                        idList =isIdList(token)
                        if idList[0]:                   
                            framelen=newPos
                            recordStructure.addNewEntity(scopeIndex=newScope,entityName=q,entity_type='Function', framelength=newPos,arguments=idList[1])
                            token=lex()
                            if token[0] == "rightpartoken":
                                token = lex()
                                if token[0] == "anwkatwtoken":
                                    recordStructure.addNewScope()
                                    token = lex()
                                    if token[0] == "anoigmatoken":
                                        token = lex()
                                        if declarations(token):

                                            token = lex()
                                        hasFunction = False
                                        while True:
                                            if isDefFunctions(token):
                                                hasFunction = True
                                                token = lex()
                                                continue
                                            else:
                                                if hasFunction == False:
                                                    quadList.append(emptyList())
                                                    indexList.append(len(quadList)-1)
                                                break
                                        while globalVar(token):
                                            token = lex()
                                        if statements(token):
                                            token = lex()
                                            
                                            if token[0] == "kleisimotoken":
                                                quadList.append(genQuad("end_block",lastBlock[-1],"_","_"))
                                                
                                                pos=newPos
                                                if len(lastBlock) == 1 and len(indexList) == 0:
                                                    lastBlock.pop()
                                                    readQuadList(quadList[-1])
                                                    return True
                                                if len(indexList)>0:
                                                    quadList[indexList[-1]] = ["begin_block",lastBlock.pop(),"_","_"]
                                                    
                                                    indexList.pop()
                                                    readQuadList(quadList[-1])
                                                    if len(indexList) == 0 and len(lastBlock)>0:
                                                        
                                                        quadList.append(genQuad("begin_block",lastBlock[-1],"_","_"))
                                                else:
                                                    
                                                    quadList.append(genQuad("begin_block",lastBlock[-1],"_","_"))
                                                
                                                return True
                                            else:
                                                print ("At line", token[1], "a '#}' was expected to close a '#{' found earlier")
                                                print("Compilation failed")
                                                exit()
                                        else:
                                            print ("At line", token[1], "a statement was expected")
                                            print("Compilation failed")
                                            exit()
                                    else:
                                        print ("At line", token[1], "a '#{' was expected")
                                        print("Compilation failed")
                                        exit()
                                else:
                                    print ("At line", token[1], "a ':' was expected")
                                    print("Compilation failed")
                                    exit()
                            else:
                                print ("At line", token[1], "a ')' was expected")
                                print("Compilation failed")
                                exit()
                        else:
                            print ("At line", token[1], "an id was expected")
                            print("Compilation failed")
                            exit()
                    else:
                        print ("At line", token[1], "a '(' was expected")
                        print("Compilation failed")
                        exit()
                else:
                    print ("At line", token[1], "an id was expected")
                    print("Compilation failed")
                    exit()
            else:
                return False
        else:
            return False

        
    def callMainPart(token):
        global scope
        global pos
        global framelen
        recordStructure.addNewScope()
        if token[0] == "defitoken":
            token = lex()
            if token[0] == "commandtoken":
                if token[2] == "main":
                    q = token[2]
                    pos=pos+4
                    newPos=pos
                    newScope=scope-1
                    framelen=newScope
                    recordStructure.addNewEntity(scopeIndex=newScope,entityName=q,entity_type='Function', framelength=newPos,arguments=[])
                    quadList.append(genQuad("begin_block","main","_","_"))
                    token=lex()
                    if declarations(token):
                        token=lex()
                    if statements(token):      
                            return True
                    else:
                        print ("At line", token[1], "a statement was expected")
                        print("Compilation failed")
                        exit()
                else:
                    exit()
            else:
                exit()
        else:
            return False


    def nextQuad():
        global quadNum
        return quadNum+1

    def genQuad(op,x,y,z):
        global quadNum
        quadNum += 1
        quad = [op,x,y,z]
        return quad

    def newTemp():
        global tempNum
        tempNum += 1
        s = "T_"
        return s+str(tempNum)

    def emptyList():
        return genQuad("_","_","_","_")

    def makeList(label):
        return [label]

    def mergeList(list1,list2):
        return list1+list2

    def backpatch(lst, label):
        for x in lst:
            quadList[x-1][-1] = label


    def getNextLabel():
        global functionNumber
        functionNumber+=1
        return "L"+str(functionNumber)


    def writeFunctionFinalCode(quadSubList):
        global finalCode
        global framelen
        branchRelOperators = ["=",">","<","!=",">=","<="]
        arithmeticOperators = ["+","-","*","/","and","not","or"]
        index = 0
        while(index<len(quadSubList)):
            quad = quadSubList[index]
            currentLabel = getNextLabel()
            finalCode += currentLabel+":\n"
            if(quad[0] == "begin_block" and quad[1] == "main"):
                finalCode += "Lmain:\n"
           

            if(quad[0] == "begin_block"):
                funcBeginLabels[quad[1]] = currentLabel
                finalCode +="\tsw ra,0(sp)\n"

            elif(quad[0] == "end_block"):
                final.retToCaller()
                finalCode = final.write_instructions(finalCode)
            
            elif(quad[0] == ":="):
                if(recordStructure.searchEntity(quad[1]) is not None):
                    final.loadvr(str(quad[1]),"t0")
                    finalCode = final.write_instructions(finalCode)
                else:
                    final.gnlvcode(str(quad[1]),"t0")
                    finalCode = final.write_instructions(finalCode)

                final.storerv((quad[3]),"t0")
                finalCode = final.write_instructions(finalCode)
            
            elif(quad[0] in branchRelOperators):
                final.loadvr(str(quad[1]), "t0")
                finalCode = final.write_instructions(finalCode)
                final.loadvr(str(quad[2]), "t1")
                finalCode = final.write_instructions(finalCode)
                final.branch("t0","t1","L"+str(quad[3]),str(quad[0]))
                finalCode = final.write_instructions(finalCode)
            
            elif(quad[0] == "jump"):
                finalCode +=("\tj L"+str(quad[3])+"\n")
            
            elif(quad[0] == "ret"):
                finalCode += "\tlw t0 -8(sp)\n\tlw t1, -"+str(pos)+"(sp)\n\tsw t1, 0(t0)\n"
            
            elif(quad[0] in arithmeticOperators):
                if(str(quad[1]).isnumeric()):
                    if(quad[0] == "+" or quad[0] == "-"):
                        finalCode += "\taddi t0, zero, "+str(quad[1])+"\n"
                    elif(quad[0] == "*" or quad[0] == "/"):
                        finalCode += "\muli t0, "+str(quad[1])+"\n"
                else:
                    final.loadvr(str(quad[1]),"t0")
                    finalCode = final.write_instructions(finalCode)

                if(str(quad[2]).isnumeric()):
                    if(quad[0] == "+" or quad[0] == "-"):
                        finalCode += "\taddi t1, zero, "+str(quad[2])+"\n"
                    elif(quad[0] == "*" or quad[0] == "/"):
                        finalCode += "\muli t1, "+str(quad[2])+"\n"
                else:
                    final.loadvr(str(quad[2]),"t1")
                    finalCode = final.write_instructions(finalCode)
                
                final.operations("t0","t1","t2",str(quad[0]))
                finalCode = final.write_instructions(finalCode)
                final.storerv(str(quad[3]),"t2")
                finalCode = final.write_instructions(finalCode)
            
            elif(quad[0] == "mod"):
                if(recordStructure.searchEntity(quad[1]) is not None):
                    final.loadvr(str(quad[1]),"t0")
                    finalCode = final.write_instructions(finalCode)
                else:
                    final.gnlvcode(str(quad[1]),"t0")
                    finalCode = final.write_instructions(finalCode) 

                if(recordStructure.searchEntity(quad[2]) is not None):
                    final.loadvr(str(quad[2]),"t1")
                    finalCode = final.write_instructions(finalCode)
                else:
                    final.gnlvcode(str(quad[2]),"t1")
                    finalCode = final.write_instructions(finalCode)

                final.loadvr(str(quad[3]),"t2")
                finalCode = final.write_instructions(finalCode)
                finalCode+= "\trem t2,t0,t1\n"
                final.storerv(str(quad[3]),"t2")
                finalCode = final.write_instructions(finalCode)
            
            elif(quad[0] == "inp"):
                final.loadvr(str(quad[1]),"t0")
                finalCode = final.write_instructions(finalCode)
                finalCode+= "\tli a0, 0\n\tli a2, 1\n\tli a7,63\n\tecall\n"
                final.move("t0","a0")
                finalCode = final.write_instructions(finalCode)
            
            elif(quad[0] == "out"):
                final.loadvr(str(quad[1]),"t0")
                finalCode = final.write_instructions(finalCode)
                finalCode+= "\tlw a0, 0(t0)\n\tli a7,1\n\tecall\n"
            
            elif(quad[0] == "halt"):
                final.end()
                finalCode = final.write_instructions(finalCode)
            
            elif(quad[0] == "par"):
                finalCode+= "\taddi s0,sp,"+str(framelen)+"\n"#### opou fp s0
                while(quad[0] =="par" and quad[2]!="ret"):
                    entity,entity_level = recordStructure.searchEntity(quad[1])
                    offset = entity.offset
                    finalCode += getNextLabel()+":\n"
                    final.loadvr(str(quad[1]),"t0")
                    finalCode = final.write_instructions(finalCode)
                    finalCode+= "\tsw t0, -"+str(offset)+"(s0)\n"###opou fp s0
                    index+=1
                    quad = quadSubList[index]
                

                finalCode += getNextLabel()+":\n"
                finalCode+= "\taddi t0, sp, -"+str(offset)+"\n"
                finalCode+= "\tsw t0, -8(s0)\n"###opou fp s0
                index+=1
                quad = quadSubList[index]
                finalCode += getNextLabel()+":\n"
                label = funcBeginLabels[quad[1]]
                final.callFun(label)
                finalCode = final.write_instructions(finalCode)
            index+=1
                     

    def readQuadList(quad):
        funcName = quad[1]
        endIndex = quadList.index(quad)
        beginIndex = quadList.index(["begin_block",funcName,"_","_"])
        writeFunctionFinalCode(quadList[beginIndex:endIndex+1])

    relOpList=["isothtatoken","mikroterotoken","megaluterotoken","mikisotoken","megisotoken","diaforotoken"]
    seekIndex = f.tell()
    lastBlock = []
    indexList = []
    functionNumber = 0
    funcBeginLabels = {}

    return startRule()

isAtLeastOneDeclaration = False
isAtLeastOneGlobal = False
isAtLeastOneID = False
isAtLeastOnePar = False
line = 0
quadNum = 1
tempNum = 0
quadList = [["jump","_","_","main"]]
recordStructure = RecordStructure()
final = Final(recordStructure)
pos=12
scope=0
latestNewLine = -1
framelen =0 

finalCode = "\t.data\n\tstr_nl: .asciz \"\\n\"\n\t.text\nL0:\n\tj Lmain\n"

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
    filename = f"intermediate-for-({fileToCompile}).int"
    filename2 = f"assembly-for-({fileToCompile}).asm"
    with open(filename, 'w') as f:
        for i, x in enumerate(quadList, start=0):
            print(f"{i}: {' '.join(map(str, x))}", file=f)
    with open(filename2, 'w') as f:
        f.write(finalCode)
else:
    print('Compilation failed')

recordStructure.printScopesToFile("symbol-table-for-("+str(fileToCompile)+").sym")
