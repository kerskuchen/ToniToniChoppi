pip3 install pyinstaller
pip3 install cairosvg
pyinstaller --add-binary "C:\Users\kerskuchen\AppData\Local\Programs\Python\Python39\Lib\site-packages\cairosvg";cairosvg --add-binary "C:\Users\kerskuchen\AppData\Local\Programs\Python\Python39\Lib\site-packages\cairocffi";cairocffi --specpath  build --name ToniToniChoppi --noconsole --onefile main.py

pause