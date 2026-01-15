import subprocess
import sys
import os

def run_command(command):
    """运行命令行命令"""
    print(f"执行命令: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ 命令执行成功")
        print(result.stdout)
    else:
        print("✗ 命令执行失败")
        print(result.stderr)
    return result.returncode

def main():
    python_path = r"D:\ProgramData\miniconda3\python.exe"
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 50)
    print("公交LCD模拟器构建脚本")
    print("=" * 50)
    
    # 1. 安装依赖
    print("\n1. 正在安装PyInstaller和Pillow...")
    install_cmd = f'"{python_path}" -m pip install pyinstaller pillow'
    if run_command(install_cmd) != 0:
        print("安装依赖失败，请手动安装：")
        print(f'打开命令行并运行: {install_cmd}')
        input("按Enter键退出...")
        return
    
    # 2. 清理旧的构建文件
    print("\n2. 清理旧的构建文件...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            import shutil
            shutil.rmtree(dir_name)
            print(f"✓ 已删除 {dir_name} 目录")
    
    # 删除spec文件
    spec_file = "公交LCD模拟器V1.1.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"✓ 已删除 {spec_file}")
    
    # 3. 打包程序
    print("\n3. 正在打包程序...")
    pyinstaller_cmd = (
        f'"{python_path}" -m PyInstaller --onedir --windowed '
        f'--icon=logo.ico --name="公交LCD模拟器V1.1" '
        f'--collect-all tkinter '
        f'--add-data="styles;styles" '
        f'--add-data="styles/resources;resources" '
        f'main.py'
    )
    
    if run_command(pyinstaller_cmd) == 0:
        print("\n" + "=" * 50)
        print("构建成功！")
        print(f"程序位置: {os.path.join(project_dir, 'dist', '公交LCD模拟器V1.1')}")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("构建失败，请检查错误信息")
        print("=" * 50)
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main()