"""
シンプルなログ出力ユーティリティ（フォールバック用）
インポートエラーが発生しても動作するように設計
"""

import sys
from pathlib import Path
from typing import Optional


def _get_log_dir() -> Path:
    """ログディレクトリのパスを取得"""
    # PyInstallerでバンドルされているかチェック
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path.cwd()
    
    log_dir = base_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    return log_dir


def log_error(message: str, exception: Optional[Exception] = None) -> None:
    """エラーログをファイルに出力"""
    try:
        log_dir = _get_log_dir()
        log_file = log_dir / 'error.log'
        
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
            if exception:
                f.write(f"Exception: {type(exception).__name__}: {str(exception)}\n")
                import traceback
                traceback.print_exc(file=f)
            f.write("\n")
            f.flush()
    except Exception:
        pass


def log_debug(message: str) -> None:
    """デバッグログをファイルに出力"""
    try:
        log_dir = _get_log_dir()
        log_file = log_dir / 'debug.log'
        
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    except Exception:
        pass
