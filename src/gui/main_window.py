"""
メインアプリケーション
タブベースのGUIアプリケーション
"""

import tkinter as tk
from tkinter import ttk

from .styles import COLORS, FONTS, SPACING, configure_styles
from .converter_tab import ConverterTab
from .inverter_tab import InverterTab
from .comparator_tab import ComparatorTab
from .duplicate_tab import DuplicateTab

# ロガーをインポートしてテスト
try:
    from ..utils.logger import log_error, log_debug
    log_debug("アプリケーション起動: ロガーが正常にインポートされました")
except ImportError as e:
    # ロガーがインポートできない場合でもアプリは起動する
    pass


class MainApplication(tk.Tk):
    """メインアプリケーションウィンドウ"""
    
    def __init__(self):
        super().__init__()
        
        self.title("PSD to PNG Converter ver.1.4")
        self.geometry("900x1100")
        self.minsize(700, 900)
        
        # 背景色を設定
        self.configure(bg=COLORS['bg_dark'])
        
        # スタイルを設定
        self.style = ttk.Style(self)
        configure_styles(self.style)
        
        self._create_widgets()
        self._layout_widgets()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダー
        self.header_frame = ttk.Frame(self, style='Dark.TFrame')
        self.app_title = ttk.Label(
            self.header_frame,
            text="PSD to PNG Converter",
            style='Title.TLabel'
        )
        self.app_subtitle = ttk.Label(
            self.header_frame,
            text="教師データ作成ツール ver.1.4",
            style='Subtitle.TLabel'
        )
        
        # ノートブック（タブコンテナ）
        self.notebook = ttk.Notebook(self)
        
        # タブを追加
        self.converter_tab = ConverterTab(self.notebook)
        self.inverter_tab = InverterTab(self.notebook)
        self.comparator_tab = ComparatorTab(self.notebook)
        self.duplicate_tab = DuplicateTab(self.notebook)

        self.notebook.add(self.converter_tab, text="  📄 PSD変換  ")
        self.notebook.add(self.inverter_tab, text="  🔄 白黒反転  ")
        self.notebook.add(self.comparator_tab, text="  🔍 ファイル比較  ")
        self.notebook.add(self.duplicate_tab, text="  🧩 重複検出  ")
    
    def _layout_widgets(self):
        """ウィジェットを配置"""
        # ヘッダー
        self.header_frame.pack(fill='x', padx=SPACING['xl'], pady=(SPACING['lg'], SPACING['sm']))
        self.app_title.pack(side='left')
        self.app_subtitle.pack(side='left', padx=(SPACING['lg'], 0))
        
        # ノートブック
        self.notebook.pack(fill='both', expand=True, padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['lg']))


def run():
    """アプリケーションを起動"""
    app = MainApplication()
    app.mainloop()
