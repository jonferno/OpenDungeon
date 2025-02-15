@echo off
echo Setting up environment...

REM Create venv if it doesn't exist
if not exist venv (
    python -m venv venv
    echo Created new virtual environment
)

REM Explicitly activate using Python command
venv\Scripts\python.exe -m pip install --upgrade pip

REM Install PyQt5 without tools
echo Installing PyQt5...
venv\Scripts\python.exe -m pip install PyQt5==5.15.7

REM Install other requirements
venv\Scripts\python.exe -m pip install -r current/requirements.txt

echo Select startup mode:
echo 1. Normal Application
echo 2. Qt Designer
echo 3. Run UI

set /p mode="Enter mode (1, 2, or 3): "

if "%mode%"=="1" (
    echo Starting normal application...
    venv\Scripts\python.exe current/main.py
) else if "%mode%"=="2" (
    echo Looking for Qt Designer...
    set "DESIGNER_PATH="
    
    REM Check Qt Designer locations with proper quotes
    if exist "C:\Qt\Tools\QtDesignStudio\qt6_design_studio_reduced_version\bin\designer.exe" (
        set DESIGNER_PATH=C:\Qt\Tools\QtDesignStudio\qt6_design_studio_reduced_version\bin\designer.exe
        echo Found Qt Designer
        start "" "%DESIGNER_PATH%" "current/ui/designer/main_window.ui"
    ) else (
        echo Qt Designer not found.
        echo Please ensure Qt Design Studio is installed at:
        echo C:\Qt\Tools\QtDesignStudio\qt6_design_studio_reduced_version\bin\designer.exe
        pause
    )
) else if "%mode%"=="3" (
    echo Running UI...
    venv\Scripts\python.exe current/main.py
) else (
    echo Invalid selection!
)

pause
