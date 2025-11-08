echo Activating Python virtual environment...
call appEnv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install required packages, continuing...
)

call cd webapp\

echo Attempting Flask database initialization...
flask db init
if errorlevel 1 (
    echo flask db init failed or already exists, continuing...
)

echo Attempting Flask database migration...
flask db migrate
if errorlevel 1 (
    echo Flask db migrate failed, continuing...
)

echo Attempting Flask database upgrade...
flask db upgrade
if errorlevel 1 (
    echo Flask db upgrade failed, continuing...
)

cls
echo Application setup complete, running app.

timeout /t 2 /nobreak > NUL

echo Running application...
py app.py
pause