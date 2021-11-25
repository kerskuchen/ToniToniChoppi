@echo off

pip3 install pyinstaller
pip3 install cairosvg

if exist shipping_windows rmdir /s /q shipping_windows
mkdir shipping_windows

REM NOTE: robocopy has success error code 1
robocopy "resources" "shipping_windows" /s /e > nul
if %errorlevel% neq 1 goto :error

pyinstaller --add-binary "C:\Users\kerskuchen\AppData\Local\Programs\Python\Python39\Lib\site-packages\cairosvg";cairosvg --add-binary "C:\Users\kerskuchen\AppData\Local\Programs\Python\Python39\Lib\site-packages\cairocffi";cairocffi --specpath  build --name ToniToniChoppi --noconsole --distpath "shipping_windows\ToniToniChoppi" --onefile main.py

if %errorlevel% neq 0 goto :error
goto :done

REM ------------------------------------------------------------------------------------------------
:error
echo Failed with error #%errorlevel%.
pause
exit /b %errorlevel%

REM ------------------------------------------------------------------------------------------------
:done
rmdir /s /q "temp"
echo FINISHED BUILDING WINDOWS SHIPPING