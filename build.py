import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, "bus_display.py")
icon_path = os.path.join(current_dir, "logo.ico")

# PyInstaller 配置参数
args = [
    script_path,           # 主脚本文件
    '--onefile',           # 打包为单个exe文件
    '--windowed',          # 隐藏控制台窗口（GUI程序）
    f'--icon={icon_path}', # 设置程序图标
    '--name=成都公交LCD模拟器', # 程序名称
    '--clean',             # 清理临时文件
    '--noconfirm',         # 覆盖输出目录不提示
    '--add-data=logo.ico;.', # 添加图标文件
]

# 执行打包
PyInstaller.__main__.run(args)