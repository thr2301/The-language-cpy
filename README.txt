Athanasios Roudis 5098 , Stylianos Simantirakis 5127

Instructions for the execution:

The test files are:
i) test.cpy
ii) onlyMainTest.cpy
iii) moreThanOneDeclarationsTest.cpy
iv) limitsTest.cpy

The compiler file is: cpy.py

To run the compiler you must open a terminal in the folder in which you have saved the cpy.py and run the following command :
\the_path_of_the_file>python cpy.py onlyMain.cpy


Important notes:
Because of the logic of  looking to the next token to determine if the syntax is correct and 
after the check we go back to the previous token with f.seek() and we call lex again, 
when it reads a \n that it already has read it counts the line again so the lines of the error messages are not correct. 
We thought of a way to do it but it would be too costly for the purpose it serves 
so we preferred not to do it so the speed of the compiler isn't compromised 

