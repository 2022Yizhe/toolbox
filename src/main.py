# 1. UI 层

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading


import service as service
import conf as dconf


class ToolboxApp:
    def __init__(self, master):
        self.master = master
        master.title("Python 图像文件工具箱")
        
        # 先设置初始尺寸（但不设置位置）
        master.geometry("900x600")  # 仅设置尺寸
        
        # 创建界面组件
        self.create_menu()
        self.create_toolbar()
        self.create_main_content()
        
        # 状态栏（必须先创建组件）
        self.status_bar = ttk.Label(master, text=" 就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 强制更新界面计算实际尺寸
        master.update_idletasks()  # 关键步骤！
        
        # 计算居中坐标
        window_width = master.winfo_width()
        window_height = master.winfo_height()
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 重新设置包含位置的geometry
        master.geometry(f"+{x}+{y}")

    def create_menu(self):
        # 菜单栏结构
        menubar = tk.Menu(self.master)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="退出", command=self.master.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_help)
        help_menu.add_command(label="使用建议", command=self.show_suggestion)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.master.config(menu=menubar)

    def create_toolbar(self):
        # 工具栏使用 Frame 容器
        toolbar = ttk.Frame(self.master, padding=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # 工具按钮
        self.btn1 = ttk.Button(toolbar, text="图像文件分类", command=self.display_script1)
        self.btn1.pack(side=tk.LEFT, padx=2)
        
        self.btn2 = ttk.Button(toolbar, text="同构目录合并", command=self.display_script2)
        self.btn2.pack(side=tk.LEFT, padx=2)

        self.btn3 = ttk.Button(toolbar, text="文件提取", command=self.display_script3)
        self.btn3.pack(side=tk.LEFT, padx=2)

        self.btn4 = ttk.Button(toolbar, text="删除目录", command=self.display_script4)
        self.btn4.pack(side=tk.LEFT, padx=2)

        # 分隔符
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
    def create_main_content(self):
        # 主内容区域使用 Notebook（标签页）
        self.notebook = ttk.Notebook(self.master)
        
        # 第一个标签页
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="参数设置")

        # 初始化显示第一个工具的配置参数
        self.create_settings1_ui(dconf.script1_conf)
        
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def clear_settings_ui(self):
        # 清除原先工具的所有组件
        for widget in self.tab1.winfo_children():
            widget.destroy()

    def create_settings1_ui(self, conf: dict):
        self.clear_settings_ui()

        # 图像源
        tk.Label(self.tab1, text="图像源路径:").grid(row=1, column=0, padx=20, pady=10)
        self.image_source_entry = tk.Entry(self.tab1, width=60)
        self.image_source_entry.grid(row=1, column=1, padx=20, pady=10)
        if conf["image_source"] is not None:
            self.image_source_entry.insert(0, conf["image_source"])

        # 模式分类路径
        tk.Label(self.tab1, text="缓存文件路径:").grid(row=2, column=0, padx=20, pady=10)
        self.mode_separated_entry = tk.Entry(self.tab1, width=60)
        self.mode_separated_entry.grid(row=2, column=1, padx=20, pady=10)
        if conf["mode_separated"] is not None:
            self.mode_separated_entry.insert(0, conf["mode_separated"])

        # 质量分类路径
        tk.Label(self.tab1, text="输出文件路径:").grid(row=3, column=0, padx=20, pady=10)
        self.quality_filtered_entry = tk.Entry(self.tab1, width=60)
        self.quality_filtered_entry.grid(row=3, column=1, padx=20, pady=10)
        if conf["quality_filtered"] is not None:
            self.quality_filtered_entry.insert(0, conf["quality_filtered"])

        # CPU 工作数量
        tk.Label(self.tab1, text=f"CPU 工作数量 ({dconf.get_cpu_workers()})").grid(row=4, column=0, padx=20, pady=10)
        self.cpu_workers_entry = tk.Entry(self.tab1, width=60)
        self.cpu_workers_entry.grid(row=4, column=1, padx=20, pady=10)
        if conf["CPU_workers"] is not None:
            self.cpu_workers_entry.insert(0, conf["CPU_workers"])

        # 复选框 - 按模式
        self.option1_var = tk.BooleanVar(value=False)    # 创建变量来指定复选框状态
        self.check_mode_var = tk.Checkbutton(self.tab1, text="按模式", variable=self.option1_var, command=None)
        self.check_mode_var.grid(row=5, column=0, columnspan=1, pady=0)

        # 复选框 - 按质量
        self.option2_var = tk.BooleanVar(value=True)
        self.check_quality_var = tk.Checkbutton(self.tab1, text="按质量 / KB", variable=self.option2_var, command=None)
        self.check_quality_var.grid(row=5, column=1, columnspan=1, pady=0)

        # 输入框 - 质量
        self.quality_entry = tk.Entry(self.tab1, width=8)
        self.quality_entry.grid(row=6, column=1, columnspan=1, pady=0)

        # 复选框 - 查重
        self.option3_var = tk.BooleanVar(value=True)
        self.check_duplicate_var = tk.Checkbutton(self.tab1, text="查重", variable=self.option3_var, command=None)
        self.check_duplicate_var.grid(row=7, column=0, columnspan=1, pady=10)

        # 复选框 - 清除缓存
        self.option4_var = tk.BooleanVar(value=True)
        self.check_clear_cache_var = tk.Checkbutton(self.tab1, text="清除缓存", variable=self.option4_var, command=None)
        self.check_clear_cache_var.grid(row=7, column=1, columnspan=1, pady=10)

        # 分类按钮 (监听点击分类操作，将参数传递给 filter_images_script)
        self.public_button = tk.Button(self.tab1, text="开始分类", command=self.filter_images_script)
        self.public_button.grid(row=8, column=0, padx=20, pady=20)

        # 进度条
        self.progressbar = ttk.Progressbar(self.tab1, orient="horizontal", length=640, mode="determinate")
        self.progressbar.grid(row=8, column=1, padx=20, pady=20)
        self.progressbar["value"] = 0  # 初始化进度条为 0

        # 进度任务信息标签
        self.progress_label = tk.Label(self.tab1, text="[-/-]")
        self.progress_label.grid(row=9, column=0, padx=10, pady=10)

        # 进度详细信息标签
        self.progress_detail_label = tk.Label(self.tab1, text="没有正在进行的任务")
        self.progress_detail_label.grid(row=9, column=1, padx=10, pady=10)



    def create_settings2_ui(self, conf):
        self.clear_settings_ui()

        # 目录 1
        tk.Label(self.tab1, text="待合并目录 1:").grid(row=1, column=0, padx=20, pady=10)
        self.source1_entry = tk.Entry(self.tab1, width=60)
        self.source1_entry.grid(row=1, column=1, padx=20, pady=10)
        if conf["src1"] is not None:
            self.source1_entry.insert(0, conf["src1"])
        
        # 目录 2
        tk.Label(self.tab1, text="待合并目录 2:").grid(row=2, column=0, padx=20, pady=10)
        self.source2_entry = tk.Entry(self.tab1, width=60)
        self.source2_entry.grid(row=2, column=1, padx=20, pady=10)
        if conf["src2"] is not None:
            self.source2_entry.insert(0, conf["src2"])

        # 合并目录
        tk.Label(self.tab1, text="合并输出目录:").grid(row=3, column=0, padx=20, pady=10)
        self.merge_entry = tk.Entry(self.tab1, width=60)
        self.merge_entry.grid(row=3, column=1, padx=20, pady=10)
        if conf["dst"] is not None:
            self.merge_entry.insert(0, conf["dst"])

        # 合并按钮 (监听点击合并操作，将参数传递给 merge_script)
        self.public_button = tk.Button(self.tab1, text="开始合并", command=self.merge_script)
        self.public_button.grid(row=4, column=0, padx=20, pady=20)

        # 进度条
        self.progressbar = ttk.Progressbar(self.tab1, orient="horizontal", length=640, mode="determinate")
        self.progressbar.grid(row=4, column=1, padx=20, pady=20)
        self.progressbar["value"] = 0  # 初始化进度条为 0

        # 进度任务信息标签
        self.progress_label = tk.Label(self.tab1, text="")
        self.progress_label.grid(row=5, column=0, padx=10, pady=10)

        # 进度详细信息标签
        self.progress_detail_label = tk.Label(self.tab1, text="没有正在进行的任务")
        self.progress_detail_label.grid(row=5, column=1, padx=10, pady=10)

    def create_settings3_ui(self, conf):
        self.clear_settings_ui()

        # 待提取目录
        tk.Label(self.tab1, text="待提取目录:").grid(row=1, column=0, padx=20, pady=10)
        self.source_entry = tk.Entry(self.tab1, width=60)
        self.source_entry.grid(row=1, column=1, padx=20, pady=10)
        if conf["src"] is not None:
            self.source_entry.insert(0, conf["src"])

        # 提取输出目录
        tk.Label(self.tab1, text="提取到目录:").grid(row=2, column=0, padx=20, pady=10)
        self.extract_entry = tk.Entry(self.tab1, width=60)
        self.extract_entry.grid(row=2, column=1, padx=20, pady=10)
        if conf["dst"] is not None:
            self.extract_entry.insert(0, conf["dst"])

        # 是否生成子目录
        tk.Label(self.tab1, text="提取到子文件夹:").grid(row=3, column=0, padx=20, pady=10)
        self.target_dir_entry = tk.Entry(self.tab1, width=60)
        self.target_dir_entry.grid(row=3, column=1, padx=20, pady=10)
        if conf["target_dir"] is not None:
            self.target_dir_entry.insert(0, conf["target_dir"])

        tk.Label(self.tab1, text="（留空则不生成子文件夹）").grid(row=4, column=1, padx=20, pady=0)

        # 提取按钮 (监听点击提取操作，将参数传递给 extract_script)
        self.public_button = tk.Button(self.tab1, text="开始提取", command=self.extract_script)
        self.public_button.grid(row=4, column=0, padx=20, pady=20)

        # 进度条
        self.progressbar = ttk.Progressbar(self.tab1, orient="horizontal", length=640, mode="determinate")
        self.progressbar.grid(row=4, column=1, padx=20, pady=20)
        self.progressbar["value"] = 0  # 初始化进度条为 0

        # 进度任务信息标签
        self.progress_label = tk.Label(self.tab1, text="")
        self.progress_label.grid(row=5, column=0, padx=10, pady=10)

        # 进度详细信息标签
        self.progress_detail_label = tk.Label(self.tab1, text="没有正在进行的任务")
        self.progress_detail_label.grid(row=5, column=1, padx=10, pady=10)

    def create_settings4_ui(self, conf):
        self.clear_settings_ui()

        # 待清除空文件夹路径
        tk.Label(self.tab1, text="待删除目录:").grid(row=1, column=0, padx=20, pady=10)
        self.target_entry = tk.Entry(self.tab1, width=60)
        self.target_entry.grid(row=1, column=1, padx=20, pady=10)
        if conf["target"] is not None:
            self.target_entry.insert(0, conf["target"])

        # 是否只清除空文件夹
        tk.Label(self.tab1, text="是否只清除空文件夹:").grid(row=2, column=0, padx=20, pady=10)
        self.only_empty_entry = tk.Entry(self.tab1, width=60)
        self.only_empty_entry.grid(row=2, column=1, padx=20, pady=10)
        if conf["only_empty"] is not None:
            self.only_empty_entry.insert(0, conf["only_empty"])

        tk.Label(self.tab1, text="（1 表示只清除空文件夹，0 表示删除所有文件夹）").grid(row=3, column=1, padx=20, pady=0)

        # 清除按钮 (监听点击清除操作，将参数传递给 delete_script)
        self.public_button = tk.Button(self.tab1, text="开始删除", command=self.delete_script)
        self.public_button.grid(row=4, column=0, padx=20, pady=20)

        # 进度条
        self.progressbar = ttk.Progressbar(self.tab1, orient="horizontal", length=640, mode="determinate")
        self.progressbar.grid(row=4, column=1, padx=20, pady=20)
        self.progressbar["value"] = 0  # 初始化进度条为 0

        # 进度任务信息标签
        self.progress_label = tk.Label(self.tab1, text="")
        self.progress_label.grid(row=5, column=0, padx=10, pady=10)

        # 进度详细信息标签
        self.progress_detail_label = tk.Label(self.tab1, text="没有正在进行的任务")
        self.progress_detail_label.grid(row=5, column=1, padx=10, pady=10)


    def show_help(self):
        # 显示帮助信息
        help_text = "这是一个由 yizhe2022 开发的 Python 图像文件工具箱，集成了一些工具和功能。\n"\
        "图像文件分类：按照图像格式（例如 JPG、PNG）、图像大小（例如以 500KB 为分界）将图像归类，同时进行图像去重（文件哈希值比对）。\n" \
        "同构目录合并：将两个目录合并为一个目录。\n" \
        "文件提取：将一个目录中的所有文件（例如 TXT、DOCX、PPT、RAR、JPG 等）向上提取到一个目录下。\n" \
        "目录删除：删除一个目录下所有内容，可选择只查找空的文件夹并进行删除。\n" \
        "希望对您能有所帮助！"
        messagebox.showinfo("帮助", help_text)
        self.status_bar.config(text=" 显示帮助信息")

    def show_suggestion(self):
        # 显示建议信息
        suggestion_text = "1. 请每次仅使用一项工具，多工具任务并行未经稳定性测试；\n" \
        "2. 请合理设置 CPU 参数，全核心并行对主机散热稳定性要求较高。\n"\
        "\n注：本工具不会对源路径下的文件造成任何损坏，其原理是先复制到 .cache 目录下，再进行处理。\n" \
        "\n如果您在使用过程中遇到任何问题，或者有任何建议或意见，请随时联系。项目地址：\n" \
        "https://github.com/2022Yizhe/toolbox.git\n"
        messagebox.showinfo("使用建议", suggestion_text)
        self.status_bar.config(text=" 显示建议信息")

    # 展示脚本 1 布局
    def display_script1(self):
        self.status_bar.config(text=" 当前工具: 图像文件分类")

        # 添加标签和文本框
        self.create_settings1_ui(dconf.script1_conf)

    def display_script2(self):
        self.status_bar.config(text=" 当前工具: 同构目录合并")
        
        # 添加标签和文本框
        self.create_settings2_ui(dconf.script2_conf)

    def display_script3(self):
        self.status_bar.config(text=" 当前工具: 文件提取")

        # 添加标签和文本框
        self.create_settings3_ui(dconf.script3_conf)

    def display_script4(self):
        self.status_bar.config(text=" 当前工具: 目录删除")
        
        # 添加标签和文本框
        self.create_settings4_ui(dconf.script4_conf)


    def check_progress(self, serv: service.Service):
        if serv.get_processing():
            # 更新进度显示
            result = serv.get_result()
            if result is not None:
                if result["total_jobs"] != 0:
                    self.progressbar["value"] = result["processed"] / result["total_jobs"] * 100
                if result["current_task"] != "":
                    self.progress_label["text"] = f"[{result['current_task']}]"
                if result["total_jobs"] != 0:
                    self.progress_detail_label["text"] = f"{result['processed']}/{result['total_jobs']}：{result['current_job']}"
            # 继续定期检查
            self.master.after(100, lambda: self.check_progress(serv))  # 每 100 毫秒检查一次
        else:
            self.enable_button()    # 恢复按钮和样式


    def filter_images_script(self):
        # 禁用按钮并改变样式
        self.disable_button()

        # 获取组件值
        image_source = self.image_source_entry.get()
        mode_separated = self.mode_separated_entry.get()
        quality_filtered = self.quality_filtered_entry.get()
        cpu_workers = self.cpu_workers_entry.get()

        by_quality = self.option2_var.get()
        quality_boundary = self.quality_entry.get()

        conf = {
            'by_mode': self.option1_var.get(),  # 获取复选框值
            'by_quality': by_quality,
            'cls_duplicate': self.option3_var.get(),
            'cls_cache': self.option4_var.get(),

            'quality_boundary': quality_boundary
        }

        # 检查是否所有参数都已输入
        if image_source == "" or mode_separated == "" or quality_filtered == "" or cpu_workers == "" or (quality_boundary == "" and by_quality == 1):
            messagebox.showerror("错误", "请输入所有参数！")
            self.enable_button()    # 恢复按钮和样式
            return

        # 开始一个新线程来执行过滤
        serv = service.Service()
        threading.Thread(target=serv.start_filter, args=(image_source, mode_separated, quality_filtered, cpu_workers, conf)).start()

        # 启动定期检查进度
        serv.set_processing()
        self.progressbar["value"] = 0   # 清空进度条
        self.check_progress(serv)

    def merge_script(self):
        # 禁用按钮并改变样式
        self.disable_button()

        # 获取组件值
        src1 = self.source1_entry.get()
        src2 = self.source2_entry.get()
        dst = self.merge_entry.get()

        # 检查是否所有参数都已输入
        if src1 == "" or src2 == "" or dst == "":
            messagebox.showerror("错误", "请输入所有参数！")
            self.enable_button()    # 恢复按钮和样式
            return

        # 创建服务实例并调用方法
        serv = service.Service()
        threading.Thread(target=serv.start_merge, args=(src1, src2, dst)).start()

        # 启动定期检查进度
        serv.set_processing()
        self.progressbar["value"] = 0   # 清空进度条
        self.check_progress(serv)
        


    def extract_script(self):
        # 禁用按钮并改变样式
        self.disable_button()

        # 获取组件值
        src = self.source_entry.get()
        dst = self.extract_entry.get()
        target_dir = self.target_dir_entry.get()

        # 检查是否所有参数都已输入
        if src == "" or dst == "":
            messagebox.showerror("错误", "请输入所有参数！")
            self.enable_button()    # 恢复按钮和样式
            return

        if target_dir == "":
            target_dir = None

        # 创建服务实例并调用方法
        serv = service.Service()
        threading.Thread(target=serv.start_extract, args=(src, dst, target_dir)).start()

        # 启动定期检查进度
        serv.set_processing()
        self.progressbar["value"] = 0   # 清空进度条
        self.check_progress(serv)        

    def delete_script(self):
        # 禁用按钮并改变样式
        self.disable_button()

        # 获取组件值
        target = self.target_entry.get()
        only_empty = self.only_empty_entry.get()

        # 检查是否所有参数都已输入
        if target == "":
            messagebox.showerror("错误", "请输入所有参数！")
            self.enable_button()    # 恢复按钮和样式
            return

        # 创建服务实例并调用方法
        serv = service.Service()
        threading.Thread(target=serv.start_delete, args=(target, only_empty)).start()

        # 启动定期检查进度
        serv.set_processing()
        self.progressbar["value"] = 0   # 清空进度条
        self.check_progress(serv)     

    def disable_button(self):
        # 禁用按钮并改变样式
        self.public_button.config(
            state=tk.DISABLED,
            bg="#EEEEEE",       # 禁用时背景色 dark gray
            relief=tk.SUNKEN    # 凹陷效果
        )

    def enable_button(self):
        # 恢复按钮和样式
        self.public_button.config(
            state=tk.NORMAL,
            bg="#F5F5F5",   # light gray
            relief=tk.RAISED
        )


# ==============================================================================================


import ctypes

# 在创建 Tk 实例前调用
ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 系统级 DPI 感知

if __name__ == "__main__":
    root = tk.Tk()
    
    # 替换默认字体
    default_font = ("Consolas", 9)  # Windows 推荐
    root.option_add("*Font", default_font)

    app = ToolboxApp(root)
    root.mainloop()