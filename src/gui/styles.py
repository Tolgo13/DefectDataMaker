"""
スタイル定義モジュール
アプリケーション全体のスタイルを定義
"""

# カラーパレット（ライトテーマ - 白背景）
COLORS = {
    # プライマリカラー
    'primary': '#3B82F6',        # ブルー
    'primary_hover': '#2563EB',
    'primary_light': '#BFDBFE',
    
    # セカンダリカラー
    'secondary': '#10B981',      # エメラルド
    'secondary_hover': '#059669',
    
    # 警告・エラー
    'warning': '#F59E0B',        # アンバー
    'error': '#EF4444',          # レッド
    'success': '#22C55E',        # グリーン
    
    # 背景色（白ベース）
    'bg_dark': '#FFFFFF',        # 白
    'bg_medium': '#F8FAFC',      # 薄いグレー
    'bg_light': '#E2E8F0',       # ライトグレー
    'bg_card': '#F1F5F9',        # カード背景
    
    # テキスト（黒ベース）
    'text_primary': '#1E293B',   # ダークグレー
    'text_secondary': '#64748B', # グレー
    'text_muted': '#94A3B8',     # ミュートグレー
    
    # ボーダー
    'border': '#CBD5E1',
    'border_light': '#E2E8F0',
    
    # ステータス
    'status_binarized': '#22C55E',
    'status_not_binarized': '#F59E0B',
    'status_error': '#EF4444',
}

# フォント設定
FONTS = {
    'family': 'Meiryo',
    'family_mono': 'Consolas',
    'size_small': 9,
    'size_normal': 10,
    'size_medium': 11,
    'size_large': 14,
    'size_xlarge': 18,
    'size_title': 24,
}

# パディング・マージン
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 24,
    'xxl': 32,
}

# ボーダー半径
RADIUS = {
    'sm': 4,
    'md': 8,
    'lg': 12,
    'xl': 16,
}


def configure_styles(style):
    """
    ttkスタイルを設定
    
    Args:
        style: ttk.Style オブジェクト
    """
    style.theme_use('clam')
    
    # フレーム
    style.configure(
        'Card.TFrame',
        background=COLORS['bg_card'],
    )
    
    style.configure(
        'Dark.TFrame',
        background=COLORS['bg_dark'],
    )
    
    # ラベル
    style.configure(
        'TLabel',
        background=COLORS['bg_dark'],
        foreground=COLORS['text_primary'],
        font=(FONTS['family'], FONTS['size_normal']),
    )
    
    style.configure(
        'Title.TLabel',
        background=COLORS['bg_dark'],
        foreground=COLORS['text_primary'],
        font=(FONTS['family'], FONTS['size_title'], 'bold'),
    )
    
    style.configure(
        'Subtitle.TLabel',
        background=COLORS['bg_dark'],
        foreground=COLORS['text_secondary'],
        font=(FONTS['family'], FONTS['size_medium']),
    )
    
    style.configure(
        'Card.TLabel',
        background=COLORS['bg_card'],
        foreground=COLORS['text_primary'],
        font=(FONTS['family'], FONTS['size_normal']),
    )
    
    # ボタン
    style.configure(
        'Primary.TButton',
        background=COLORS['primary'],
        foreground=COLORS['text_primary'],
        font=(FONTS['family'], FONTS['size_normal'], 'bold'),
        padding=(SPACING['lg'], SPACING['sm']),
        borderwidth=0,
    )
    style.map(
        'Primary.TButton',
        background=[('active', COLORS['primary_hover']), ('pressed', COLORS['primary_hover'])],
    )
    
    style.configure(
        'Secondary.TButton',
        background=COLORS['secondary'],
        foreground=COLORS['text_primary'],
        font=(FONTS['family'], FONTS['size_normal']),
        padding=(SPACING['md'], SPACING['sm']),
        borderwidth=0,
    )
    style.map(
        'Secondary.TButton',
        background=[('active', COLORS['secondary_hover']), ('pressed', COLORS['secondary_hover'])],
    )
    
    style.configure(
        'Outline.TButton',
        background=COLORS['bg_card'],
        foreground=COLORS['text_primary'],
        font=(FONTS['family'], FONTS['size_normal']),
        padding=(SPACING['md'], SPACING['sm']),
        borderwidth=1,
        relief='solid',
    )
    style.map(
        'Outline.TButton',
        background=[('active', COLORS['bg_light']), ('pressed', COLORS['bg_light'])],
    )
    
    style.configure(
        'Danger.TButton',
        background=COLORS['error'],
        foreground=COLORS['text_primary'],
        font=(FONTS['family'], FONTS['size_normal']),
        padding=(SPACING['md'], SPACING['sm']),
        borderwidth=0,
    )
    style.map(
        'Danger.TButton',
        background=[('active', '#DC2626'), ('pressed', '#DC2626')],
    )
    
    # エントリ
    style.configure(
        'TEntry',
        fieldbackground=COLORS['bg_light'],
        foreground=COLORS['text_primary'],
        insertcolor=COLORS['text_primary'],
        borderwidth=1,
        padding=SPACING['sm'],
    )
    
    # プログレスバー
    style.configure(
        'TProgressbar',
        background=COLORS['primary'],
        troughcolor=COLORS['bg_light'],
        borderwidth=0,
        thickness=8,
    )
    
    # ノートブック（タブ）
    style.configure(
        'TNotebook',
        background=COLORS['bg_dark'],
        borderwidth=0,
    )
    
    style.configure(
        'TNotebook.Tab',
        background=COLORS['bg_medium'],
        foreground=COLORS['text_secondary'],
        font=(FONTS['family'], FONTS['size_normal']),
        padding=(SPACING['lg'], SPACING['sm']),
        borderwidth=0,
    )
    style.map(
        'TNotebook.Tab',
        background=[('selected', COLORS['bg_card'])],
        foreground=[('selected', COLORS['text_primary'])],
    )
    
    # チェックボタン
    style.configure(
        'TCheckbutton',
        background=COLORS['bg_card'],
        foreground=COLORS['text_primary'],
        font=(FONTS['family'], FONTS['size_normal']),
    )
    
    # スピンボックス
    style.configure(
        'TSpinbox',
        fieldbackground=COLORS['bg_light'],
        foreground=COLORS['text_primary'],
        arrowcolor=COLORS['text_primary'],
        borderwidth=1,
    )
    
    # ツリービュー（ファイルリスト）
    style.configure(
        'Treeview',
        background=COLORS['bg_medium'],
        foreground=COLORS['text_primary'],
        fieldbackground=COLORS['bg_medium'],
        font=(FONTS['family'], FONTS['size_normal']),
        rowheight=28,
        borderwidth=0,
    )
    style.configure(
        'Treeview.Heading',
        background=COLORS['bg_light'],
        foreground=COLORS['text_primary'],
        font=(FONTS['family'], FONTS['size_normal'], 'bold'),
    )
    style.map(
        'Treeview',
        background=[('selected', COLORS['primary'])],
        foreground=[('selected', COLORS['text_primary'])],
    )
    
    # スクロールバー
    style.configure(
        'TScrollbar',
        background=COLORS['bg_light'],
        troughcolor=COLORS['bg_medium'],
        borderwidth=0,
        arrowcolor=COLORS['text_secondary'],
    )
