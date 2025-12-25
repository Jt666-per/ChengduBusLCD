import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from PIL import Image, ImageTk
import math
import re
import sys
import ctypes
import hashlib
import uuid
import platform
import json

class LicenseManager:
    """无权访问这个类别的说明"""
    
    def __init__(self):
        self.license_file = "license.dat"
        self.max_attempts = 3
        self.attempts = 0
        
        # 用户码列表（最多100个）
        self.blacklist = {
            "1111-1111-1111-1111"  # 初始
        }
        # 在此行添加，示例：self.blacklist.add("XXXX-XXXX-XXXX-XXXX")
        
    def check_blacklist(self, user_code):
        """检查"""
        return user_code in self.blacklist
    
    def get_machine_fingerprint(self):
        """获取机器指纹"""
        # 组合多种硬件信息
        machine_info = ""
        
        try:
            # 1. 计算机名
            machine_info += platform.node()
            
            # 2. MAC地址
            mac = uuid.getnode()
            machine_info += str(mac)
            
            # 3. 处理器信息
            if platform.system() == "Windows":
                import subprocess
                try:
                    # 获取处理器ID
                    cpu_info = subprocess.check_output(
                        'wmic cpu get ProcessorId', 
                        shell=True
                    ).decode().split('\n')[1].strip()
                    machine_info += cpu_info
                except:
                    machine_info += "unknown_cpu"
            else:
                # Linux/Mac
                machine_info += platform.processor()
                
            # 4. 系统信息
            machine_info += platform.machine()
            machine_info += platform.version()
            
        except Exception as e:
            # 如果获取失败，使用随机UUID
            machine_info = str(uuid.uuid4())
            
        # 使用SHA256哈希生成
        hash_object = hashlib.sha256(machine_info.encode())
        user_code = hash_object.hexdigest()[:16].upper()  # 取前16位大写
        
        # 格式化
        formatted_code = '-'.join([user_code[i:i+4] for i in range(0, 16, 4)])
        return formatted_code
    
    def generate_key_from_code(self, user_code):
        """？"""
        cleaned_code = user_code.replace('-', '')
        reversed_code = cleaned_code[::-1]
        offset = 7
        shifted_chars = []
        for char in cleaned_code:
            if char.isdigit():
                new_digit = (int(char) + offset) % 10
                shifted_chars.append(str(new_digit))
            else:
                new_char = chr((ord(char) - ord('A') + offset) % 26 + ord('A'))
                shifted_chars.append(new_char)
        shifted_code = ''.join(shifted_chars)
        combined = reversed_code + shifted_code + "BUS_DISPLAY_HD"
        key_hash = hashlib.sha256(combined.encode()).hexdigest()[:16].upper()
        formatted_key = '-'.join([key_hash[i:i+4] for i in range(0, 16, 4)])
        return formatted_key
    
    def verify_license(self):
        """验证"""
        user_code = self.get_machine_fingerprint()
        
        # 第一步：检查是否在“通缉”中
        if self.check_blacklist(user_code):
            messagebox.showerror(
                "您可能触碰了作者底线",
                "您使用之前的版本有违规行为且次数达上限，已限制您的使用权。\n\n"
                "如无异议，请停止使用并删除此程序所有拷贝；\n"
                "如有异议，请与作者联系。"
            )
            sys.exit(0) 
        
        # 第二步：是否存在有效的许可证文件
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    license_data = json.load(f)
                    
                stored_code = license_data.get('user_code', '')
                stored_key = license_data.get('license_key', '')
                if stored_code == user_code:
                    expected_key = self.generate_key_from_code(user_code)
                    if stored_key == expected_key:
                        return True  # 许可证有效
            except:
                # 文件损坏或格式错误
                pass
                
        # 第三步：运行到此步为首次启动
        return self.request_license_key(user_code)
    
    def request_license_key(self, user_code):
        """请求用户激活"""
        # 创建专门的用户码显示窗口
        code_window = tk.Tk()
        code_window.title("许可证验证 - 如不清楚如何操作请访问帮助文档")
        code_window.geometry("500x500")
        code_window.resizable(False, False)
        
        # 设置窗口居中
        code_window.update_idletasks()
        width = code_window.winfo_width()
        height = code_window.winfo_height()
        x = (code_window.winfo_screenwidth() // 2) - (width // 2)
        y = (code_window.winfo_screenheight() // 2) - (height // 2)
        code_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # 绑定窗口关闭事件 - 直接退出程序
        def on_closing():
            code_window.destroy()
            sys.exit(0)
        
        code_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 标题
        title_label = tk.Label(
            code_window,
            text="许可证验证",
            font=("微软雅黑", 14, "bold"),
            fg="#333333"
        )
        title_label.pack(pady=10)
        
        # 用户码显示区域
        frame_code = tk.Frame(code_window, relief=tk.RAISED, borderwidth=2)
        frame_code.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame_code,
            text="您的用户码：",
            font=("微软雅黑", 11),
            fg="#333333"
        ).pack(pady=(15, 5))
        
        # 用户码文本框（只读）
        user_code_var = tk.StringVar(value=user_code)
        entry_code = tk.Entry(
            frame_code,
            textvariable=user_code_var,
            font=("微软雅黑", 12, "bold"),
            justify='center',
            state='readonly',
            readonlybackground='white',
            fg="#333333",
            relief=tk.FLAT
        )
        entry_code.pack(pady=5, padx=20, fill=tk.X)
        
        # 复制按钮
        def copy_to_clipboard():
            code_window.clipboard_clear()
            code_window.clipboard_append(user_code)
            btn_copy.config(text="✓ 已复制")
            code_window.after(2000, lambda: btn_copy.config(text="复制到剪贴板"))
        
        btn_copy = tk.Button(
            frame_code,
            text="复制到剪贴板",
            command=copy_to_clipboard,
            bg="#3498DB",
            fg="white",
            font=("微软雅黑", 10),
            padx=20,
            pady=5
        )
        btn_copy.pack(pady=10)
        
        # 提示信息
        info_text = (
            "简要说明：请验证自己的信息，不要代替他人验证，每份订单仅能授权一个用户码。\n\n"
            "如果您是在哔哩哔哩工坊购买的，请联系创作者，发送这段用户码给作者，"
            "作者将在两天内回复您密钥。输入正确后永久激活。\n\n"
            "此密钥仅对此台电脑有效，如更换电脑（或其主要硬件），则激活失效需重新购买。"
            "密钥转发给他人无效。\n\n"
            "如果您不是通过此途径购买的本程序，则您已经被骗，您是盗版受害者。"
            "请尝试退款并向平台举报。"
        )
        
        info_label = tk.Label(
            code_window,
            text=info_text,
            font=("微软雅黑", 9),
            fg="#666666",
            justify=tk.LEFT,
            wraplength=450
        )
        info_label.pack(pady=10, padx=20)
        
        # 按钮框架
        btn_frame = tk.Frame(code_window)
        btn_frame.pack(pady=10)
        
        def continue_to_verify():
            code_window.destroy()
            self.enter_license_key(user_code)
        
        btn_continue = tk.Button(
            btn_frame,
            text="已得知密钥",
            command=continue_to_verify,
            bg="#27AE60",
            fg="white",
            font=("微软雅黑", 10, "bold"),
            padx=20,
            pady=8
        )
        btn_continue.pack(side=tk.LEFT, padx=5)
        
        btn_cancel = tk.Button(
            btn_frame,
            text="取消",
            command=on_closing,  # 直接退出程序
            font=("微软雅黑", 10),
            padx=20,
            pady=8
        )
        btn_cancel.pack(side=tk.LEFT, padx=5)
        
        # 运行窗口
        code_window.mainloop()
        
        # 如果窗口被关闭，返回False
        return False
    
    def enter_license_key(self, user_code):
        """输入"""
        temp_root = tk.Tk()
        temp_root.withdraw()  # 隐藏主窗口
        
        while self.attempts < self.max_attempts:
            # 使用simpledialog获取密钥
            license_key = simpledialog.askstring(
                "输入许可证密钥",
                f"用户码: {user_code}\n\n密钥（格式: XXXX-XXXX-XXXX-XXXX，连字符请自己打）:",
                parent=temp_root
            )
            
            if license_key is None:
                #接退出程序，不弹任何提示
                temp_root.destroy()
                sys.exit(0)
                
            # 验证密钥格式
            license_key = license_key.strip().upper()
            if not re.match(r'^[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$', license_key):
                self.attempts += 1
                remaining = self.max_attempts - self.attempts
                if remaining > 0:
                    messagebox.showerror(
                        "错误",
                        f"密钥格式错误！应为XXXX-XXXX-XXXX-XXXX格式（大写字母和数字）。\n"
                        f"剩余尝试次数: {remaining}"
                    )
                continue
                
            # 验证密钥
            expected_key = self.generate_key_from_code(user_code)
            if license_key == expected_key:
                # 保存许可证文件
                self.save_license(user_code, license_key)
                temp_root.destroy()
                
                # 显示成功信息并退出
                messagebox.showinfo(
                    "验证成功",
                    "密钥正确，由于高分屏适配问题，首次启动效果不佳，因此程序将退出。\n\n"
                    "麻烦您重新运行。后续以当前用户身份运行本程序且许可证文件未被移动删除，则无需验证。"
                )
                return True
            else:
                self.attempts += 1
                remaining = self.max_attempts - self.attempts
                if remaining > 0:
                    messagebox.showerror(
                        "错误",
                        f"密钥不对！\n剩余尝试次数: {remaining}"
                    )
                    
        # 超过最大尝试次数
        temp_root.destroy()
        messagebox.showerror(
            "验证失败",
            "验证失败次数过多，程序将退出。\n"
            "如果您确信已获得正确密钥，请删除本目录license.dat后重试。"
        )
        sys.exit(0)
    
    def save_license(self, user_code, license_key):
        """保存许可证文件"""
        license_data = {
            'user_code': user_code,
            'license_key': license_key,
            'save_time': platform.node()  # 保存计算机名用于调试
        }
        
        try:
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存许可证文件失败: {e}")

class BusDisplayApp:
    def __init__(self):
        # 首先验证许可证
        license_manager = LicenseManager()
        if not license_manager.verify_license():
            sys.exit(0)  # 验证失败，退出程序
        
        # 设置DPI感知，适应高分屏
        if os.name == 'nt':  # Windows
            try:
                # 设置进程DPI感知
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass  # 如果失败，继续使用默认设置
        
        # 获取屏幕尺寸和缩放因子
        self.screen_width = None
        self.screen_height = None
        self.scale_factor = self.get_windows_scaling()
        
        # 存储数据
        self.bus_number = ""
        self.stations = []
        self.photo_path = ""
        self.driver_name = ""
        self.star_rating = 3
        self.current_station_index = 0
        self.is_at_station = True
        self.display_mode = 0  # 0: 到站状态, 1: 完整线路, 2: 精简线路
        self.after_id = None
        
        # 根据PPT确定的颜色方案
        self.colors = {
            'area_a_bg': '#FFFFFF',  # 区域甲背景 - 白色
            'area_b_bg': '#595959',  # 区域乙背景 - 灰色
            'area_c_bg': '#ED7D31',  # 区域丙背景 - 橙色
            'destination_text': '#ED7D31',  # 开往文字 - 橙色
            'transfer_text': '#000000',     # 换乘提示 - 黑色
            'driver_info_text': '#FFFFFF',  # 车长信息 - 白色
            'next_station_text': '#FFFFFF', # 下一站文字 - 白色
            'bus_number_text': '#FFFFFF',   # 公交号码 - 白色
            'station_passed': '#CCCCCC',    # 已过站点 - 灰色
            'station_current': '#ED7D31',   # 当前站点 - 橙色
            'station_future': '#60B000',    # 前方站点 - 绿色
            'divider_orange': '#ED7D31',    # 分界线橙色部分
            'divider_green': '#60B000',     # 分界线绿色部分
            'side_door_text': '#FF0000'     # 对侧开门 - 红色
        }
        
        # 创建设置窗口A
        self.create_setup_window()
        
    def get_windows_scaling(self):
        """获取Windows缩放因子"""
        if os.name == 'nt':
            try:
                # 获取DPI缩放比例，适用于高分屏
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                dc = user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)  # 88 = LOGPIXELSX
                user32.ReleaseDC(0, dc)
                return dpi / 96.0
            except:
                return 1.0
        return 1.0
        
    def create_setup_window(self):
        """创建设置窗口A"""
        self.window_a = tk.Tk()
        self.window_a.title("成都公交风格车内LCD电显模拟设置-Bilibili@逐梦桃花源编写")
        
        # 根据缩放因子调整窗口大小
        base_width = 600
        base_height = 550
        scaled_width = int(base_width * self.scale_factor)
        scaled_height = int(base_height * self.scale_factor)
        self.window_a.geometry(f"{scaled_width}x{scaled_height}")
        self.window_a.resizable(True, True)
        
        # 设置程序图标
        try:
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe文件
                application_path = sys._MEIPASS
            else:
                # 如果是Python脚本
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, "logo.ico")
            if os.path.exists(icon_path):
                self.window_a.iconbitmap(icon_path)
        except Exception as e:
            print(f"无法加载图标: {e}")
        
        # 创建控件
        self.create_setup_widgets()
        
        # 添加版权信息
        copyright_label = tk.Label(
            self.window_a,
            text="全龄友好——幸福出行 注意：此风格主要用于主城区新能源公交。不同车有较小差异，请以实际为准。 警告：禁止将此软件用于散布谣言或商业宣传，由此产生的一切后果由使用者承担。违规达两次者将被限制使用。 声明：逐梦桃花源享有最终解释权。此软件几乎免费，后续如大家诚实守信，我将会去掉下载者登记环节并开源。 严禁商用。 二创及发布LCD有关画面需注明原作者。 您使用即表示您同意所有条款。在软件构建过程中，使用DeepSeek辅助。 当前版本：V1.0第一次公测版，如觉得好记得回去一键三连，遇bug希望您给作者反馈~",
            font=("微软雅黑", int(4 * self.scale_factor)),
            fg='gray',
            wraplength=int(480 * self.scale_factor)
        )
        copyright_label.pack(side='bottom', pady=int(5 * self.scale_factor))
        
    def create_setup_widgets(self):
        """创建设置窗口的控件"""
        # 标题
        title_label = tk.Label(
            self.window_a, 
            text="成都公交车车内LCD屏设置（屏幕在运行方向左侧）", 
            font=("微软雅黑", int(8 * self.scale_factor), "bold"),
            fg='#333333'
        )
        title_label.pack(pady=int(2 * self.scale_factor))
        
        # 公交线路号输入
        tk.Label(self.window_a, text="公交线路号码：", font=("微软雅黑", int(5 * self.scale_factor))).pack(pady=int(5 * self.scale_factor))
        self.bus_number_entry = tk.Entry(self.window_a, width=int(10 * self.scale_factor), font=("微软雅黑", int(6 * self.scale_factor)))
        self.bus_number_entry.pack(pady=int(2 * self.scale_factor))
        
        # 车长姓名输入
        tk.Label(self.window_a, text="车长姓名：", font=("微软雅黑", int(5 * self.scale_factor))).pack(pady=int(2 * self.scale_factor))
        self.driver_name_entry = tk.Entry(self.window_a, width=int(10 * self.scale_factor), font=("微软雅黑", int(6 * self.scale_factor)))
        self.driver_name_entry.pack(pady=int(2 * self.scale_factor))
        
        # 星级选择
        tk.Label(self.window_a, text="车长星级：", font=("微软雅黑", int(5 * self.scale_factor))).pack(pady=int(2 * self.scale_factor))
        self.star_var = tk.IntVar(value=3)
        
        star_frame = tk.Frame(self.window_a)
        star_frame.pack(pady=int(2 * self.scale_factor))
        
        tk.Radiobutton(star_frame, text="3★", variable=self.star_var, value=3, font=("微软雅黑", int(5 * self.scale_factor))).pack(side='left', padx=int(10 * self.scale_factor))
        tk.Radiobutton(star_frame, text="4★", variable=self.star_var, value=4, font=("微软雅黑", int(5 * self.scale_factor))).pack(side='left', padx=int(10 * self.scale_factor))
        tk.Radiobutton(star_frame, text="5★", variable=self.star_var, value=5, font=("微软雅黑", int(5 * self.scale_factor))).pack(side='left', padx=int(10 * self.scale_factor))
        
        # 插入照片按钮
        self.photo_button = tk.Button(
            self.window_a, 
            text="载入车长照片", 
            command=self.select_photo,
            width=int(7 * self.scale_factor),
            font=("微软雅黑", int(5 * self.scale_factor)),
            bg='#3498DB',
            fg='white'
        )
        self.photo_button.pack(pady=int(5 * self.scale_factor))
        self.photo_label = tk.Label(self.window_a, text="您好像啥都没选呢？程序仅在本地运行，不上传数据。", fg="gray", font=("微软雅黑", int(5 * self.scale_factor)))
        self.photo_label.pack()
        
        # 插入站点按钮
        self.station_button = tk.Button(
            self.window_a,
            text="载入站点文件",
            command=self.select_station_file,
            width=int(7 * self.scale_factor),
            font=("微软雅黑", int(5 * self.scale_factor)),
            bg='#3498DB',
            fg='white'
        )
        self.station_button.pack(pady=int(5 * self.scale_factor))
        self.station_label = tk.Label(self.window_a, text="该文件包含所运行方向所有站点，站名以换行符分隔。", fg="gray", font=("微软雅黑", int(5 * self.scale_factor)))
        self.station_label.pack()
        
        # 开始展示按钮
        self.start_button = tk.Button(
            self.window_a,
            text="开始展示",
            command=self.start_display,
            bg="#27AE60",
            fg="white",
            width=int(8 * self.scale_factor),
            height=2,
            font=("微软雅黑", int(6 * self.scale_factor), "bold")
        )
        self.start_button.pack(pady=int(10 * self.scale_factor))
        
    def select_photo(self):
        """选择车长照片"""
        file_path = filedialog.askopenfilename(
            title="选择车长大头照（建议为红底3：4比例）",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            # 检查图片是否能正常打开
            try:
                with Image.open(file_path) as img:
                    img.verify()  # 验证图片是否损坏
                
                # 重新打开图片检查比例
                image = Image.open(file_path)
                width, height = image.size
                expected_ratio = 3/4
                actual_ratio = width/height
                
                # 允许一定的误差范围
                if abs(actual_ratio - expected_ratio) > 0.05:  # 5%的误差范围
                    result = messagebox.askokcancel(
                        "图片比例失调", 
                        "图片并非标准证件照长宽比例(3:4)，将被拉伸，请问是否继续？"
                    )
                    if not result:
                        # 用户取消，重新选择
                        self.select_photo()
                        return
                    else:
                        # 用户确认，继续使用
                        self.photo_path = file_path
                        filename = os.path.basename(file_path)
                        self.photo_label.config(text=filename, fg="black")
                else:
                    # 比例正常
                    self.photo_path = file_path
                    filename = os.path.basename(file_path)
                    self.photo_label.config(text=filename, fg="black")
                    
            except Exception as e:
                messagebox.showerror("我们都有不顺利的时候", f"图片文件已损坏或无打开权限: {str(e)}\n请重新选择图片。")
                # 重新选择图片
                self.select_photo()
                return
            
    def select_station_file(self):
        """选择站点文件"""
        file_path = filedialog.askopenfilename(
            title="站点文件（要求格式：一个站名空一行，快捷获取方法见使用说明）",
            filetypes=[("文本文件", "*.txt")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # 检查文件行数
                    lines = content.strip().split('\n')
                    if len(lines) < 2:
                        messagebox.showwarning(
                            "文件格式警告", 
                            "站点数过少。请以换行分隔站名。站名列表快速获取方法请见使用指南。"
                        )
                        return
                    
                    # 合并所有行并分割站点
                    content = ' '.join([line.strip() for line in lines])
                    # 使用多种分隔符分割
                    self.stations = re.split(r'[ ,;，；\s]+', content)
                    # 过滤空字符串
                    self.stations = [station for station in self.stations if station]
                    
                # 检查站点数量
                if len(self.stations) > 90:
                    messagebox.showerror("噫，出错了", "哪里有超过90个站的线路啊！司机怕憋尿都憋出问题了！")
                    self.stations = []
                    return
                elif len(self.stations) > 48:
                    messagebox.showwarning("站点数量警告", "线路站点较多，将影响显示效果。")
                
                # 检查每个站名的长度
                for station in self.stations:
                    if len(station) > 20:
                        messagebox.showerror("这年轻人卧槽牛逼！", f"站名\"{station}\"超过20个汉字")
                        self.stations = []
                        return
                    
                if self.stations:
                    self.station_label.config(
                        text=f"已加载 {len(self.stations)} 个站点", 
                        fg="black"
                    )
                else:
                    self.station_label.config(text="文件为空", fg="red")
                    
            except Exception as e:
                messagebox.showerror("这不是你的问题，也不是我的问题", f"读取文件失败: {str(e)}，请尝试关掉其他占用应用。")
                self.station_label.config(text="读取失败", fg="red")
                
    def validate_inputs(self):
        """验证输入数据"""
        self.bus_number = self.bus_number_entry.get().strip()
        self.driver_name = self.driver_name_entry.get().strip()
        self.star_rating = self.star_var.get()
        
        # 验证公交线路号
        if not self.bus_number:
            messagebox.showerror("错误", "你号码搞忘输了！例：K11,东1")
            return False
            
        if len(self.bus_number) > 6:
            messagebox.showerror("错误", "线路号码长度不超过6个字符。")
            return False
            
        # 验证车长姓名
        if not self.driver_name:
            messagebox.showerror("错误", "车长难道没有取名字？！")
            return False
            
        # 只允许汉字和·
        if not re.match(r'^[\u4e00-\u9fa5·]+$', self.driver_name):
            messagebox.showerror("错误", "车长姓名只能输入汉字和·")
            return False
            
        if len(self.driver_name) > 11:
            messagebox.showerror("错误", "太长了吧，车长姓名不超过11个汉字。")
            return False
            
        if not self.photo_path:
            messagebox.showerror("错误", "可车长总得有张照片吧！")
            return False
            
        if not os.path.exists(self.photo_path):
            messagebox.showerror("错误", "选择的照片文件不存在。")
            return False
            
        if not self.stations:
            messagebox.showerror("错误", "请选择并加载站点文件。")
            return False
            
        # 验证图片文件
        try:
            with Image.open(self.photo_path) as img:
                img.verify()
        except Exception as e:
            messagebox.showerror("麻烦大了", f"图片文件已损坏或格式不支持: {str(e)}")
            return False
            
        return True
        
    def start_display(self):
        """开始展示"""
        if self.validate_inputs():
            self.window_a.withdraw()  # 隐藏设置窗口
            self.create_display_window()  # 创建展示窗口
            self.create_control_window()  # 创建控制窗口
            
    def create_display_window(self):
        """创建展示窗口B"""
        # 获取屏幕尺寸
        self.screen_width = self.window_a.winfo_screenwidth()
        # 修复：使用更大的高度比例，从0.25改为0.3
        self.screen_height = int(self.screen_width * 0.3)
        
        # 创建无边框窗口
        self.window_b = tk.Toplevel()
        self.window_b.title("电脑上开公交LCD屏")
        self.window_b.geometry(f"{self.screen_width}x{self.screen_height}")
        self.window_b.overrideredirect(True)  # 无边框
        
        # 设置窗口位置（顶部居中）
        x = 0
        y = 0
        self.window_b.geometry(f"+{x}+{y}")
        
        # 绑定ESC键退出
        self.window_b.bind('<Escape>', lambda e: self.close_display())
        
        # 创建显示内容
        self.create_display_content()
        
        # 初始状态为到站状态
        self.update_display()
        
    def create_display_content(self):
        """创建显示内容"""
        # 区域甲（上1/4，左3/4）- 白色背景
        self.area_a = tk.Frame(
            self.window_b, 
            bg=self.colors['area_a_bg'], 
            width=int(self.screen_width * 0.75),
            height=int(self.screen_height * 0.25)
        )
        self.area_a.place(x=0, y=0)
        
        # 区域乙（下3/4，左3/4）- 灰色背景
        self.area_b = tk.Frame(
            self.window_b, 
            bg=self.colors['area_b_bg'], 
            width=int(self.screen_width * 0.75),
            height=int(self.screen_height * 0.75)
        )
        self.area_b.place(x=0, y=int(self.screen_height * 0.25))
        
        # 区域丙（右侧1/4）- 橙色背景
        self.area_c = tk.Frame(
            self.window_b, 
            bg=self.colors['area_c_bg'], 
            width=int(self.screen_width * 0.25),
            height=self.screen_height
        )
        self.area_c.place(x=int(self.screen_width * 0.75), y=0)
        
        # 绘制甲乙区域分界线
        self.draw_divider_line()
        
        # 初始化各区域内容
        self.init_area_a()
        self.init_area_c()
        
    def draw_divider_line(self):
        """绘制甲乙区域分界线 - 使用平行四边形"""
        canvas_width = int(self.screen_width * 0.75)
        line_y = int(self.screen_height * 0.25)
        
        # 创建画布绘制分界线
        divider_canvas = tk.Canvas(
            self.window_b,
            width=canvas_width,
            height=20,  # 增加高度以容纳平行四边形
            bg='white',
            highlightthickness=0
        )
        divider_canvas.place(x=0, y=line_y-10)  # 调整位置
        
        # 橙色平行四边形（占左侧2/3，在边界线下方）
        orange_length = int(canvas_width * 2/3)
        # 向右倾斜的平行四边形
        divider_canvas.create_polygon(
            0, 20,           # 左下
            orange_length, 20,  # 右下
            orange_length+10, 0, # 右上
            10, 0,            # 左上
            fill=self.colors['divider_orange'],
            outline=self.colors['divider_orange']
        )
        
        # 绿色平行四边形（占右侧1/3，在边界线上方）
        green_start = orange_length
        green_length = canvas_width - orange_length
        # 向右倾斜的平行四边形
        divider_canvas.create_polygon(
            green_start+10, 0,           # 左上
            green_start+green_length+10, 0,  # 右上
            green_start+green_length, 20, # 右下
            green_start, 20,        # 左下
            fill=self.colors['divider_green'],
            outline=self.colors['divider_green']
        )
        
    def init_area_a(self):
        """初始化区域A内容"""
        # 开往终点站文字位于左上角
        if self.stations:
            destination = self.stations[-1]  # 倒数第一个为终点站
            
            # 处理长终点站名
            if len(destination) > 14:
                display_destination = destination[:13] + "…"
            else:
                display_destination = destination
                
            # 创建开往标签
            self.destination_label = tk.Label(
                self.area_a,
                text=f"开往 {display_destination}",
                font=("微软雅黑", int(12 * self.scale_factor), "bold"),
                bg=self.colors['area_a_bg'],
                fg=self.colors['destination_text'],
                anchor='w'
            )
            self.destination_label.place(x=int(15 * self.scale_factor), y=int(12 * self.scale_factor))
        
        # 换乘提示位于右侧
        self.transfer_label = tk.Label(
            self.area_a,
            text="换乘提示：",
            font=("微软雅黑", int(8 * self.scale_factor)),
            bg=self.colors['area_a_bg'],
            fg=self.colors['transfer_text'],
            anchor='w'
        )
        # 位于右侧
        self.transfer_label.place(relx=0.6, y=int(14 * self.scale_factor))
        
    def init_area_c(self):
        """初始化区域C内容"""
        # 车长信息区域（上半部分）
        info_frame = tk.Frame(
            self.area_c,
            bg=self.colors['area_c_bg'],
            width=int(self.screen_width * 0.25),
            height=int(self.screen_height * 1)
        )
        info_frame.pack(pady=int(10 * self.scale_factor))
        info_frame.pack_propagate(False)
        
        # 本车车长
        tk.Label(
            info_frame,
            text="本车车长：",
            font=("微软雅黑", int(10 * self.scale_factor)),
            bg=self.colors['area_c_bg'],
            fg=self.colors['driver_info_text']
        ).pack(anchor='w', padx=int(10 * self.scale_factor), pady=(int(5 * self.scale_factor), 0))
        
        # 车长姓名
        tk.Label(
            info_frame,
            text=self.driver_name,
            font=("微软雅黑", int(10 * self.scale_factor)),
            bg=self.colors['area_c_bg'],
            fg=self.colors['driver_info_text']
        ).pack(anchor='w', padx=int(10 * self.scale_factor), pady=(int(5 * self.scale_factor), 0))
        
        # 星级
        tk.Label(
            info_frame,
            text="星级：",
            font=("微软雅黑", int(10 * self.scale_factor)),
            bg=self.colors['area_c_bg'],
            fg=self.colors['driver_info_text']
        ).pack(anchor='w', padx=int(10 * self.scale_factor), pady=(int(5 * self.scale_factor), 0))
        
        # 绘制多少颗星星
        stars = "★" * self.star_rating
        tk.Label(
            info_frame,
            text=stars,
            font=("微软雅黑", int(10 * self.scale_factor)),
            bg=self.colors['area_c_bg'],
            fg=self.colors['driver_info_text']  # 改为白色
        ).pack(anchor='w', padx=int(10 * self.scale_factor), pady=(int(5 * self.scale_factor), 0))
        
        # 车长照片区域位于右上角
        photo_frame = tk.Frame(
            self.area_c,
            bg=self.colors['area_c_bg'],  # 使用橙色背景
            width=int(135* self.scale_factor),  # 根据PPT调整大小
            height=int(180 * self.scale_factor)  # 3:4比例
        )
        photo_frame.place(relx=0.5, y=int(10 * self.scale_factor))
        photo_frame.pack_propagate(False)
        
        # 加载并显示照片（3:4比例）
        try:
            image = Image.open(self.photo_path)
            # 调整图片大小为3:4比例
            target_width = int(135 * self.scale_factor)
            target_height = int(180 * self.scale_factor) 
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            photo_label = tk.Label(photo_frame, image=photo, bg=self.colors['area_c_bg'])
            photo_label.image = photo  # 保持引用
            photo_label.pack(pady=int(5 * self.scale_factor))
            
        except Exception as e:
            error_label = tk.Label(
                photo_frame,
                text="照片被\n外星人\n劫走了",
                fg='red',
                bg=self.colors['area_c_bg'],
                font=("微软雅黑", int(8 * self.scale_factor)),
                justify='center'
            )
            error_label.pack(expand=True)
        
        # 下一站信息区域 - 修复：放在照片下方
        self.next_station_frame = tk.Frame(
            self.area_c,
            bg=self.colors['area_c_bg'],
            width=int(self.screen_width * 0.25),
            height=int(self.screen_height * 0.4)
        )
        photo_bottom = int(10 * self.scale_factor) + int(120 * self.scale_factor)
        self.next_station_frame.place(x=0, y=photo_bottom + int(80 * self.scale_factor))
        
        # 下一站文字容器
        self.next_station_container = tk.Frame(
            self.next_station_frame,
            bg=self.colors['area_c_bg']
        )
        self.next_station_container.pack(pady=(int(20 * self.scale_factor), int(10 * self.scale_factor)))
        
        # 下一站前缀
        self.next_station_prefix = tk.Label(
            self.next_station_container,
            text=" 下一站 ",
            font=("微软雅黑", int(11 * self.scale_factor), "bold"),
            bg=self.colors['area_c_bg'],
            fg=self.colors['next_station_text']
        )
        self.next_station_prefix.pack(side='left')
        
        # 下一站站名
        self.next_station_name = tk.Label(
            self.next_station_container,
            text="",
            font=("微软雅黑", int(11 * self.scale_factor), "bold"),
            bg=self.colors['area_c_bg'],
            fg=self.colors['next_station_text']
        )
        self.next_station_name.pack(side='left')
        
        # 公交线路号（大字号）
        self.bus_number_label = tk.Label(
            self.next_station_frame,
            text=" "+self.bus_number,
            font=("微软雅黑", int(30 * self.scale_factor), "bold"),
            bg=self.colors['area_c_bg'],
            fg=self.colors['bus_number_text']
        )
        self.bus_number_label.pack(side='left')
        
    def update_next_station_display(self):
        """更新下一站显示 - 修复逻辑错误"""
        if self.is_at_station:
            # 到站状态 - 显示已到达当前站
            station_name = self.stations[self.current_station_index]
            # 处理长站名（超过7个字加...）
            if len(station_name) > 7:
                display_name = station_name[:6] + "…"
            else:
                display_name = station_name
                
            self.next_station_prefix.config(text=" 已到达 ")
            self.next_station_name.config(text=display_name)
        else:
            # 行驶状态 - 显示下一站
            # 下一站就是当前站点索引指向的站点
            next_station = self.stations[self.current_station_index]
            # 处理长站名（超过7个字加...）
            if len(next_station) > 7:
                display_name = next_station[:6] + "…"
            else:
                display_name = next_station
                #只要代码跑对了千万别动它
            self.next_station_prefix.config(text=" 下一站 ")
            self.next_station_name.config(text=display_name)
                
    def update_display(self):
        """更新乙区域显示"""
        # 清除乙区域所有内容
        for widget in self.area_b.winfo_children():
            widget.destroy()
            
        # 取消之前的定时器
        if self.after_id:
            self.window_b.after_cancel(self.after_id)
            self.after_id = None
            
        # 在乙区域右上角添加"对侧开门"
        side_door_label = tk.Label(
            self.area_b,
            text="对侧开门",
            font=("微软雅黑", int(9 * self.scale_factor)),
            bg=self.colors['area_b_bg'],
            fg=self.colors['side_door_text']
        )
        side_door_label.place(relx=0.95, y=int(10 * self.scale_factor), anchor='ne')
            
        if self.is_at_station:
            # 到站状态显示
            self.show_arrival_display()
        else:
            # 行驶状态显示
            if len(self.stations) <= 5:
                # 站点少于等于5个，只显示完整线路
                self.show_full_route_display()
            else:
                # 站点多于5个，轮换显示
                if self.display_mode == 1:
                    self.show_full_route_display()
                    self.after_id = self.window_b.after(20000, self.switch_display_mode)  # 20秒后切换
                else:
                    self.show_simplified_route_display()
                    self.after_id = self.window_b.after(20000, self.switch_display_mode)  # 20秒后切换
        
        # 更新下一站显示
        self.update_next_station_display()
        
    def switch_display_mode(self):
        """切换显示模式"""
        self.display_mode = 2 if self.display_mode == 1 else 1
        self.update_display()
        
    def show_arrival_display(self):
        """显示到站状态 - 乙区域显示"xxx 到了"和橙色圆角矩形"""
        station_name = self.stations[self.current_station_index]
        
        # 显示"xxx 到了"
        arrival_label = tk.Label(
            self.area_b,
            text=f"{station_name} 到了",
            font=("微软雅黑", int(18 * self.scale_factor), "bold"),
            bg=self.colors['area_b_bg'],
            fg='#4CAF50'  # 绿色
        )
        arrival_label.place(relx=0.5, rely=0.3, anchor='center')

        # 绘制橙色圆角矩形
        canvas_width = int(self.screen_width * 0.75)
        canvas_height = int(self.screen_height * 0.75)
        
        canvas = tk.Canvas(
            self.area_b,
            width=1200,
            height=150,
            bg=self.colors['area_b_bg'],  # 使用乙区域背景色
            highlightthickness=0
        )
        canvas.place(relx=0.5, rely=0.6, anchor='center')
        
        # 绘制圆角矩形 - 修复：使用正确的圆角矩形绘制方法
        self.create_round_rect(canvas, 0, 100, 1200, 150, 50, fill='#ED7D31', outline='')
        
    def create_round_rect(self, canvas, x1, y1, x2, y2, radius=50, **kwargs):
        """创建圆角矩形"""
        points = [x1+radius, y1,
                 x1+radius, y1,
                 x2-radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1+radius,
                 x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)
        
    def show_full_route_display(self):
        """显示完整线路"""
        canvas_width = int(self.screen_width * 0.75)
        canvas_height = int(self.screen_height * 0.75)
        
        canvas = tk.Canvas(
            self.area_b,
            width=canvas_width,
            height=canvas_height,
            bg=self.colors['area_b_bg'],
            highlightthickness=0
        )
        canvas.pack()
        
        # 绘制橙色箭头的位置在分界线下方一点点
        arrow_y = int(25 * self.scale_factor)
        start_x = int(60 * self.scale_factor)  # 留出空间显示站点序号
        end_x = canvas_width - int(30 * self.scale_factor)

        # 箭头参数
        line_width = int(6 * self.scale_factor)
        arrow_length = int(80 * self.scale_factor)
        arrow_width = int(18 * self.scale_factor)

        # 绘制直线
        canvas.create_line(
            start_x, arrow_y, end_x, arrow_y,
            width=line_width,
            fill=self.colors['divider_orange']
        )

        # 在起点绘制橙色实心圆点
        circle_radius = line_width  # 半径与箭头宽度相同
        canvas.create_oval(
            start_x - circle_radius, arrow_y - circle_radius,
            start_x + circle_radius, arrow_y + circle_radius,
            fill=self.colors['divider_orange'],
            outline=''  # 无边框
        )

        # 在终点绘制单边箭头（只有上方）
        canvas.create_polygon(
            end_x + 45, arrow_y+5,
            end_x + 45 - arrow_length, arrow_y - arrow_width+5,
            end_x + 45 - arrow_length, arrow_y+5,
            fill=self.colors['divider_orange'],
            outline=self.colors['divider_orange']
        )
        
        # 计算站点间距
        station_count = len(self.stations)
        if station_count > 1:
            station_spacing = (end_x - start_x) / (station_count - 1)
        else:
            station_spacing = end_x - start_x
            
        # 绘制站点圆圈和站名
        for i, station in enumerate(self.stations):
            x = start_x + i * station_spacing
            circle_y = arrow_y + int(30 * self.scale_factor)
            
            # 确定圆圈颜色
            if i < self.current_station_index:
                # 已过站点 - 灰色
                circle_color = self.colors['station_passed']
                text_color = self.colors['station_passed']
            elif i == self.current_station_index:
                # 当前站点 - 橙色
                circle_color = self.colors['station_current']
                text_color = self.colors['station_current']
            else:
                # 前方站点 - 绿色
                circle_color = self.colors['station_future']
                text_color = self.colors['station_future']
                
            # 绘制圆圈 - 仅填充
            circle_radius = int(10 * self.scale_factor)
            canvas.create_oval(
                x - circle_radius, circle_y - circle_radius,
                x + circle_radius, circle_y + circle_radius,
                fill=circle_color,
                outline='',  # 无边框
                width=0
            )
            
            # 绘制序号（在圆圈内）
            canvas.create_text(
                x, circle_y,
                text=str(i+1),
                font=("微软雅黑", int(5 * self.scale_factor), "bold"),
                fill='white'
            )
            
            # 绘制站名（竖排）- 调整位置避免重叠
            text_y = circle_y + int(13 * self.scale_factor)#此处已改
            
            # 处理长站名
            if len(station) > 10:
                display_station = station[:9] + "…"
            else:
                display_station = station
                
            # 竖排显示，靠上对齐
            vertical_text = '\n'.join(display_station)
            canvas.create_text(
                x, text_y,
                text=vertical_text,
                font=("微软雅黑", int(6 * self.scale_factor)),
                fill=text_color,
                anchor='n',  # 靠上对齐
                justify='center'
            )
            
            # 如果是指向的站点，添加橙色边框（包括序号和站名）
            if i == self.current_station_index:
                # 计算站名高度（假设每个字高度为15，最多8个字）
                text_height = min(len(display_station), 8) * int(15 * self.scale_factor)
                box_height = int(230 * self.scale_factor)  # 高度固定到屏幕底部
                
                # 调整边框宽度为序号直径+4像素
                border_width = circle_radius * 2 + int(4 * self.scale_factor)
                canvas.create_rectangle(
                    x - circle_radius - int(2 * self.scale_factor), circle_y - circle_radius - int(20 * self.scale_factor),
                    x + circle_radius + int(2 * self.scale_factor), circle_y + box_height,
                    outline=self.colors['station_current'],
                    width=int(2 * self.scale_factor)
                )
                
    def show_simplified_route_display(self):
        """显示精简线路（只显示5个站）"""
        canvas_width = int(self.screen_width * 0.75)
        canvas_height = int(self.screen_height * 0.75)
        
        canvas = tk.Canvas(
            self.area_b,
            width=canvas_width,
            height=canvas_height,
            bg=self.colors['area_b_bg'],
            highlightthickness=0
        )
        canvas.pack()
        
        # 计算要显示的5个站点
        start_idx = max(0, self.current_station_index - 1)
        end_idx = min(len(self.stations), start_idx + 5)
        
        # 如果不足5个站，调整起始索引
        if end_idx - start_idx < 5:
            start_idx = max(0, end_idx - 5)
        
        displayed_stations = self.stations[start_idx:end_idx]
        displayed_indices = list(range(start_idx, end_idx))
        
        # 绘制线路 - 精简重复代码
        self.draw_arrow_line(canvas, canvas_width)
        
        # 计算站点间距
        start_x = int(60 * self.scale_factor)
        end_x = canvas_width - int(30 * self.scale_factor)
        arrow_y = int(25 * self.scale_factor)
        
        station_count = len(displayed_stations)
        if station_count > 1:
            station_spacing = (end_x - start_x) / (station_count - 1)
        else:
            station_spacing = end_x - start_x
            
        # 绘制站点
        for i, (station_idx, station) in enumerate(zip(displayed_indices, displayed_stations)):
            x = start_x + i * station_spacing
            circle_y = arrow_y + int(30 * self.scale_factor)
            
            # 确定圆圈颜色
            if station_idx < self.current_station_index:
                circle_color = self.colors['station_passed']
                text_color = self.colors['station_passed']
            elif station_idx == self.current_station_index:
                circle_color = self.colors['station_current']
                text_color = self.colors['station_current']
            else:
                circle_color = self.colors['station_future']
                text_color = self.colors['station_future']
                
            # 绘制圆圈 - 仅填充
            circle_radius = int(10 * self.scale_factor)
            canvas.create_oval(
                x - circle_radius, circle_y - circle_radius,
                x + circle_radius, circle_y + circle_radius,
                fill=circle_color,
                outline='',  # 无边框
                width=0
            )
            
            # 绘制序号
            canvas.create_text(
                x, circle_y,
                text=str(station_idx+1),
                font=("Arial", int(5 * self.scale_factor), "bold"),
                fill='white'
            )
            
            # 绘制站名
            text_y = circle_y + int(25 * self.scale_factor)
            
            # 处理长站名
            if len(station) > 10:
                display_station = station[:9] + "…"
            else:
                display_station = station
                
            vertical_text = '\n'.join(display_station)
            canvas.create_text(
                x, text_y,
                text=vertical_text,
                font=("微软雅黑", int(6 * self.scale_factor)),
                fill=text_color,
                anchor='n',  # 靠上对齐
                justify='center'
            )
            
            # 当前站点边框（包括序号和站名）
            if station_idx == self.current_station_index:
                # 计算站名高度
                text_height = min(len(display_station), 8) * int(15 * self.scale_factor)
                box_height = int(230 * self.scale_factor)  # 同上
                
                # 调整边框宽度为序号直径+4像素
                border_width = circle_radius * 2 + int(4 * self.scale_factor)
                canvas.create_rectangle(
                    x - circle_radius - int(2 * self.scale_factor), circle_y - circle_radius - int(20 * self.scale_factor),#边框上界与箭头重合
                    x + circle_radius + int(2 * self.scale_factor), circle_y + box_height,
                    outline=self.colors['station_current'],
                    width=int(2 * self.scale_factor)
                )
    
    def draw_arrow_line(self, canvas, canvas_width):
        """绘制箭头线路（精简重复代码）"""
        arrow_y = int(25 * self.scale_factor)
        start_x = int(60 * self.scale_factor)
        end_x = canvas_width - int(30 * self.scale_factor)

        # 箭头参数
        line_width = int(6 * self.scale_factor)
        arrow_length = int(80 * self.scale_factor)
        arrow_width = int(18 * self.scale_factor)

        # 绘制直线
        canvas.create_line(
            start_x, arrow_y, end_x, arrow_y,
            width=line_width,
            fill=self.colors['divider_orange']
        )

        # 在起点绘制橙色实心圆点
        circle_radius = line_width
        canvas.create_oval(
            start_x - circle_radius, arrow_y - circle_radius,
            start_x + circle_radius, arrow_y + circle_radius,
            fill=self.colors['divider_orange'],
            outline=''
        )

        # 在终点绘制单边箭头
        canvas.create_polygon(
            end_x + 50, arrow_y+5,
            end_x + 50 - arrow_length, arrow_y - arrow_width+5,
            end_x + 50 - arrow_length, arrow_y+5,
            fill=self.colors['divider_orange'],
            outline=self.colors['divider_orange']
        )
                
    def create_control_window(self):
        """创建控制窗口C"""
        self.window_c = tk.Toplevel()
        self.window_c.title("虚拟司机控制端")
        base_width = 450  
        base_height = 150  
        scaled_width = int(base_width * self.scale_factor)
        scaled_height = int(base_height * self.scale_factor)
        self.window_c.geometry(f"{scaled_width}x{scaled_height}")
        self.window_c.resizable(False, False)
        
        # 设置程序图标
        try:
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe文件
                application_path = sys._MEIPASS
            else:
                # 如果是Python脚本
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, "logo.ico")
            if os.path.exists(icon_path):
                self.window_c.iconbitmap(icon_path)
        except Exception as e:
            print(f"无法加载图标: {e}")
        
        # 设置窗口位置（在窗口B下方）
        x = self.window_b.winfo_x()
        y = self.window_b.winfo_y() + self.screen_height + int(10 * self.scale_factor)
        self.window_c.geometry(f"+{x}+{y}")
        
        # 绑定关闭事件
        self.window_c.protocol("WM_DELETE_WINDOW", self.close_display)
        
        # 创建控制按钮 
        button_frame = tk.Frame(self.window_c)
        button_frame.pack(expand=True, fill='both', padx=int(20 * self.scale_factor), pady=int(20 * self.scale_factor))
        
        self.arrival_button = tk.Button(
            button_frame,
            text="进站",
            command=self.arrival_station,
            bg="#4CAF50",
            fg="white",
            width=int(6 * self.scale_factor),
            height=2,  # 增加高度
            font=("微软雅黑", int(6 * self.scale_factor), "bold")
        )
        self.arrival_button.pack(side='left', expand=True, padx=int(20 * self.scale_factor))

        self.departure_button = tk.Button(
            button_frame,
            text="出站",
            command=self.departure_station,
            bg="#FF9800",
            fg="white",
            width=int(6 * self.scale_factor),
            height=2,  # 增加高度
            font=("微软雅黑", int(6 * self.scale_factor), "bold")
        )
        self.departure_button.pack(side='right', expand=True, padx=int(20 * self.scale_factor))
        
        # 检查并显示授权信息（如果已授权）
        license_file = "license.dat"
        if os.path.exists(license_file):
            try:
                with open(license_file, 'r', encoding='utf-8') as f:
                    license_data = json.load(f)
                    user_code = license_data.get('user_code', '')
                    if user_code:
                        # 显示授权信息
                        auth_label = tk.Label(
                            self.window_c,
                            text=f"此产品已授权给 {user_code}",
                            font=("微软雅黑", int(5 * self.scale_factor)),
                            fg='green',
                            bg='#F5F5F5',
                            wraplength=int(480 * self.scale_factor)
                        )
                        auth_label.pack(side='bottom', pady=int(2 * self.scale_factor))
            except:
                pass  # 如果文件读取失败，不显示
        # 添加版权信息
        copyright_label = tk.Label(
            self.window_c,
            text="逐梦桃花源享有著作权。供公交车迷兴趣交流，不是真实出行建议。",
            font=("微软雅黑", int(4 * self.scale_factor)),
            fg='gray',
            wraplength=int(280 * self.scale_factor)
        )
        copyright_label.pack(side='bottom', pady=int(5 * self.scale_factor))
        
        # 更新按钮初始状态
        self.update_button_states()
        
    def arrival_station(self):
        """进站操作"""
        self.is_at_station = True
        self.update_button_states()
        self.update_display()
        
    def departure_station(self):
        """出站操作"""
        self.is_at_station = False
        self.display_mode = 1  # 重置为完整线路显示模式
        
        # 移动到下一站
        if self.current_station_index < len(self.stations) - 1:
            self.current_station_index += 1
            
        self.update_button_states()
        self.update_display()
        
    def update_button_states(self):
        """更新按钮状态"""
        # 检查是否到达终点站
        is_at_last_station = (self.current_station_index == len(self.stations) - 1 and self.is_at_station)
        
        if is_at_last_station:
            # 到达终点站，禁用所有按钮
            self.arrival_button.config(state='disabled')
            self.departure_button.config(state='disabled')
        else:
            if self.is_at_station:
                # 到站状态：进站按钮禁用，出站按钮启用
                self.arrival_button.config(state='disabled')
                self.departure_button.config(state='normal')
            else:
                # 行驶状态：进站按钮启用，出站按钮禁用
                self.arrival_button.config(state='normal')
                self.departure_button.config(state='disabled')
        
    def close_display(self):
        """关闭展示窗口和控制窗口"""
        # 取消所有动画
        if self.after_id:
            self.window_b.after_cancel(self.after_id)
            
        if hasattr(self, 'window_b'):
            self.window_b.destroy()
        if hasattr(self, 'window_c'):
            self.window_c.destroy()
            
        # 重置运行状态为起点站
        self.current_station_index = 0
        self.is_at_station = True
        self.display_mode = 0
        self.window_a.deiconify()  # 重新显示设置窗口
        
    def run(self):
        """运行应用程序"""
        self.window_a.mainloop()

# 为Canvas添加圆角矩形方法
def create_round_rect(self, x1, y1, x2, y2, radius=50, **kwargs):
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]
    return self.create_polygon(points, **kwargs, smooth=True)

tk.Canvas.create_round_rect = create_round_rect

# 创建并运行应用
if __name__ == "__main__":
    app = BusDisplayApp()
    app.run()