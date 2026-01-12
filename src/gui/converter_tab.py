"""
メイン変換タブ
PSDファイルをPNGに変換するメインUIコンポーネント
"""

import os
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from typing import List, Optional

from ..psd_processor import PSDProcessor, BinarizationStatus, ProcessingResult

# ロガーをインポート
try:
    from ..utils.logger import log_error, log_debug
except ImportError:
    try:
        from ..utils.logger_simple import log_error, log_debug
    except ImportError:
        def log_error(message: str, exception=None): pass
        def log_debug(message: str): pass
from .styles import COLORS, FONTS, SPACING


class ConverterTab(ttk.Frame):
    """メイン変換タブ"""
    
    def __init__(self, parent):
        super().__init__(parent, style='Dark.TFrame')
        
        self.processor = PSDProcessor()
        self.psd_files: List[str] = []
        self.is_processing = False
        self.cancel_requested = False
        self.start_time: float = 0
        self.timer_id: Optional[str] = None
        
        self._create_widgets()
        self._layout_widgets()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダー
        self.header_frame = ttk.Frame(self, style='Dark.TFrame')
        self.title_label = ttk.Label(
            self.header_frame,
            text="PSD → PNG 変換",
            style='Title.TLabel'
        )
        self.subtitle_label = ttk.Label(
            self.header_frame,
            text="PSDファイルを白黒二値化PNGに変換します",
            style='Subtitle.TLabel'
        )
        
        # 入力セクション
        self.input_frame = self._create_card_frame("入力")
        self.input_content = ttk.Frame(self.input_frame, style='Card.TFrame')
        
        self.input_path_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            self.input_content,
            textvariable=self.input_path_var,
            width=60,
        )
        
        self.btn_frame = ttk.Frame(self.input_content, style='Card.TFrame')
        self.btn_select_file = ttk.Button(
            self.btn_frame,
            text="📄 ファイル選択",
            style='Outline.TButton',
            command=self._select_file
        )
        self.btn_select_folder = ttk.Button(
            self.btn_frame,
            text="📁 フォルダ選択",
            style='Outline.TButton',
            command=self._select_folder
        )
        
        # 出力セクション
        self.output_frame = self._create_card_frame("出力先")
        self.output_content = ttk.Frame(self.output_frame, style='Card.TFrame')
        
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(
            self.output_content,
            textvariable=self.output_path_var,
            width=60,
        )
        self.btn_select_output = ttk.Button(
            self.output_content,
            text="📁 選択",
            style='Outline.TButton',
            command=self._select_output
        )
        
        # オプションセクション
        self.options_frame = self._create_card_frame("オプション")
        self.options_content = ttk.Frame(self.options_frame, style='Card.TFrame')
        
        self.invert_var = tk.BooleanVar(value=False)
        self.invert_check = ttk.Checkbutton(
            self.options_content,
            text="白黒を反転する",
            variable=self.invert_var,
            style='TCheckbutton'
        )
        
        self.threshold_frame = ttk.Frame(self.options_content, style='Card.TFrame')
        self.threshold_label = ttk.Label(
            self.threshold_frame,
            text="二値化閾値:",
            style='Card.TLabel'
        )
        self.threshold_var = tk.IntVar(value=128)
        self.threshold_spinbox = ttk.Spinbox(
            self.threshold_frame,
            from_=0,
            to=255,
            textvariable=self.threshold_var,
            width=8
        )
        
        # ファイルリストセクション
        self.list_frame = self._create_card_frame("ファイルリスト")
        self.list_content = ttk.Frame(self.list_frame, style='Card.TFrame')
        
        # ツリービュー
        self.tree_frame = ttk.Frame(self.list_content, style='Card.TFrame')
        self.file_tree = ttk.Treeview(
            self.tree_frame,
            columns=('status', 'filename', 'message'),
            show='headings',
            height=8
        )
        self.file_tree.heading('status', text='ステータス')
        self.file_tree.heading('filename', text='ファイル名')
        self.file_tree.heading('message', text='メッセージ')
        self.file_tree.column('status', width=120, anchor='center')
        self.file_tree.column('filename', width=300)
        self.file_tree.column('message', width=300)
        
        self.tree_scroll = ttk.Scrollbar(
            self.tree_frame,
            orient='vertical',
            command=self.file_tree.yview
        )
        self.file_tree.configure(yscrollcommand=self.tree_scroll.set)
        
        self.file_count_label = ttk.Label(
            self.list_content,
            text="ファイル数: 0",
            style='Card.TLabel'
        )
        
        # プログレスセクション
        self.progress_frame = ttk.Frame(self, style='Dark.TFrame')
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="",
            style='TLabel'
        )
        
        # タイマー表示フレーム
        self.timer_frame = ttk.Frame(self.progress_frame, style='Dark.TFrame')
        self.elapsed_label = ttk.Label(
            self.timer_frame,
            text="経過時間: --:--",
            style='TLabel'
        )
        self.remaining_label = ttk.Label(
            self.timer_frame,
            text="残り時間: --:--",
            style='TLabel'
        )
        
        # アクションボタン（タイマーと同じ行に配置）
        self.btn_convert = ttk.Button(
            self.timer_frame,
            text="変換開始",
            style='Primary.TButton',
            command=self._start_conversion
        )
        self.btn_cancel = ttk.Button(
            self.timer_frame,
            text="⏹ 中止",
            style='Danger.TButton',
            command=self._cancel_conversion,
            state='disabled'
        )
        self.btn_clear = ttk.Button(
            self.timer_frame,
            text="クリア",
            style='Outline.TButton',
            command=self._clear_list
        )
    
    def _create_card_frame(self, title: str) -> ttk.Frame:
        """カードフレームを作成"""
        frame = ttk.Frame(self, style='Card.TFrame')
        label = ttk.Label(frame, text=title, style='Card.TLabel')
        label.configure(font=(FONTS['family'], FONTS['size_medium'], 'bold'))
        label.pack(anchor='w', padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        return frame
    
    def _layout_widgets(self):
        """ウィジェットを配置"""
        # ヘッダー（タイトルとサブタイトルを同一行に）
        self.header_frame.pack(fill='x', padx=SPACING['xl'], pady=(SPACING['md'], SPACING['sm']))
        self.title_label.pack(side='left')
        self.subtitle_label.pack(side='left', padx=(SPACING['lg'], 0))
        
        # 入力セクション
        self.input_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['sm'])
        self.input_content.pack(fill='x', padx=SPACING['md'], pady=(0, SPACING['md']))
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(0, SPACING['sm']))
        self.btn_frame.pack(side='right')
        self.btn_select_file.pack(side='left', padx=(0, SPACING['xs']))
        self.btn_select_folder.pack(side='left')
        
        # 出力セクション
        self.output_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['sm'])
        self.output_content.pack(fill='x', padx=SPACING['md'], pady=(0, SPACING['md']))
        self.output_entry.pack(side='left', fill='x', expand=True, padx=(0, SPACING['sm']))
        self.btn_select_output.pack(side='right')
        
        # オプションセクション
        self.options_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['sm'])
        self.options_content.pack(fill='x', padx=SPACING['md'], pady=(0, SPACING['md']))
        self.invert_check.pack(side='left', padx=(0, SPACING['xl']))
        self.threshold_frame.pack(side='left')
        self.threshold_label.pack(side='left', padx=(0, SPACING['sm']))
        self.threshold_spinbox.pack(side='left')
        
        # ファイルリストセクション
        self.list_frame.pack(fill='both', expand=True, padx=SPACING['xl'], pady=SPACING['sm'])
        self.list_content.pack(fill='both', expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))
        self.tree_frame.pack(fill='both', expand=True)
        self.file_tree.pack(side='left', fill='both', expand=True)
        self.tree_scroll.pack(side='right', fill='y')
        self.file_count_label.pack(anchor='w', pady=(SPACING['sm'], 0))
        
        # プログレスセクション
        self.progress_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['sm'])
        self.progress_bar.pack(fill='x')
        self.progress_label.pack(anchor='w', pady=(SPACING['xs'], 0))
        self.timer_frame.pack(fill='x', pady=(SPACING['xs'], SPACING['md']))
        self.elapsed_label.pack(side='left', padx=(0, SPACING['xl']))
        self.remaining_label.pack(side='left')
        # アクションボタン（タイマーと同じ行に配置）
        self.btn_convert.pack(side='right', padx=(SPACING['sm'], 0))
        self.btn_cancel.pack(side='right', padx=(SPACING['sm'], 0))
        self.btn_clear.pack(side='right')
    
    def _select_file(self):
        """ファイル選択"""
        files = filedialog.askopenfilenames(
            title="PSDファイルを選択",
            filetypes=[("PSD files", "*.psd"), ("All files", "*.*")]
        )
        if files:
            self.psd_files = list(files)
            self.input_path_var.set(f"{len(files)} ファイル選択済み")
            # 出力先をデフォルトで入力ファイルと同じフォルダに設定
            if files[0]:
                self.output_path_var.set(os.path.dirname(files[0]))
            self._update_file_list()
    
    def _select_folder(self):
        """フォルダ選択"""
        folder = filedialog.askdirectory(title="PSDファイルが含まれるフォルダを選択")
        if folder:
            self.input_path_var.set(folder)
            self.psd_files = self.processor.find_psd_files(folder)
            # 出力先をデフォルトで入力フォルダに設定
            self.output_path_var.set(folder)
            self._update_file_list()
    
    def _select_output(self):
        """出力先選択"""
        folder = filedialog.askdirectory(title="出力先フォルダを選択")
        if folder:
            self.output_path_var.set(folder)
    
    def _update_file_list(self):
        """ファイルリストを更新"""
        # 既存のアイテムをクリア
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # ファイルを追加
        for file_path in self.psd_files:
            self.file_tree.insert('', 'end', values=('待機中', file_path, ''))
        
        self.file_count_label.config(text=f"ファイル数: {len(self.psd_files)}")
    
    def _clear_list(self):
        """リストをクリア"""
        self.psd_files = []
        self.input_path_var.set("")
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.file_count_label.config(text="ファイル数: 0")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="")
    
    def _start_conversion(self):
        """変換を開始"""
        if self.is_processing:
            return
        
        if not self.psd_files:
            messagebox.showwarning("警告", "PSDファイルを選択してください。")
            return
        
        output_dir = self.output_path_var.get()
        if not output_dir:
            messagebox.showwarning("警告", "出力先フォルダを選択してください。")
            return
        
        # 同名ファイルの重複チェック
        existing_files = []
        for psd_path in self.psd_files:
            png_path = Path(output_dir) / f"{Path(psd_path).stem}.png"
            if png_path.exists():
                existing_files.append(png_path.name)
        
        if existing_files:
            msg = f"出力先に同名のファイルが {len(existing_files)} 件存在します。\n上書きしてよろしいですか？"
            if len(existing_files) <= 5:
                msg += "\n\n対象:\n" + "\n".join(existing_files)
            else:
                msg += "\n\n対象例:\n" + "\n".join(existing_files[:5]) + "\n...など"
                
            if not messagebox.askyesno("上書き確認", msg):
                return
        
        # 処理スレッドを開始
        self.is_processing = True
        self.cancel_requested = False
        self.btn_convert.config(state='disabled')
        self.btn_cancel.config(state='normal')
        self.btn_clear.config(state='disabled')
        
        # タイマー開始
        self.start_time = time.time()
        self._update_timer()
        
        # プロセッサーの設定を更新
        self.processor.threshold = self.threshold_var.get()
        
        thread = Thread(target=self._process_files, args=(output_dir,))
        thread.daemon = True
        thread.start()
    
    def _cancel_conversion(self):
        """変換を中止"""
        if self.is_processing:
            self.cancel_requested = True
            self.btn_cancel.config(state='disabled')
            self.progress_label.config(text="中止中...")
    
    def _update_timer(self):
        """タイマーを更新（1秒ごと）"""
        if not self.is_processing:
            return
        
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)
        self.elapsed_label.config(text=f"経過時間: {elapsed_str}")
        
        # 1秒後に再度更新
        self.timer_id = self.after(1000, self._update_timer)
    
    def _format_time(self, seconds: float) -> str:
        """秒数をMM:SS形式にフォーマット"""
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def _process_files(self, output_dir: str):
        """ファイルを処理（バックグラウンドスレッド）"""
        processed_count = 0
        
        log_debug(f"_process_files開始: ファイル数={len(self.psd_files)}, output_dir={output_dir}")
        
        def progress_callback(current, total, result):
            nonlocal processed_count
            processed_count = current
            log_debug(f"progress_callback: {current}/{total}, status={result.status}, message={result.message}")
            self.after(0, lambda c=current, t=total, r=result: self._update_progress(c, t, r))
            # キャンセルチェック
            return not self.cancel_requested
        
        try:
            log_debug(f"batch_process開始: {len(self.psd_files)}ファイル")
            self.processor.batch_process(
                self.psd_files,
                output_dir,
                invert=self.invert_var.get(),
                progress_callback=progress_callback
            )
            log_debug("batch_process完了")
        except Exception as e:
            log_error(f"_process_filesで例外発生", e)
            log_debug(f"_process_filesで例外発生: {type(e).__name__}: {e}")
            if not self.cancel_requested:
                self.after(0, lambda: messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}"))
        finally:
            log_debug("_process_files終了")
            self.after(0, lambda: self._finish_processing(cancelled=self.cancel_requested))
    
    def _update_progress(self, current: int, total: int, result: ProcessingResult):
        """進捗を更新（メインスレッド）"""
        # プログレスバーを更新
        progress = (current / total) * 100
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"{current} / {total} 完了")
        
        # 残り時間を計算
        if current > 0:
            elapsed = time.time() - self.start_time
            avg_time_per_file = elapsed / current
            remaining_files = total - current
            estimated_remaining = avg_time_per_file * remaining_files
            remaining_str = self._format_time(estimated_remaining)
            self.remaining_label.config(text=f"残り時間: {remaining_str}")
        
        # ツリービューを更新
        items = self.file_tree.get_children()
        if current <= len(items):
            item = items[current - 1]
            
            # 現在のファイルパスを取得（既存の値を保持）
            current_values = self.file_tree.item(item, 'values')
            file_path = current_values[1] if len(current_values) > 1 else result.file_path
            
            # ステータスに応じた表示
            if result.status == BinarizationStatus.BINARIZED:
                status_text = "✓ 二値化済"
            elif result.status == BinarizationStatus.NOT_BINARIZED:
                status_text = "⚠ 二値化実行"
            else:
                status_text = "✗ エラー"
            
            self.file_tree.item(item, values=(status_text, file_path, result.message))
    
    def _finish_processing(self, cancelled: bool = False):
        """処理完了"""
        self.is_processing = False
        self.cancel_requested = False
        
        # タイマー停止
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        
        # ボタン状態を戻す
        self.btn_convert.config(state='normal')
        self.btn_cancel.config(state='disabled')
        self.btn_clear.config(state='normal')
        
        # 完了メッセージ
        if cancelled:
            self.progress_label.config(text="変換が中止されました")
            self.remaining_label.config(text="残り時間: --:--")
            messagebox.showinfo("中止", "変換が中止されました。")
        else:
            self.remaining_label.config(text="残り時間: 00:00")
            messagebox.showinfo("完了", "変換が完了しました！")
