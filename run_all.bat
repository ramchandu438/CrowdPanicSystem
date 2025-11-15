@echo off
REM One-click starter for CrowdPanicSystem

set PROJECT_DIR=%USERPROFILE%\OneDrive\Desktop\CrowdPanicSystem

echo Starting Simulator...
start cmd /k "cd /d %PROJECT_DIR% && python simulator.py"
timeout /t 3 >nul

echo Starting Trainer (once)...
start cmd /k "cd /d %PROJECT_DIR% && python trainer.py"
timeout /t 3 >nul

echo Starting Classifier...
start cmd /k "cd /d %PROJECT_DIR% && python classifier.py"
timeout /t 3 >nul

echo Starting Dashboard...
start cmd /k "cd /d %PROJECT_DIR% && streamlit run dashboard.py"

echo All services started!
exit
