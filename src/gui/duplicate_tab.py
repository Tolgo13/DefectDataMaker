"""
重複ファイル検出タブ
2つのフォルダを比較し、同名ファイルのみを列挙するUIコンポーネント
"""

import os
import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Set

from .styles import COLORS, FONTS, SPACING


class DuplicateTab(ttk.Frame):
    """重複ファイル検出タブ"""

    def __init__(self, parent):
        super().__init__(parent, style='Dark.TFrame')

        self.folder_a: str = ""
        self.folder_b: str = ""
        self.duplicate_results: List[Dict] = []

        self._create_widgets()
        self._layout_widgets()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダー
        self.header_frame = ttk.Frame(self, style='Dark.TFrame')
        self.title_label = ttk.Label(
            self.header_frame,
            text="重複ファイル検出",
            style='Title.TLabel'
        )
        self.subtitle_label = ttk.Label(
            self.header_frame,
            text="2つのフォルダを比較し、同名のファイルのみを列挙します",
            style='Subtitle.TLabel'
        )

        # フォルダ選択セクション
        self.folder_frame = self._create_card_frame("フォルダ選択")
        self.folder_content = ttk.Frame(self.folder_frame, style='Card.TFrame')

        # フォルダA
        self.folder_a_frame = ttk.Frame(self.folder_content, style='Card.TFrame')
        self.folder_a_label = ttk.Label(
            self.folder_a_frame,
            text="フォルダA:",
            style='Card.TLabel'
        )
        self.folder_a_path_var = tk.StringVar()
        self.folder_a_entry = ttk.Entry(
            self.folder_a_frame,
            textvariable=self.folder_a_path_var,
            width=60,
        )
        self.btn_select_folder_a = ttk.Button(
            self.folder_a_frame,
            text="📁 選択",
            style='Outline.TButton',
            command=self._select_folder_a
        )

        # フォルダB
        self.folder_b_frame = ttk.Frame(self.folder_content, style='Card.TFrame')
        self.folder_b_label = ttk.Label(
            self.folder_b_frame,
            text="フォルダB:",
            style='Card.TLabel'
        )
        self.folder_b_path_var = tk.StringVar()
        self.folder_b_entry = ttk.Entry(
            self.folder_b_frame,
            textvariable=self.folder_b_path_var,
            width=60,
        )
        self.btn_select_folder_b = ttk.Button(
            self.folder_b_frame,
            text="📁 選択",
            style='Outline.TButton',
            command=self._select_folder_b
        )

        # 比較実行ボタン
        self.btn_compare = ttk.Button(
            self.folder_content,
            text="🔍 重複検出実行",
            style='Primary.TButton',
            command=self._find_duplicates
        )

        # 結果表示セクション
        self.result_frame = self._create_card_frame("重複ファイル一覧")
        self.result_content = ttk.Frame(self.result_frame, style='Card.TFrame')

        # 統計情報
        self.stats_frame = ttk.Frame(self.result_content, style='Card.TFrame')
        self.stats_label = ttk.Label(
            self.stats_frame,
            text="",
            style='Card.TLabel'
        )

        # ツリービュー
        self.tree_frame = ttk.Frame(self.result_content, style='Card.TFrame')
        self.result_tree = ttk.Treeview(
            self.tree_frame,
            columns=('filename', 'ext_a', 'ext_b'),
            show='headings',
            height=15
        )
        self.result_tree.heading('filename', text='ファイル名')
        self.result_tree.heading('ext_a', text='フォルダAの拡張子')
        self.result_tree.heading('ext_b', text='フォルダBの拡張子')

        self.result_tree.column('filename', width=350)
        self.result_tree.column('ext_a', width=150, anchor='center')
        self.result_tree.column('ext_b', width=150, anchor='center')

        self.tree_scroll = ttk.Scrollbar(
            self.tree_frame,
            orient='vertical',
            command=self.result_tree.yview
        )
        self.result_tree.configure(yscrollcommand=self.tree_scroll.set)

        # CSV出力ボタン
        self.action_frame = ttk.Frame(self, style='Dark.TFrame')
        self.btn_export_csv = ttk.Button(
            self.action_frame,
            text="📊 CSV出力",
            style='Secondary.TButton',
            command=self._export_csv,
            state='disabled'
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
        # ヘッダー
        self.header_frame.pack(fill='x', padx=SPACING['xl'], pady=(SPACING['md'], SPACING['sm']))
        self.title_label.pack(side='left')
        self.subtitle_label.pack(side='left', padx=(SPACING['lg'], 0))

        # フォルダ選択セクション
        self.folder_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['sm'])
        self.folder_content.pack(fill='x', padx=SPACING['md'], pady=(0, SPACING['md']))

        self.folder_a_frame.pack(fill='x', pady=(0, SPACING['sm']))
        self.folder_a_label.pack(side='left', padx=(0, SPACING['sm']))
        self.folder_a_entry.pack(side='left', fill='x', expand=True, padx=(0, SPACING['sm']))
        self.btn_select_folder_a.pack(side='right')

        self.folder_b_frame.pack(fill='x', pady=(0, SPACING['md']))
        self.folder_b_label.pack(side='left', padx=(0, SPACING['sm']))
        self.folder_b_entry.pack(side='left', fill='x', expand=True, padx=(0, SPACING['sm']))
        self.btn_select_folder_b.pack(side='right')

        self.btn_compare.pack(pady=(SPACING['sm'], 0))

        # 結果表示セクション
        self.result_frame.pack(fill='both', expand=True, padx=SPACING['xl'], pady=SPACING['sm'])
        self.result_content.pack(fill='both', expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))

        self.stats_frame.pack(fill='x', pady=(0, SPACING['sm']))
        self.stats_label.pack(anchor='w')

        self.tree_frame.pack(fill='both', expand=True)
        self.result_tree.pack(side='left', fill='both', expand=True)
        self.tree_scroll.pack(side='right', fill='y')

        # アクションボタン
        self.action_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['lg'])
        self.btn_export_csv.pack(side='right')

    def _select_folder_a(self):
        """フォルダAを選択"""
        folder = filedialog.askdirectory(title="フォルダAを選択")
        if folder:
            self.folder_a = folder
            self.folder_a_path_var.set(folder)

    def _select_folder_b(self):
        """フォルダBを選択"""
        folder = filedialog.askdirectory(title="フォルダBを選択")
        if folder:
            self.folder_b = folder
            self.folder_b_path_var.set(folder)

    def _get_files_in_folder(self, folder: str) -> Dict[str, str]:
        """フォルダ内の全ファイル名（拡張子なし）→拡張子のマッピングを取得"""
        files: Dict[str, str] = {}
        if not folder or not os.path.exists(folder):
            return files

        for root, dirs, filenames in os.walk(folder):
            for filename in filenames:
                path = Path(filename)
                name_without_ext = path.stem
                files[name_without_ext] = path.suffix
        return files

    def _find_duplicates(self):
        """フォルダを比較し、同名ファイルのみを抽出"""
        if not self.folder_a or not os.path.exists(self.folder_a):
            messagebox.showwarning("警告", "フォルダAを選択してください。")
            return

        if not self.folder_b or not os.path.exists(self.folder_b):
            messagebox.showwarning("警告", "フォルダBを選択してください。")
            return

        files_a = self._get_files_in_folder(self.folder_a)
        files_b = self._get_files_in_folder(self.folder_b)

        # 両方のフォルダに存在するファイル名のみ抽出
        duplicate_names = set(files_a.keys()) & set(files_b.keys())

        self.duplicate_results = []
        for filename in sorted(duplicate_names):
            self.duplicate_results.append({
                'filename': filename,
                'ext_a': files_a[filename],
                'ext_b': files_b[filename],
            })

        self._display_results()
        self.btn_export_csv.config(state='normal' if self.duplicate_results else 'disabled')

    def _display_results(self):
        """結果を表示"""
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        stats_text = f"重複ファイル数: {len(self.duplicate_results)}"
        self.stats_label.config(text=stats_text)

        for result in self.duplicate_results:
            self.result_tree.insert('', 'end', values=(
                result['filename'],
                result['ext_a'],
                result['ext_b'],
            ))

    def _export_csv(self):
        """CSVファイルに出力"""
        if not self.duplicate_results:
            messagebox.showwarning("警告", "重複ファイルがありません。")
            return

        file_path = filedialog.asksaveasfilename(
            title="CSVファイルを保存",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ファイル名', 'フォルダAの拡張子', 'フォルダBの拡張子'])
                for result in self.duplicate_results:
                    writer.writerow([
                        result['filename'],
                        result['ext_a'],
                        result['ext_b'],
                    ])

            messagebox.showinfo("完了", f"CSVファイルを保存しました:\n{file_path}")

        except Exception as e:
            messagebox.showerror("エラー", f"CSVファイルの保存に失敗しました:\n{e}")
