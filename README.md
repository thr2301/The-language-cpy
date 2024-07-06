# This is a compiler that compiles a language called cpy to RISC-V assembly. It was created from scratch for a project for the university course Complilers 1

## Instructions for the execution:

The compiler file is:cpy.py

To run the compiler you need to open a terminal in the folder where you saved cpy.py and run the following command: 
\the_path_of_the_file>/python cpy.py nameOfTheFileToTest.cpy

Intermediate code is generated in the intermediate-for file
(nameOfTheFileToTest.cpy).int and the symbol table is generated in the file 
symbol-table-for-(nameOfTheFileToTest.cpy).sym .The final code is generated at 
assembly-for-(nameOfTheFileToTest.cpy).asm file.


## Some test files are:
- i) test.cpy 
- ii) onlyMainTest.cpy 
- iii) moreThanOneDeclarationsTest.cpy
- iv) limitsTest.cpy 
- v)smallTest.cpy
- vi)ifWhileTest.cpy 
- vii) finalCodeExampleTest.cpy 

## Important notes:
- 1)More details you can find in the REPORT.pdf
- 2)There is a problem in the code that is produced , more specifically in some tests there are infinite loop where a function returns to the caller.
- 3)You can run all the tests at once in command line using the file run_tests.bat and using the following command:
run_tests.bat cpy.py
