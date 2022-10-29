FOR /F "tokens=* USEBACKQ" %%F IN (`where python ^| findstr Python310`) DO (
SET py310=%%F
)
IF [%py310%]==[] SET py310=py

%py310% -m virtualenv venv && venv\Scripts\activate.bat && pip install -r packages.txt
if %ERRORLEVEL% neq 0 GOTO ProcessError

:ProcessError
%py310% -m venv venv && venv\Scripts\activate.bat && pip install -r packages.txt

DOSKEY app=py app.py $*
