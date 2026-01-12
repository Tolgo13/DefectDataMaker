"""
白黒反転タブ
PNGファイルの白黒を反転するUIコンポーネント
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from typing import List, Optional
from PIL import Image, ImageTk

from ..psd_processor import PNGInverter
from .styles import COLORS, FONTS, SPACING


class InverterTab(ttk.Frame):
    """白黒反転タブ"""
    
    def __init__(self, parent):
        super().__init__(parent, style='Dark.TFrame')
        
        self.inverter = PNGInverter()
        self.png_files: List[str] = []
        self.current_image: Optional[Image.Image] = None
        self.current_index: int = 0
        self.preview_size = (250, 250)
        
        self._create_widgets()
        self._layout_widgets()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダー
        self.header_frame = ttk.Frame(self, style='Dark.TFrame')
        self.title_label = ttk.Label(
            self.header_frame,
            text="白黒反転",
            style='Title.TLabel'
        )
        self.subtitle_label = ttk.Label(
            self.header_frame,
            text="PNGファイルの白黒を反転します",
            style='Subtitle.TLabel'
        )
        
        # メインコンテンツ
        self.main_frame = ttk.Frame(self, style='Dark.TFrame')
        
        # 左側: ファイル選択
        self.left_frame = self._create_card_frame_in(self.main_frame, "入力ファイル")
        self.left_content = ttk.Frame(self.left_frame, style='Card.TFrame')
        
        self.input_path_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            self.left_content,
            textvariable=self.input_path_var,
            width=40,
        )
        
        self.btn_input_frame = ttk.Frame(self.left_content, style='Card.TFrame')
        self.btn_select_files = ttk.Button(
            self.btn_input_frame,
            text="📄 ファイル選択",
            style='Outline.TButton',
            command=self._select_files
        )
        self.btn_select_folder = ttk.Button(
            self.btn_input_frame,
            text="📁 フォルダ選択",
            style='Outline.TButton',
            command=self._select_folder
        )
        
        # ファイルリスト
        self.file_listbox = tk.Listbox(
            self.left_content,
            height=12,
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'],
            selectforeground=COLORS['text_primary'],
            font=(FONTS['family'], FONTS['size_normal']),
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS['border'],
        )
        self.file_listbox.bind('<<ListboxSelect>>', self._on_file_select)
        
        self.file_scroll = ttk.Scrollbar(
            self.left_content,
            orient='vertical',
            command=self.file_listbox.yview
        )
        self.file_listbox.configure(yscrollcommand=self.file_scroll.set)
        
        self.file_count_label = ttk.Label(
            self.left_content,
            text="ファイル数: 0",
            style='Card.TLabel'
        )
        
        # 中央: プレビュー
        self.center_frame = self._create_card_frame_in(self.main_frame, "プレビュー")
        self.center_content = ttk.Frame(self.center_frame, style='Card.TFrame')
        
        self.preview_frame = ttk.Frame(self.center_content, style='Card.TFrame')
        
        # 元画像プレビュー
        self.original_frame = ttk.Frame(self.preview_frame, style='Card.TFrame')
        self.original_label = ttk.Label(
            self.original_frame,
            text="元画像",
            style='Card.TLabel'
        )
        self.original_canvas = tk.Canvas(
            self.original_frame,
            width=self.preview_size[0],
            height=self.preview_size[1],
            bg=COLORS['bg_light'],
            highlightthickness=0,
        )
        
        # 矢印
        self.arrow_label = ttk.Label(
            self.preview_frame,
            text="↓",
            style='Card.TLabel',
            font=(FONTS['family'], FONTS['size_xlarge']),
        )
        
        # 反転画像プレビュー
        self.inverted_frame = ttk.Frame(self.preview_frame, style='Card.TFrame')
        self.inverted_label = ttk.Label(
            self.inverted_frame,
            text="反転後",
            style='Card.TLabel'
        )
        self.inverted_canvas = tk.Canvas(
            self.inverted_frame,
            width=self.preview_size[0],
            height=self.preview_size[1],
            bg=COLORS['bg_light'],
            highlightthickness=0,
        )
        
        # 右側: 出力設定
        self.right_frame = self._create_card_frame_in(self.main_frame, "出力設定")
        self.right_content = ttk.Frame(self.right_frame, style='Card.TFrame')
        
        self.output_mode_var = tk.StringVar(value="overwrite")
        self.mode_overwrite = ttk.Radiobutton(
            self.right_content,
            text="上書き保存",
            variable=self.output_mode_var,
            value="overwrite",
        )
        self.mode_new_folder = ttk.Radiobutton(
            self.right_content,
            text="別フォルダに保存",
            variable=self.output_mode_var,
            value="new_folder",
        )
        
        self.output_folder_frame = ttk.Frame(self.right_content, style='Card.TFrame')
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(
            self.output_folder_frame,
            textvariable=self.output_path_var,
            width=30,
        )
        self.btn_select_output = ttk.Button(
            self.output_folder_frame,
            text="📁",
            style='Outline.TButton',
            command=self._select_output,
            width=3
        )
        
        # アクションボタン
        self.action_frame = ttk.Frame(self, style='Dark.TFrame')
        self.progress_bar = ttk.Progressbar(
            self.action_frame,
            mode='determinate',
            length=300
        )
        self.progress_label = ttk.Label(
            self.action_frame,
            text="",
            style='TLabel'
        )
        self.btn_invert = ttk.Button(
            self.action_frame,
            text="🔄 反転実行",
            style='Primary.TButton',
            command=self._start_inversion
        )
    
    def _create_card_frame_in(self, parent, title: str) -> ttk.Frame:
        """親フレーム内にカードフレームを作成"""
        frame = ttk.Frame(parent, style='Card.TFrame')
        label = ttk.Label(frame, text=title, style='Card.TLabel')
        label.configure(font=(FONTS['family'], FONTS['size_medium'], 'bold'))
        label.pack(anchor='w', padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        return frame
    
    def _layout_widgets(self):
        """ウィジェットを配置"""
        # ヘッダー
        self.header_frame.pack(fill='x', padx=SPACING['xl'], pady=(SPACING['xl'], SPACING['lg']))
        self.title_label.pack(anchor='w')
        self.subtitle_label.pack(anchor='w', pady=(SPACING['xs'], 0))
        
        # メインコンテンツ
        self.main_frame.pack(fill='both', expand=True, padx=SPACING['xl'], pady=SPACING['sm'])
        
        # 左側
        self.left_frame.pack(side='left', fill='both', expand=True, padx=(0, SPACING['sm']))
        self.left_content.pack(fill='both', expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.input_entry.pack(fill='x', pady=(0, SPACING['sm']))
        self.btn_input_frame.pack(fill='x', pady=(0, SPACING['sm']))
        self.btn_select_files.pack(side='left', padx=(0, SPACING['xs']))
        self.btn_select_folder.pack(side='left')
        
        # ファイルリストフレーム
        list_frame = ttk.Frame(self.left_content, style='Card.TFrame')
        list_frame.pack(fill='both', expand=True)
        self.file_listbox.pack(side='left', fill='both', expand=True)
        self.file_scroll.pack(side='right', fill='y')
        
        self.file_count_label.pack(anchor='w', pady=(SPACING['sm'], 0))
        
        # 中央
        self.center_frame.pack(side='left', fill='both', padx=SPACING['sm'])
        self.center_content.pack(fill='both', expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.preview_frame.pack(fill='both', expand=True)
        self.original_frame.pack(fill='x', pady=(0, SPACING['sm']))
        self.original_label.pack()
        self.original_canvas.pack()
        
        self.arrow_label.pack(pady=SPACING['xs'])
        
        self.inverted_frame.pack(fill='x', pady=(SPACING['sm'], 0))
        self.inverted_label.pack()
        self.inverted_canvas.pack()
        
        # 右側
        self.right_frame.pack(side='left', fill='both', expand=True, padx=(SPACING['sm'], 0))
        self.right_content.pack(fill='both', expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.mode_overwrite.pack(anchor='w', pady=SPACING['xs'])
        self.mode_new_folder.pack(anchor='w', pady=SPACING['xs'])
        
        self.output_folder_frame.pack(fill='x', pady=(SPACING['sm'], 0))
        self.output_entry.pack(side='left', fill='x', expand=True, padx=(0, SPACING['xs']))
        self.btn_select_output.pack(side='right')
        
        # アクションボタン
        self.action_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['lg'])
        self.progress_bar.pack(side='left', padx=(0, SPACING['md']))
        self.progress_label.pack(side='left', padx=(0, SPACING['md']))
        self.btn_invert.pack(side='right')
    
    def _select_files(self):
        """ファイル選択"""
        files = filedialog.askopenfilenames(
            title="PNGファイルを選択",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if files:
            self.png_files = list(files)
            self.input_path_var.set(f"{len(files)} ファイル選択済み")
            self._update_file_list()
    
    def _select_folder(self):
        """フォルダ選択"""
        folder = filedialog.askdirectory(title="PNGファイルが含まれるフォルダを選択")
        if folder:
            self.input_path_var.set(folder)
            self.png_files = self._find_png_files(folder)
            self._update_file_list()
    
    def _find_png_files(self, directory: str) -> List[str]:
        """ディレクトリ内のPNGファイルを検索"""
        png_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.png'):
                    png_files.append(os.path.join(root, file))
        return sorted(png_files)
    
    def _select_output(self):
        """出力先選択"""
        folder = filedialog.askdirectory(title="出力先フォルダを選択")
        if folder:
            self.output_path_var.set(folder)
    
    def _update_file_list(self):
        """ファイルリストを更新"""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.png_files:
            self.file_listbox.insert(tk.END, file_path)
        
        self.file_count_label.config(text=f"ファイル数: {len(self.png_files)}")
        
        # 最初のファイルを選択してプレビュー
        if self.png_files:
            self.file_listbox.selection_set(0)
            self.current_index = 0
            self._update_preview()
    
    def _on_file_select(self, event):
        """ファイル選択時"""
        selection = self.file_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self._update_preview()
    
    def _update_preview(self):
        """プレビューを更新"""
        if not self.png_files or self.current_index >= len(self.png_files):
            return
        
        file_path = self.png_files[self.current_index]
        
        try:
            # 元画像を読み込み
            original = self.inverter.load_png(file_path)
            if original is None:
                return
            
            self.current_image = original
            
            # 反転画像を生成
            inverted = self.inverter.invert_image(original)
            
            # プレビュー用にリサイズ
            original_preview = self._resize_for_preview(original)
            inverted_preview = self._resize_for_preview(inverted)
            
            # Tkinter用に変換
            self.original_photo = ImageTk.PhotoImage(original_preview)
            self.inverted_photo = ImageTk.PhotoImage(inverted_preview)
            
            # キャンバスサイズを画像サイズに合わせて更新
            orig_width, orig_height = original_preview.size
            inv_width, inv_height = inverted_preview.size
            
            # キャンバスサイズを更新（画像サイズに合わせる、最大値はpreview_size）
            orig_canvas_width = min(orig_width, self.preview_size[0])
            orig_canvas_height = min(orig_height, self.preview_size[1])
            self.original_canvas.config(width=orig_canvas_width, height=orig_canvas_height)
            
            inv_canvas_width = min(inv_width, self.preview_size[0])
            inv_canvas_height = min(inv_height, self.preview_size[1])
            self.inverted_canvas.config(width=inv_canvas_width, height=inv_canvas_height)
            
            # キャンバスに表示
            self.original_canvas.delete('all')
            self.inverted_canvas.delete('all')
            
            self.original_canvas.create_image(
                orig_canvas_width // 2,
                orig_canvas_height // 2,
                image=self.original_photo,
                anchor='center'
            )
            self.inverted_canvas.create_image(
                inv_canvas_width // 2,
                inv_canvas_height // 2,
                image=self.inverted_photo,
                anchor='center'
            )
            
        except Exception as e:
            print(f"Preview error: {e}")
    
    def _resize_for_preview(self, image: Image.Image) -> Image.Image:
        """プレビュー用にリサイズ"""
        # アスペクト比を維持してリサイズ（全表示できるように）
        # キャンバスサイズに合わせてリサイズ
        max_width, max_height = self.preview_size
        img_width, img_height = image.size
        
        # アスペクト比を計算
        width_ratio = max_width / img_width
        height_ratio = max_height / img_height
        ratio = min(width_ratio, height_ratio)
        
        # リサイズ
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _start_inversion(self):
        """反転を開始"""
        if not self.png_files:
            messagebox.showwarning("警告", "PNGファイルを選択してください。")
            return
        
        output_mode = self.output_mode_var.get()
        if output_mode == "new_folder":
            output_dir = self.output_path_var.get()
            if not output_dir:
                messagebox.showwarning("警告", "出力先フォルダを選択してください。")
                return
        else:
            output_dir = None
        
        # 確認
        if output_mode == "overwrite":
            result = messagebox.askyesno(
                "確認",
                f"{len(self.png_files)} 個のファイルを上書きします。よろしいですか？"
            )
            if not result:
                return
        
        # 処理スレッドを開始
        self.btn_invert.config(state='disabled')
        thread = Thread(target=self._process_inversion, args=(output_dir,))
        thread.daemon = True
        thread.start()
    
    def _process_inversion(self, output_dir: Optional[str]):
        """反転処理（バックグラウンドスレッド）"""
        total = len(self.png_files)
        
        try:
            for i, file_path in enumerate(self.png_files):
                # 画像を読み込み
                image = self.inverter.load_png(file_path)
                if image is None:
                    continue
                
                # 反転
                inverted = self.inverter.invert_image(image)
                
                # 保存先を決定
                if output_dir:
                    filename = os.path.basename(file_path)
                    save_path = os.path.join(output_dir, filename)
                else:
                    save_path = file_path
                
                # 保存
                self.inverter.save_png(inverted, save_path)
                
                # 進捗を更新
                self.after(0, lambda c=i+1, t=total: self._update_inversion_progress(c, t))
            
            self.after(0, lambda: messagebox.showinfo("完了", "反転が完了しました！"))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}"))
        finally:
            self.after(0, self._finish_inversion)
    
    def _update_inversion_progress(self, current: int, total: int):
        """進捗を更新"""
        progress = (current / total) * 100
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"{current} / {total}")
    
    def _finish_inversion(self):
        """反転完了"""
        self.btn_invert.config(state='normal')
        self.progress_bar['value'] = 0
        self.progress_label.config(text="")
