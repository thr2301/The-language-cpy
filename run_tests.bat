@echo off

REM Check if the compiler script is provided as argument
if "%1"=="" (
    echo Usage: %0 ^<compiler_script^>
    exit /b 1
)

set "compiler_script=%1"

REM List of test file names
set "test_files=test.cpy onlyMainTest.cpy moreThanOneDeclarationsTest.cpy limitsTest.cpy smallTest.cpy ifWhileTest.cpy finalCodeExampleTest.cpy"

REM Change directory to where your test files are located
cd /d "path\to\your\test\files\directory"

REM Iterate over each test file
for %%f in (%test_files%) do (
    echo Testing %%f...
    REM Call the compiler script with the test file as argument
    python "%compiler_script%" "%%f"
    REM Add a blank line for clarity
    echo.
)
