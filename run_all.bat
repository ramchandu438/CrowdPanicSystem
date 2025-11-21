@echo off
echo Starting Crowd Panic System...

REM -------- Start Simulator (Firebase or Local) --------
start cmd /k "python simulator_firebase.py"

REM -------- Start Classifier --------
start cmd /k "python classifier_firebase.py"

REM -------- Start Dashboard --------
start cmd /k "streamlit run dashboard_multi.py"

echo All services started!
pause
