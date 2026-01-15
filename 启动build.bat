"D:\ProgramData\miniconda3\python.exe" -m PyInstaller ^
  --onedir ^
  --console ^
  --icon=logo.ico ^
  --name="¹«½»LCDÄ£ÄâÆ÷V1.1" ^
  --version-file=version_info.txt ^
  --add-data="styles;styles" ^
  --add-data="styles/resources;resources" ^
  --hidden-import=subprocess ^
  --hidden-import=platform ^
  --hidden-import=json ^
  --hidden-import=re ^
  --hidden-import=hashlib ^
  --hidden-import=uuid ^
  --hidden-import=ctypes ^
  --hidden-import=ctypes.wintypes ^
  --hidden-import=winreg ^
  --hidden-import=os ^
  --hidden-import=sys ^
  --hidden-import=math ^
  --collect-all tkinter ^
  --clean ^
  main.py
pause