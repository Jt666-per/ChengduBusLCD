import sys

print(f"Python路径: {sys.executable}")

try:
    import tkinter
    print("tkinter导入成功!")
    print(f"Tk版本: {tkinter.TkVersion}")
except ImportError as e:
    print(f"tkinter导入失败: {e}")