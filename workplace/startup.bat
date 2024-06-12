@echo off
setlocal enabledelayedexpansion

for /l %%i in (1,1,100) do (
    set "task_num=%%i"
    if %%i LSS 10 (
        set "task_num=00%%i"
    ) else if %%i LSS 100 (
        set "task_num=0%%i"
    )
    call :run_task wp!task_num!
)

:end
echo All tasks completed. Press any key to exit...
pause >nul
exit /b

:run_task
echo Starting task in directory %1 at %date% %time%
cd %1
if exist "Job-2.lck" del "Job-2.lck"
powershell -ExecutionPolicy Bypass -File ..\monitor.ps1 "abq2022 cpus=8 job=Job-2 user=..\subroutines3_revised.for input=Job-1_modified.inp int ask=OFF"

if exist "Job-2.dat" del "Job-2.dat"
if exist "Job-2.stt" del "Job-2.stt"

cd ..
echo Completed task in directory %1 at %date% %time%
echo.
exit /b
