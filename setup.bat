@echo off
FOR /F "tokens=* USEBACKQ" %%F IN (`py --version`) DO (
SET PYVERSION=%%F
)
echo %PYVERSION%
set /p pyexist= "Does the above prompt say Python 3.10.x? [y/n] : "
IF "%pyexist%"=="n" (
    GOTO NeedInstall
) ELSE (
    GOTO EnvSetup
)

:NeedInstall
set /p needinstall= "Does Python 3.10 need to be installed? [y/n] : "
IF "%needinstall%"=="y"  GOTO GetPython
IF "%needinstall%"=="n"  GOTO FindPython

:FindPython
FOR /F "tokens=* USEBACKQ" %%F IN (`dir /S C:\python.exe ^| findstr /e Python310`) DO (
SET pydir=%%F
)
set pydir=%pydir:Directory of =%
set py310=%pydir%\python.exe
GOTO EnvSetup

:EnvSetup
IF [%pydir%]==[] SET py310=py
%py310% -m virtualenv venv && venv\Scripts\activate.bat && pip install -r packages.txt && DOSKEY app=py app.py $*
if %ERRORLEVEL% neq 0 GOTO ProcessError

:ProcessError
%py310% -m venv venv && venv\Scripts\activate.bat && pip install -r packages.txt && DOSKEY app=py app.py $*

:GetPython
get_python.bat