"""
ファイル比較タブ
imageフォルダとmasakフォルダのファイルを比較するUIコンポーネント
"""

import os
import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Set, Tuple

from .styles import COLORS, FONTS, SPACING


class ComparatorTab(ttk.Frame):
    """ファイル比較タブ"""
    
    def __init__(self, parent):
        super().__init__(parent, style='Dark.TFrame')
        
        self.image_folder: str = ""
        self.masak_folder: str = ""
        self.comparison_results: List[Dict] = []
        
        self._create_widgets()
        self._layout_widgets()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダー
        self.header_frame = ttk.Frame(self, style='Dark.TFrame')
        self.title_label = ttk.Label(
            self.header_frame,
            text="ファイル比較",
            style='Title.TLabel'
        )
        self.subtitle_label = ttk.Label(
            self.header_frame,
            text="imageフォルダとmasakフォルダのファイルを比較します",
            style='Subtitle.TLabel'
        )
        
        # フォルダ選択セクション
        self.folder_frame = self._create_card_frame("フォルダ選択")
        self.folder_content = ttk.Frame(self.folder_frame, style='Card.TFrame')
        
        # imageフォルダ
        self.image_frame = ttk.Frame(self.folder_content, style='Card.TFrame')
        self.image_label = ttk.Label(
            self.image_frame,
            text="imageフォルダ:",
            style='Card.TLabel'
        )
        self.image_path_var = tk.StringVar()
        self.image_entry = ttk.Entry(
            self.image_frame,
            textvariable=self.image_path_var,
            width=60,
        )
        self.btn_select_image = ttk.Button(
            self.image_frame,
            text="📁 選択",
            style='Outline.TButton',
            command=self._select_image_folder
        )
        
        # masakフォルダ
        self.masak_frame = ttk.Frame(self.folder_content, style='Card.TFrame')
        self.masak_label = ttk.Label(
            self.masak_frame,
            text="masakフォルダ:",
            style='Card.TLabel'
        )
        self.masak_path_var = tk.StringVar()
        self.masak_entry = ttk.Entry(
            self.masak_frame,
            textvariable=self.masak_path_var,
            width=60,
        )
        self.btn_select_masak = ttk.Button(
            self.masak_frame,
            text="📁 選択",
            style='Outline.TButton',
            command=self._select_masak_folder
        )
        
        # 比較実行ボタン
        self.btn_compare = ttk.Button(
            self.folder_content,
            text="🔍 比較実行",
            style='Primary.TButton',
            command=self._compare_folders
        )
        
        # 結果表示セクション
        self.result_frame = self._create_card_frame("比較結果")
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
            columns=('type', 'filename', 'image_exists', 'masak_exists', 'status'),
            show='headings',
            height=15
        )
        self.result_tree.heading('type', text='種類')
        self.result_tree.heading('filename', text='ファイル名')
        self.result_tree.heading('image_exists', text='image')
        self.result_tree.heading('masak_exists', text='masak')
        self.result_tree.heading('status', text='ステータス')
        
        self.result_tree.column('type', width=100, anchor='center')
        self.result_tree.column('filename', width=300)
        self.result_tree.column('image_exists', width=80, anchor='center')
        self.result_tree.column('masak_exists', width=80, anchor='center')
        self.result_tree.column('status', width=200)
        
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
        
        self.image_frame.pack(fill='x', pady=(0, SPACING['sm']))
        self.image_label.pack(side='left', padx=(0, SPACING['sm']))
        self.image_entry.pack(side='left', fill='x', expand=True, padx=(0, SPACING['sm']))
        self.btn_select_image.pack(side='right')
        
        self.masak_frame.pack(fill='x', pady=(0, SPACING['md']))
        self.masak_label.pack(side='left', padx=(0, SPACING['sm']))
        self.masak_entry.pack(side='left', fill='x', expand=True, padx=(0, SPACING['sm']))
        self.btn_select_masak.pack(side='right')
        
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
    
    def _select_image_folder(self):
        """imageフォルダを選択"""
        folder = filedialog.askdirectory(title="imageフォルダを選択")
        if folder:
            self.image_folder = folder
            self.image_path_var.set(folder)
    
    def _select_masak_folder(self):
        """masakフォルダを選択"""
        folder = filedialog.askdirectory(title="masakフォルダを選択")
        if folder:
            self.masak_folder = folder
            self.masak_path_var.set(folder)
    
    def _get_files_in_folder(self, folder: str) -> Set[str]:
        """フォルダ内の全ファイル名を取得（拡張子なし）"""
        files = set()
        if not folder or not os.path.exists(folder):
            return files
        
        for root, dirs, filenames in os.walk(folder):
            for filename in filenames:
                # 拡張子を除いたファイル名を取得
                name_without_ext = Path(filename).stem
                files.add(name_without_ext)
        
        return files
    
    def _compare_folders(self):
        """フォルダを比較"""
        if not self.image_folder or not os.path.exists(self.image_folder):
            messagebox.showwarning("警告", "imageフォルダを選択してください。")
            return
        
        if not self.masak_folder or not os.path.exists(self.masak_folder):
            messagebox.showwarning("警告", "masakフォルダを選択してください。")
            return
        
        # ファイル名を取得
        image_files = self._get_files_in_folder(self.image_folder)
        masak_files = self._get_files_in_folder(self.masak_folder)
        
        # 比較結果を格納
        self.comparison_results = []
        
        # 全ファイル名の集合
        all_files = image_files | masak_files
        
        # 各ファイルについて比較
        for filename in sorted(all_files):
            in_image = filename in image_files
            in_masak = filename in masak_files
            
            if not in_image:
                # imageフォルダに存在しない
                result = {
                    'type': '不足',
                    'filename': filename,
                    'image_exists': '✗',
                    'masak_exists': '✓',
                    'status': 'imageフォルダに存在しません'
                }
            elif not in_masak:
                # masakフォルダに存在しない
                result = {
                    'type': '不足',
                    'filename': filename,
                    'image_exists': '✓',
                    'masak_exists': '✗',
                    'status': 'masakフォルダに存在しません'
                }
            else:
                # 両方に存在（正常）
                result = {
                    'type': '一致',
                    'filename': filename,
                    'image_exists': '✓',
                    'masak_exists': '✓',
                    'status': '両フォルダに存在'
                }
            
            self.comparison_results.append(result)
        
        # 結果を表示
        self._display_results()
        
        # CSV出力ボタンを有効化
        self.btn_export_csv.config(state='normal')
    
    def _display_results(self):
        """結果を表示"""
        # 既存のアイテムをクリア
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 統計情報を計算
        total = len(self.comparison_results)
        missing_in_image = sum(1 for r in self.comparison_results if r['type'] == '不足' and r['masak_exists'] == '✓')
        missing_in_masak = sum(1 for r in self.comparison_results if r['type'] == '不足' and r['image_exists'] == '✓')
        matched = sum(1 for r in self.comparison_results if r['type'] == '一致')
        
        # 統計情報を表示
        stats_text = (
            f"総ファイル数: {total} | "
            f"一致: {matched} | "
            f"image不足: {missing_in_image} | "
            f"masak不足: {missing_in_masak}"
        )
        self.stats_label.config(text=stats_text)
        
        # 結果をツリービューに追加
        for result in self.comparison_results:
            # 不足ファイルのみ表示（一致は表示しない）
            if result['type'] == '不足':
                self.result_tree.insert('', 'end', values=(
                    result['type'],
                    result['filename'],
                    result['image_exists'],
                    result['masak_exists'],
                    result['status']
                ))
    
    def _export_csv(self):
        """CSVファイルに出力"""
        if not self.comparison_results:
            messagebox.showwarning("警告", "比較結果がありません。")
            return
        
        # 保存先を選択
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
                
                # ヘッダー
                writer.writerow(['種類', 'ファイル名', 'image', 'masak', 'ステータス'])
                
                # データ（不足ファイルのみ）
                for result in self.comparison_results:
                    if result['type'] == '不足':
                        writer.writerow([
                            result['type'],
                            result['filename'],
                            result['image_exists'],
                            result['masak_exists'],
                            result['status']
                        ])
            
            messagebox.showinfo("完了", f"CSVファイルを保存しました:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("エラー", f"CSVファイルの保存に失敗しました:\n{e}")
