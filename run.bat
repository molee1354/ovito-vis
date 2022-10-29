FOR /F "tokens=* USEBACKQ" %%F IN (`where python ^| findstr Python310`) DO (
SET py310=%%F
)

%py310% -m virtualenv venv
venv\Scripts\activate.bat && pip install -r packages.txt

DOSKEY app=py app.py $*
