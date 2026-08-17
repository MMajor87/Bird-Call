$version = & .\.venv\Scripts\python.exe -c "from version import VERSION; print(VERSION)"
& .\.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --name "Bird-Call-$version" --add-data "BlueJay.png;." --paths ".." main.py
