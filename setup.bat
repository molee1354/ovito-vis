FOR /F "tokens=* USEBACKQ" %%F IN (`dir /S C:\python.exe ^| findstr /e Python310`) DO (
SET pydir=%%F
)
set pydir=%pydir:Directory of =%
set py310=%pydir%\python.exe
IF [%pydir%]==[] SET py310=py

%py310% -m virtualenv venv && venv\Scripts\activate.bat && pip install -r packages.txt && DOSKEY app=py app.py $*
if %ERRORLEVEL% neq 0 GOTO ProcessError

:ProcessError
%py310% -m venv venv && venv\Scripts\activate.bat && pip install -r packages.txt && DOSKEY app=py app.py $*