@echo off

:loop
set /p cmd=mcsmp.py 
python %~dp0\mcsmp.py %cmd%
set cmd=""
echo.
goto loop