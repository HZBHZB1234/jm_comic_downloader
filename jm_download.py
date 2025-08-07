import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import jmcomic
import json
import os
import threading
from time import sleep
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
# 创建配置对象
print('导入JMComic模块...')
if not os.path.exists('setting.yml'):
    jmcomic.JmOption.default().to_file('setting.yml')
option = jmcomic.create_option_by_file('setting.yml')
jmoption = jmcomic.JmOption.default()
client = jmoption.build_jm_client()
print('JMComic客户端加载完成')

class JMComicDownloaderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JMComic下载器")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('微软雅黑', 10), padding=5)
        self.style.configure('TLabel', background='#f0f0f0', font=('微软雅黑', 10))
        self.style.configure('Treeview', font=('微软雅黑', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('微软雅黑', 10, 'bold'))
        
        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建搜索区域
        self.create_search_section()
        
        # 创建结果区域
        self.create_results_section()
        
        # 创建日志区域
        self.create_log_section()
        
        # 初始化搜索参数
        self.init_search_params()
        
        # 绑定事件
        self.category_combo.bind("<<ComboboxSelected>>", self.update_subcategory)
    
    def init_search_params(self):
        """初始化搜索参数"""
        # 排序方式
        self.sort_options = {
            "最新": jmcomic.JmMagicConstants.ORDER_BY_LATEST,
            "最热": jmcomic.JmMagicConstants.ORDER_BY_VIEW,
            "最多图片": jmcomic.JmMagicConstants.ORDER_BY_PICTURE,
            "最多收藏": jmcomic.JmMagicConstants.ORDER_BY_LIKE
        }
        
        # 时间段
        self.time_options = {
            "全部": jmcomic.JmMagicConstants.TIME_ALL,
            "今天": jmcomic.JmMagicConstants.TIME_TODAY,
            "本周": jmcomic.JmMagicConstants.TIME_WEEK,
            "本月": jmcomic.JmMagicConstants.TIME_MONTH
        }
        
        # 主分类
        self.category_options = {
            "全部": jmcomic.JmMagicConstants.CATEGORY_ALL,
            "同人": jmcomic.JmMagicConstants.CATEGORY_DOUJIN,
            "单本": jmcomic.JmMagicConstants.CATEGORY_SINGLE,
            "短篇": jmcomic.JmMagicConstants.CATEGORY_SHORT,
            "其他": jmcomic.JmMagicConstants.CATEGORY_ANOTHER,
            "韩漫": jmcomic.JmMagicConstants.CATEGORY_HANMAN,
            "美漫": jmcomic.JmMagicConstants.CATEGORY_MEIMAN,
            "COSPLAY": jmcomic.JmMagicConstants.CATEGORY_DOUJIN_COSPLAY,
            "3D": jmcomic.JmMagicConstants.CATEGORY_3D,
            "英文站": jmcomic.JmMagicConstants.CATEGORY_ENGLISH_SITE
        }
        
        # 副分类
        self.subcategory_options = {
            "全部": "",
            "汉化": jmcomic.JmMagicConstants.SUB_CHINESE,
            "日语": jmcomic.JmMagicConstants.SUB_JAPANESE,
            "CG": jmcomic.JmMagicConstants.SUB_DOUJIN_CG,
            "青年": jmcomic.JmMagicConstants.SUB_SINGLE_YOUTH,
            "其他": jmcomic.JmMagicConstants.SUB_ANOTHER_OTHER
        }
        
        # 设置下拉框选项
        self.sort_combo['values'] = list(self.sort_options.keys())
        self.time_combo['values'] = list(self.time_options.keys())
        self.category_combo['values'] = list(self.category_options.keys())
        self.subcategory_combo['values'] = list(self.subcategory_options.keys())
        
        # 设置默认值
        self.sort_combo.current(0)
        self.time_combo.current(0)
        self.category_combo.current(0)
        self.subcategory_combo.current(0)
    
    def create_search_section(self):
        """创建搜索区域"""
        search_frame = ttk.LabelFrame(self.main_frame, text="搜索设置")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 搜索关键词
        ttk.Label(search_frame, text="搜索关键词:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 排序方式
        ttk.Label(search_frame, text="排序方式:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.sort_combo = ttk.Combobox(search_frame, width=12, state="readonly")
        self.sort_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # 时间段
        ttk.Label(search_frame, text="时间段:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.time_combo = ttk.Combobox(search_frame, width=10, state="readonly")
        self.time_combo.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # 分类
        ttk.Label(search_frame, text="主分类:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.category_combo = ttk.Combobox(search_frame, width=10, state="readonly")
        self.category_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 副分类
        ttk.Label(search_frame, text="副分类:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.subcategory_combo = ttk.Combobox(search_frame, width=10, state="readonly")
        self.subcategory_combo.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        
        # 搜索按钮
        self.search_btn = ttk.Button(search_frame, text="搜索", command=self.start_search)
        self.search_btn.grid(row=1, column=5, padx=5, pady=5, sticky=tk.E)
        
        # 页面控制
        ttk.Label(search_frame, text="页码:").grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)
        self.page_var = tk.StringVar(value="1")
        self.page_entry = ttk.Entry(search_frame, width=5, textvariable=self.page_var)
        self.page_entry.grid(row=1, column=5, padx=(0, 100), pady=5, sticky=tk.W)
    
    def create_results_section(self):
        """创建结果区域"""
        results_frame = ttk.LabelFrame(self.main_frame, text="搜索结果")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建树状视图
        columns = ("id", "title", "tags")
        self.results_tree = ttk.Treeview(
            results_frame, 
            columns=columns, 
            show="headings",
            selectmode="extended"
        )
        
        # 设置列
        self.results_tree.heading("id", text="ID", anchor=tk.W)
        self.results_tree.heading("title", text="标题", anchor=tk.W)
        self.results_tree.heading("tags", text="标签", anchor=tk.W)
        
        # 设置列宽
        self.results_tree.column("id", width=80, minwidth=80)
        self.results_tree.column("title", width=400, minwidth=200)
        self.results_tree.column("tags", width=300, minwidth=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # 下载按钮区域
        btn_frame = ttk.Frame(results_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        self.download_selected_details_btn = ttk.Button(
            btn_frame, 
            text="下载选中详情", 
            command=self.download_selected_comic_detail,
            state=tk.DISABLED
        )
        self.download_selected_details_btn.pack(side=tk.LEFT, padx=5)
        
        # 下载本页全部详情按钮
        self.download_all_details_btn = ttk.Button(
            btn_frame, 
            text="下载本页全部详情", 
            command=self.download_all_comic_details,
            state=tk.DISABLED
        )
        self.download_all_details_btn.pack(side=tk.LEFT, padx=5)
        # 下载选中按钮
        self.download_selected_btn = ttk.Button(
            btn_frame, 
            text="下载选中", 
            command=self.download_selected,
            state=tk.DISABLED
        )
        self.download_selected_btn.pack(side=tk.LEFT, padx=5)
        
        # 下载全部按钮
        self.download_all_btn = ttk.Button(
            btn_frame, 
            text="下载本页全部", 
            command=self.download_all,
            state=tk.DISABLED
        )
        self.download_all_btn.pack(side=tk.LEFT, padx=5)
        # 删除选中按钮
        self.delete_selected_btn = ttk.Button(
            btn_frame, 
            text="删除选中", 
            command=self.delete_selected,
            state=tk.DISABLED
        )
        self.delete_selected_btn.pack(side=tk.LEFT, padx=5)
        # 清空结果按钮
        self.clear_btn = ttk.Button(
            btn_frame, 
            text="清空结果", 
            command=self.clear_results
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
         # 导入结果按钮
        self.import_btn = ttk.Button(
            btn_frame, 
            text="导入列表", 
            command=self.import_list_from_file
        )
        self.import_btn.pack(side=tk.RIGHT, padx=5)
        # 导入结果按钮
        self.export_btn = ttk.Button(
            btn_frame, 
            text="导出列表", 
            command=self.export_list_to_file
        )
        self.export_btn.pack(side=tk.RIGHT, padx=5)
    def create_log_section(self):
        """创建日志区域"""
        log_frame = ttk.LabelFrame(self.main_frame, text="操作日志")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            font=('微软雅黑', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.configure(state=tk.DISABLED)
    
    def update_subcategory(self, event=None):
        """根据主分类更新副分类选项"""
        category = self.category_combo.get()
        
        # 重置副分类
        self.subcategory_combo['values'] = list(self.subcategory_options.keys())
        self.subcategory_combo.current(0)
    
    def log_message(self, message):
        """在日志区域添加消息"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def start_search(self):
        """开始搜索"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("输入错误", "请输入搜索关键词")
            return
        
        try:
            page = int(self.page_var.get())
            if page < 1:
                raise ValueError
        except:
            messagebox.showwarning("输入错误", "页码必须是正整数")
            return
        
        # 获取搜索参数
        sort_key = self.sort_combo.get()
        time_key = self.time_combo.get()
        category_key = self.category_combo.get()
        subcategory_key = self.subcategory_combo.get()
        
        # 映射到实际值
        order_by = self.sort_options.get(sort_key, jmcomic.JmMagicConstants.ORDER_BY_LATEST)
        time = self.time_options.get(time_key, jmcomic.JmMagicConstants.TIME_ALL)
        category = self.category_options.get(category_key, jmcomic.JmMagicConstants.CATEGORY_ALL)
        subcategory = self.subcategory_options.get(subcategory_key, "")
        
        self.log_message(f"开始搜索: {keyword} (第{page}页)")
        self.log_message(f"排序: {sort_key}, 时间: {time_key}, 分类: {category_key}, 副分类: {subcategory_key}")
        
        # 在新线程中执行搜索
        threading.Thread(
            target=self.perform_search,
            args=(keyword, page, order_by, time, category, subcategory),
            daemon=True
        ).start()
    
    def perform_search(self, keyword, page, order_by, time, category, subcategory):
        """执行搜索操作"""
        try:
            # 更新UI状态
            self.search_btn.configure(state=tk.DISABLED)
            
            search_page = client.search(
                keyword,
                page,
                0,
                order_by,
                time,
                category,
                subcategory
            )
            
            self.log_message(f"搜索完成: 共 {search_page.total} 条结果, {search_page.page_count} 页")
            
            # 清空现有结果
            self.results_tree.delete(*self.results_tree.get_children())
            
            # 添加新结果
            for album_id, title, tags in search_page.iter_id_title_tag():
                tag_str = ", ".join(tags)
                self.results_tree.insert("", tk.END, values=(album_id, title, tag_str))
            
            # 更新按钮状态
            self.download_selected_btn.configure(state=tk.NORMAL)
            self.download_all_btn.configure(state=tk.NORMAL)
            self.download_selected_details_btn.configure(state=tk.NORMAL)
            self.download_all_details_btn.configure(state=tk.NORMAL)
            self.delete_selected_btn.configure(state=tk.NORMAL)

        except Exception as e:
            self.log_message(f"搜索出错: {str(e)}")
        finally:
            self.search_btn.configure(state=tk.NORMAL)
    
    def clear_results(self):
        """清空搜索结果"""
        self.results_tree.delete(*self.results_tree.get_children())
        self.download_selected_btn.configure(state=tk.DISABLED)
        self.download_all_btn.configure(state=tk.DISABLED)
        self.download_selected_details_btn.configure(state=tk.DISABLED)
        self.download_all_details_btn.configure(state=tk.DISABLED)
        self.delete_selected_btn.configure(state=tk.DISABLED)
        self.log_message("已清空搜索结果")
    def export_list_to_file(self):
        """导出列表到文件"""
        from tkinter import filedialog
        
        # 检查是否有数据可以导出
        items = self.results_tree.get_children()
        if not items:
            messagebox.showinfo("导出失败", "没有可导出的数据")
            return
        
        # 打开文件保存对话框
        file_path = filedialog.asksaveasfilename(
            title="保存列表文件",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # 根据文件扩展名选择导出方式
            if file_path.endswith('.json'):
                self._export_to_json(file_path)
            elif file_path.endswith('.txt'):
                self._export_to_txt(file_path)
            else:
                # 默认使用JSON格式
                self._export_to_json(file_path)
                
            self.log_message(f"成功导出列表文件: {os.path.basename(file_path)}")
            messagebox.showinfo("导出成功", f"列表已成功导出到:\n{file_path}")
            
        except Exception as e:
            error_msg = f"导出列表时出错: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("导出失败", error_msg)

    def _export_to_json(self, file_path):
        """导出到JSON文件"""
        data = []
        
        # 收集所有数据
        for item in self.results_tree.get_children():
            values = self.results_tree.item(item, "values")
            if values:
                # 解析标签
                tags_str = values[2] if len(values) > 2 else ""
                tags = tags_str.split(", ") if tags_str else []
                
                data.append({
                    "id": values[0],
                    "title": values[1],
                    "tags": tags
                })
        
        # 写入JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _export_to_txt(self, file_path):
        """导出到TXT文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            # 写入表头
            f.write("ID,标题,标签\n")
            
            # 写入数据
            for item in self.results_tree.get_children():
                values = self.results_tree.item(item, "values")
                if values:
                    # 转义逗号和换行符
                    escaped_values = [str(v).replace(',', '，').replace('\n', '\\n') for v in values]
                    line = ','.join(escaped_values)
                    f.write(line + '\n')
    def import_list_from_file(self):
        """从文件导入列表"""
        from tkinter import filedialog
        
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title="选择要导入的列表文件",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # 根据文件扩展名选择解析方式
            if file_path.endswith('.json'):
                self._import_from_json(file_path)
            elif file_path.endswith('.txt'):
                self._import_from_txt(file_path)
            else:
                messagebox.showwarning("导入失败", "不支持的文件格式")
                return
                
            self.log_message(f"成功导入列表文件: {os.path.basename(file_path)}")
            
        except Exception as e:
            error_msg = f"导入列表时出错: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("导入失败", error_msg)

    def _import_from_json(self, file_path):
        """从JSON文件导入列表"""
        import json
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 清空现有结果
        self.results_tree.delete(*self.results_tree.get_children())
        
        # 检查数据格式
        if isinstance(data, list):
            # 格式1: 直接包含漫画信息的列表
            for item in data:
                comic_id = item.get('id', '')
                title = item.get('title', '未知标题')
                tags = item.get('tags', [])
                tag_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
                self.results_tree.insert("", tk.END, values=(comic_id, title, tag_str))
        elif isinstance(data, dict) and 'albums' in data:
            # 格式2: 包含albums键的字典
            for item in data['albums']:
                comic_id = item.get('id', '')
                title = item.get('title', '未知标题')
                tags = item.get('tags', [])
                tag_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
                self.results_tree.insert("", tk.END, values=(comic_id, title, tag_str))
        else:
            raise ValueError("不支持的JSON格式")
        
        # 更新按钮状态
        if self.results_tree.get_children():
            self.download_selected_btn.configure(state=tk.NORMAL)
            self.download_all_btn.configure(state=tk.NORMAL)
            self.download_selected_details_btn.configure(state=tk.NORMAL)
            self.download_all_details_btn.configure(state=tk.NORMAL)
            self.delete_selected_btn.configure(state=tk.NORMAL)

    def _import_from_txt(self, file_path):
        """从TXT文件导入列表"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 清空现有结果
        self.results_tree.delete(*self.results_tree.get_children())
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 尝试解析行数据 (格式: id,title,tags)
            parts = line.split(',', 2)
            if len(parts) >= 2:
                comic_id = parts[0]
                title = parts[1]
                tag_str = parts[2] if len(parts) > 2 else ""
                self.results_tree.insert("", tk.END, values=(comic_id, title, tag_str))
            else:
                # 只有ID的情况
                self.results_tree.insert("", tk.END, values=(line, "未知标题", ""))
        
        # 更新按钮状态
        if self.results_tree.get_children():
            self.download_selected_btn.configure(state=tk.NORMAL)
            self.download_all_btn.configure(state=tk.NORMAL)
            self.download_selected_details_btn.configure(state=tk.NORMAL)
            self.download_all_details_btn.configure(state=tk.NORMAL)
            self.delete_selected_btn.configure(state=tk.NORMAL)
    def download_selected(self):
        """下载选中的项目"""
        selected_items = self.results_tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要下载的项目")
            return
        
        ids = []
        for item in selected_items:
            values = self.results_tree.item(item, "values")
            if values:
                ids.append(values[0])
        
        if not ids:
            return
        
        self.log_message(f"开始下载选中的 {len(ids)} 个项目...")
        threading.Thread(
            target=self.download_albums,
            args=(ids,),
            daemon=True
        ).start()
    
    def download_all(self):
        """下载当前页所有项目"""
        all_items = self.results_tree.get_children()
        if not all_items:
            return
        
        ids = []
        for item in all_items:
            values = self.results_tree.item(item, "values")
            if values:
                ids.append(values[0])
        
        if not ids:
            return
        
        self.log_message(f"开始下载本页全部 {len(ids)} 个项目...")
        threading.Thread(
            target=self.download_albums,
            args=(ids,),
            daemon=True
        ).start()
    
    def download_selected_comic_detail(self):
        """下载选中的漫画详情"""
        if not os.path.exists('details'):
            os.mkdir('details')
        
        selected_items = self.results_tree.selection()
        if not selected_items:
            messagebox.showwarning("下载失败", "请先选择漫画")
            self.log_message("下载选中详情失败: 未选择漫画")
            return
        
        # 收集任务
        tasks = []
        for item in selected_items:
            values = self.results_tree.item(item, "values")
            if values and values[0]:
                comic_id = str(values[0])
                comic_title = str(values[1])
                tasks.append((comic_id, comic_title))
        
        if not tasks:
            messagebox.showwarning("下载失败", "选中的漫画无效")
            return

        # 禁用按钮
        self.download_selected_details_btn.config(state=tk.DISABLED)
        self.download_all_details_btn.config(state=tk.DISABLED)
        self.log_message(f"开始下载选中的 {len(tasks)} 个漫画详情...")
        
        # 使用线程池下载
        threading.Thread(
            target=self._download_multiple_comics_detail,
            args=(tasks,),
            daemon=True
        ).start()
    
    def download_all_comic_details(self):
        """下载当前页所有漫画详情"""
        if not os.path.exists('details'):
            os.mkdir('details')
        
        all_items = self.results_tree.get_children()
        if not all_items:
            messagebox.showwarning("下载失败", "当前没有搜索结果")
            return
        
        # 收集任务
        tasks = []
        for item in all_items:
            values = self.results_tree.item(item, "values")
            if values and values[0]:
                comic_id = str(values[0])
                comic_title = str(values[1])
                tasks.append((comic_id, comic_title))
        
        if not tasks:
            messagebox.showwarning("下载失败", "没有有效的漫画ID")
            return
        
        # 确认下载
        confirm = messagebox.askyesno(
            "确认下载", 
            f"确定要下载所有漫画详情吗？\n\n共 {len(tasks)} 个漫画"
        )
        if not confirm:
            return
        
        # 禁用按钮
        self.download_selected_details_btn.config(state=tk.DISABLED)
        self.download_all_details_btn.config(state=tk.DISABLED)
        self.log_message(f"开始下载全部 {len(tasks)} 个漫画详情...")
        
        # 使用线程池下载
        threading.Thread(
            target=self._download_multiple_comics_detail,
            args=(tasks,),
            daemon=True
        ).start()
    
    def _download_multiple_comics_detail(self, tasks):
        """后台线程执行批量下载任务（15线程并发）"""
        try:
            # 创建线程池（最大15个线程）
            with ThreadPoolExecutor(max_workers=15) as executor:
                future_to_task = {}
                
                # 提交所有任务到线程池
                for task in tasks:
                    comic_id, comic_title = task
                    future = executor.submit(
                        self._download_single_comic_detail, 
                        comic_id, 
                        comic_title
                    )
                    future_to_task[future] = (comic_id, comic_title)
                
                # 跟踪进度
                completed = 0
                total = len(tasks)
                failed = []
                
                # 等待任务完成并更新状态
                for future in as_completed(future_to_task):
                    comic_id, comic_title = future_to_task[future]
                    
                    try:
                        success, error = future.result()
                        if success:
                            self.root.after(0, lambda cid=comic_id, ct=comic_title: 
                                self.log_message(f"详情下载完成: {ct} (ID: {cid})"))
                        else:
                            failed.append((comic_id, comic_title, error))
                            self.root.after(0, lambda cid=comic_id, ct=comic_title, e=error: 
                                self.log_message(f"详情下载失败: {ct} - {e}"))
                    except Exception as e:
                        failed.append((comic_id, comic_title, str(e)))
                        self.root.after(0, lambda cid=comic_id, ct=comic_title, e=str(e): 
                            self.log_message(f"详情下载异常: {ct} - {e}"))
                    
                    completed += 1
                    self.root.after(0, lambda c=completed, t=total: 
                        self.log_message(f"详情下载中: {c}/{t} 已完成"))
            
            # 全部完成
            self.root.after(0, lambda: self.log_message(
                f"批量下载详情完成! 成功: {total - len(failed)}, 失败: {len(failed)}"
            ))
            
            # 如果有失败的任务，显示错误报告
            if failed:
                error_report = "\n".join([f"ID: {f[0]}, 标题: {f[1]}, 错误: {f[2]}" for f in failed])
                self.root.after(0, lambda: messagebox.showwarning(
                    "部分详情下载失败", 
                    f"以下 {len(failed)} 个漫画详情下载失败:\n\n{error_report}"
                ))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"批量下载详情异常: {str(e)}"))
        finally:
            # 重新启用按钮
            self.root.after(0, lambda: [
                self.download_selected_details_btn.config(state=tk.NORMAL),
                self.download_all_details_btn.config(state=tk.NORMAL)
            ])
    
    def _download_single_comic_detail(self, comic_id, comic_title):
        """下载单个漫画详情（供线程池使用）"""
        try:
            option = jmcomic.JmOption.default()
            client = option.new_jm_client()
            details_path = "details\\"
            os.makedirs(details_path, exist_ok=True)
            
            # 调用下载函数
            return download_detail(client, comic_id, comic_id, details_path)
        except Exception as e:
            return False, str(e)
    
    def download_albums(self, album_ids):
        """下载相册"""
        try:
            # 下载每个相册
            for album_id in album_ids:
                try:
                    self.log_message(f"开始下载相册: {album_id}")
                    jmcomic.download_album(int(album_id), option)
                    self.log_message(f"相册 {album_id} 下载完成")
                except Exception as e:
                    self.log_message(f"下载相册 {album_id} 时出错: {str(e)}")
            
            self.log_message("所有下载任务已完成")
            
        except Exception as e:
            self.log_message(f"下载过程中出错: {str(e)}")
    
    def delete_selected(self):
        """删除选中的项目"""
        selected_items = self.results_tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要删除的项目")
            return
        
        # 确认删除
        count = len(selected_items)
        # 删除选中的项目
        for item in selected_items:
            self.results_tree.delete(item)
        
        # 如果没有剩余项目，禁用下载按钮
        if not self.results_tree.get_children():
            self.download_selected_btn.configure(state=tk.DISABLED)
            self.download_all_btn.configure(state=tk.DISABLED)
            self.download_selected_details_btn.configure(state=tk.DISABLED)
            self.download_all_details_btn.configure(state=tk.DISABLED)
            self.delete_selected_btn.configure(state=tk.DISABLED)
        
        self.log_message(f"已删除 {count} 个项目")

def download_detail(client, id, album_id, path):
    """下载漫画详情和封面"""
    try:
        download_detail_album(client, id, album_id, path)
        download_detail_cover(client, id, album_id, path)
        return True, None
    except Exception as e:
        return False, str(e)

def download_detail_album(client, id, album_id, path):
    """下载漫画详情JSON"""
    # 获取漫画详情
    album: jmcomic.JmAlbumDetail = client.get_album_detail(album_id)
    album_json = {
        'id': album.album_id,
        'title': album.title,
        'author': album.author,
        'description': album.description,
        'tags': album.tags,
        'comment_count': album.comment_count,
        'likes': album.likes,
        'works': album.works,
        'related_list': album.related_list,
    }
    
    # 确保目录存在
    json_path = os.path.join(path, str(id))
    os.makedirs(json_path, exist_ok=True)
    
    # 保存JSON文件
    with open(os.path.join(json_path, 'album.json'), 'w', encoding='utf-8') as f:
        json.dump(album_json, f, ensure_ascii=False, indent=4)

def download_detail_cover(client, id, album_id, path):
    """下载漫画封面"""
    # 获取章节详情
    photo: jmcomic.JmPhotoDetail = client.get_photo_detail(album_id)
    
    # 获取第一张图片作为封面
    if len(photo) > 0:
        first_image: jmcomic.JmImageDetail = photo[0]
        cover_path = os.path.join(path, str(id), 'cover.png')
        client.download_by_image_detail(first_image, cover_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = JMComicDownloaderUI(root)
    root.mainloop()