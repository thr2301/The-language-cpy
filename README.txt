***This is a compiler that compiles a language callwd cpy to RISC-V assembly. It was created from the scratch for the project of the university course Complilers 1***

**Instructions for the execution:**

**Some test files are:**
i) test.cpy 
ii) onlyMainTest.cpy 
iii) moreThanOneDeclarationsTest.cpy
iv) limitsTest.cpy 
v)smallTest.cpy
vi)ifWhileTest.cpy 
vii) finalCodeExampleTest.cpy 

**The compiler file is:* 
cpy.py

To run the compiler you need to open a terminal in the folder where you saved cpy.py and run the following command: 
\the_path_of_the_file>/python cpy.py nameOfTheFileToTest.cpy

Intermediate code is generated in the intermediate-for file
(nameOfTheFileToTest.cpy).int and the symbol table is generated in the file 
symbol-table-for-(nameOfTheFileToTest.cpy).sym .The final code is generated at 
assembly-for-(nameOfTheFileToTest.cpy).asm file.

**Important notes:*
1)More details you can find in the REPORT.pdf
2)There is a problem in the code that is produced , more specifically in some tests there are infinite loop.
