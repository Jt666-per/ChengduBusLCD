import urllib.request
import json
import sys

def test_github_api():
    repo_owner = "Jt666-per"
    repo_name = "ChengduBusLCD"
    api_url_latest = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    print("=== GitHub更新检测诊断脚本 ===\n")
    
    # 1. 测试基础连接
    print("1. 测试基础连接到 api.github.com...")
    try:
        urllib.request.urlopen("https://api.github.com", timeout=5)
        print("   ✓ 连接成功\n")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
        print("   请检查网络、代理或防火墙设置。")
        return
    
    # 2. 测试仓库访问
    repo_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    print(f"2. 测试访问仓库 {repo_owner}/{repo_name}...")
    try:
        req = urllib.request.Request(repo_api_url, headers={'User-Agent': 'Diagnostic-Script'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print("   ✓ 仓库可公开访问\n")
            else:
                print(f"   ✗ 意外状态码: {response.status}\n")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"   ✗ 仓库未找到 (404)。请确认：")
            print(f"     - 用户名 '{repo_owner}' 是否正确？")
            print(f"     - 仓库名 '{repo_name}' 是否正确？")
            print(f"     - 仓库是否为公开(Public)状态？[citation:2]")
        else:
            print(f"   ✗ HTTP 错误: {e.code} {e.reason}")
        return
    except Exception as e:
        print(f"   ✗ 访问仓库失败: {e}")
        return
    
    # 3. 测试获取最新Release
    print("3. 测试获取最新 Release...")
    try:
        req = urllib.request.Request(api_url_latest, headers={'User-Agent': 'Diagnostic-Script'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                tag_name = data.get('tag_name', 'N/A')
                print(f"   ✓ 成功获取最新Release！")
                print(f"     标签名称: {tag_name}")
                print(f"     发布名称: {data.get('name', 'N/A')}")
                print(f"     创建时间: {data.get('created_at', 'N/A')}\n")
                print("结论：API地址和Release配置正确。请检查你主程序中版本号比对部分的代码。")
                return
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"   ✗ 未找到任何Release (404)。")
            print(f"     这意味着你尚未在GitHub上为此仓库创建过正式的'Release'。[citation:3]")
            print(f"     请登录GitHub，进入你的仓库：")
            print(f"     1. 点击顶部菜单的 'Releases'")
            print(f"     2. 点击 'Create a new release'")
            print(f"     3. 在 'Choose a tag' 中选择你的标签（如 V1.0beta），填写信息后发布。")
        else:
            print(f"   ✗ 获取Release失败，HTTP状态码: {e.code}")
    except Exception as e:
        print(f"   ✗ 获取Release时发生意外错误: {e}")

if __name__ == "__main__":
    test_github_api()
    input("\n按Enter键退出...")