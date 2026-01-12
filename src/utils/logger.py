"""
ログ出力ユーティリティ
PyInstallerでバンドルされた実行ファイルでも動作するように設計
"""

import sys
import os
from pathlib import Path
from typing import Optional


def _get_log_dir() -> Path:
    """ログディレクトリのパスを取得"""
    try:
        # PyInstallerでバンドルされているかチェック
        if getattr(sys, 'frozen', False):
            # 実行ファイルのディレクトリ
            base_dir = Path(sys.executable).parent
        else:
            # スクリプトのディレクトリ
            try:
                base_dir = Path(__file__).parent.parent.parent
            except NameError:
                # __file__が定義されていない場合（PyInstallerなど）
                base_dir = Path.cwd()
    except Exception:
        # フォールバック: カレントディレクトリを使用
        base_dir = Path.cwd()
    
    log_dir = base_dir / 'logs'
    try:
        log_dir.mkdir(exist_ok=True)
    except Exception:
        # ディレクトリ作成に失敗した場合はカレントディレクトリを使用
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(exist_ok=True)
    
    return log_dir


def log_error(message: str, exception: Optional[Exception] = None) -> None:
    """
    エラーログをファイルに出力
    
    Args:
        message: エラーメッセージ
        exception: 例外オブジェクト（オプション）
    """
    try:
        log_dir = _get_log_dir()
        log_file = log_dir / 'error.log'
        
        import traceback
        import datetime
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
            if exception:
                f.write(f"Exception: {type(exception).__name__}: {str(exception)}\n")
                f.write("Traceback:\n")
                try:
                    traceback.print_exc(file=f)
                except Exception:
                    f.write(f"Traceback output failed: {str(exception)}\n")
            f.write("\n")
            f.flush()  # 即座にファイルに書き込む
    except Exception as e:
        # ログ出力に失敗してもアプリをクラッシュさせない
        # 可能であればフォールバック先に書き込む
        try:
            fallback_file = Path.cwd() / 'error_fallback.log'
            with open(fallback_file, 'a', encoding='utf-8') as f:
                f.write(f"Logger failed: {e}\nOriginal message: {message}\n\n")
        except Exception:
            pass


def log_debug(message: str) -> None:
    """
    デバッグログをファイルに出力
    
    Args:
        message: デバッグメッセージ
    """
    try:
        log_dir = _get_log_dir()
        log_file = log_dir / 'debug.log'
        
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass
