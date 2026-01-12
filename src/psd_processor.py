"""
PSDファイル処理モジュール
PSDファイルの読み込み、二値化チェック、PNG変換を行う
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np
from PIL import Image
from psd_tools import PSDImage

# ロガーをインポート（オプション）
_log_error_available = False
_log_debug_available = False

try:
    from ..utils.logger import log_error, log_debug
    _log_error_available = True
    _log_debug_available = True
except ImportError:
    try:
        # フォールバック: シンプルなロガーを試す
        from ..utils.logger_simple import log_error, log_debug
        _log_error_available = True
        _log_debug_available = True
    except ImportError:
        # ロガーが利用できない場合は何もしない
        def log_error(message: str, exception: Optional[Exception] = None) -> None:
            pass
        def log_debug(message: str) -> None:
            pass


class BinarizationStatus(Enum):
    """二値化ステータス"""
    BINARIZED = "binarized"  # 二値化済み
    NOT_BINARIZED = "not_binarized"  # 二値化されていない
    ERROR = "error"  # エラー


@dataclass
class ProcessingResult:
    """処理結果"""
    file_path: str
    status: BinarizationStatus
    message: str
    output_path: Optional[str] = None


class PSDProcessor:
    """PSDファイル処理クラス"""
    
    def __init__(self, threshold: int = 128, tolerance: float = 0.01):
        """
        Args:
            threshold: 二値化の閾値 (0-255)
            tolerance: 二値化判定の許容誤差 (0.0-1.0)
        """
        self.threshold = threshold
        self.tolerance = tolerance
    
    def load_psd(self, file_path: str) -> Optional[Image.Image]:
        """
        PSDファイルを読み込んでPIL Imageに変換
        
        Args:
            file_path: PSDファイルのパス
            
        Returns:
            PIL Image オブジェクト、エラー時はNone
        """
        try:
            log_debug(f"load_psd開始: {file_path}")
            # Pathオブジェクトに変換してから文字列に戻すことで、エンコーディング問題を回避
            path = Path(file_path)
            log_debug(f"Path作成成功: {path}")
            
            log_debug(f"PSDImage.open開始: {str(path)}")
            psd = PSDImage.open(str(path))
            log_debug("PSDImage.open成功")
            
            log_debug("psd.composite()開始")
            image = psd.composite()
            log_debug("psd.composite()成功")
            
            return image
        except ImportError as e:
            # モジュールのインポートエラー（PyInstallerでバンドル漏れの可能性）
            error_msg = f"モジュールのインポートエラー: {e}\npsd_toolsが正しくインストールされていないか、PyInstallerでバンドルされていない可能性があります。"
            log_error(f"Error loading PSD (ImportError): {file_path}", e)
            log_debug(f"ImportError発生: {e}")
            print(error_msg)
            return None
        except Exception as e:
            error_msg = f"PSDファイルの読み込みエラー: {file_path}, {e}"
            log_error(f"Error loading PSD: {file_path}", e)
            log_debug(f"Exception発生: {type(e).__name__}: {e}")
            print(error_msg)
            return None
    
    def is_binarized(self, image: Image.Image) -> Tuple[bool, float]:
        """
        画像が二値化されているかチェック
        
        Args:
            image: PIL Image オブジェクト
            
        Returns:
            (is_binarized, ratio_of_non_binary_pixels)
        """
        # グレースケールに変換
        gray = image.convert('L')
        pixels = np.array(gray)
        
        # 完全な黒(0)と白(255)のピクセル数をカウント
        total_pixels = pixels.size
        black_pixels = np.sum(pixels == 0)
        white_pixels = np.sum(pixels == 255)
        binary_pixels = black_pixels + white_pixels
        
        # 二値化の割合を計算
        binary_ratio = binary_pixels / total_pixels
        non_binary_ratio = 1.0 - binary_ratio
        
        # 許容誤差以内なら二値化済みと判定
        is_binary = non_binary_ratio <= self.tolerance
        
        return is_binary, non_binary_ratio
    
    def convert_to_binary(self, image: Image.Image, invert: bool = False) -> Image.Image:
        """
        画像を二値化（白黒）に変換
        
        Args:
            image: PIL Image オブジェクト
            invert: Trueの場合、白黒を反転
            
        Returns:
            二値化されたPIL Image
        """
        # グレースケールに変換
        gray = image.convert('L')
        pixels = np.array(gray)
        
        # 閾値で二値化
        binary = np.where(pixels > self.threshold, 255, 0).astype(np.uint8)
        
        # 反転処理
        if invert:
            binary = 255 - binary
        
        return Image.fromarray(binary, mode='L')
    
    def process_file(
        self, 
        input_path: str, 
        output_dir: str, 
        force_convert: bool = True,
        invert: bool = False
    ) -> ProcessingResult:
        """
        単一のPSDファイルを処理
        
        Args:
            input_path: 入力PSDファイルのパス
            output_dir: 出力ディレクトリ
            force_convert: 二値化されていない場合も変換するか
            invert: 白黒を反転するか
            
        Returns:
            ProcessingResult
        """
        try:
            log_debug(f"process_file開始: input_path={input_path}, output_dir={output_dir}")
            # PSD読み込み
            image = self.load_psd(input_path)
            if image is None:
                log_debug("load_psdがNoneを返しました")
                return ProcessingResult(
                    file_path=input_path,
                    status=BinarizationStatus.ERROR,
                    message="PSDファイルの読み込みに失敗しました"
                )
            
            log_debug("PSD読み込み成功、二値化チェック開始")
            # 二値化チェック
            is_binary, non_binary_ratio = self.is_binarized(image)
            log_debug(f"二値化チェック完了: is_binary={is_binary}, non_binary_ratio={non_binary_ratio}")
            
            # 出力パスを生成（Pathオブジェクトを使用）
            input_path_obj = Path(input_path)
            output_dir_obj = Path(output_dir)
            output_path_obj = output_dir_obj / f"{input_path_obj.stem}.png"
            output_path = str(output_path_obj)
            log_debug(f"出力パス: {output_path}")
            
            # 二値化して保存
            log_debug("二値化処理開始")
            binary_image = self.convert_to_binary(image, invert=invert)
            log_debug("二値化処理完了")
            
            # 出力ディレクトリがなければ作成
            log_debug(f"出力ディレクトリ作成: {output_dir_obj}")
            output_dir_obj.mkdir(parents=True, exist_ok=True)
            log_debug(f"PNG保存開始: {output_path}")
            binary_image.save(output_path, 'PNG')
            log_debug("PNG保存成功")
            
            if is_binary:
                return ProcessingResult(
                    file_path=input_path,
                    status=BinarizationStatus.BINARIZED,
                    message="元から二値化済み",
                    output_path=output_path
                )
            else:
                return ProcessingResult(
                    file_path=input_path,
                    status=BinarizationStatus.NOT_BINARIZED,
                    message=f"二値化されていませんでした (非二値ピクセル: {non_binary_ratio:.1%})",
                    output_path=output_path
                )
                
        except Exception as e:
            error_msg = f"処理エラー: {str(e)}"
            log_error(f"Error processing file: {input_path}, output_dir={output_dir}", e)
            log_debug(f"process_fileで例外発生: {type(e).__name__}: {e}")
            return ProcessingResult(
                file_path=input_path,
                status=BinarizationStatus.ERROR,
                message=error_msg
            )
    
    def find_psd_files(self, directory: str) -> List[str]:
        """
        ディレクトリ内のPSDファイルを再帰的に検索
        
        Args:
            directory: 検索ディレクトリ
            
        Returns:
            PSDファイルのパスリスト
        """
        psd_files = []
        # Pathオブジェクトを使用して日本語パスを正しく処理
        dir_path = Path(directory)
        for psd_path in dir_path.rglob('*.psd'):
            if psd_path.is_file():
                psd_files.append(str(psd_path))
        # 大文字小文字を区別しない検索も追加
        for psd_path in dir_path.rglob('*.PSD'):
            if psd_path.is_file():
                file_str = str(psd_path)
                if file_str not in psd_files:  # 重複を避ける
                    psd_files.append(file_str)
        return sorted(psd_files)
    
    def batch_process(
        self,
        input_paths: List[str],
        output_dir: str,
        force_convert: bool = True,
        invert: bool = False,
        progress_callback=None
    ) -> List[ProcessingResult]:
        """
        複数のPSDファイルをバッチ処理
        
        Args:
            input_paths: 入力ファイルパスのリスト
            output_dir: 出力ディレクトリ
            force_convert: 二値化されていない場合も変換するか
            invert: 白黒を反転するか
            progress_callback: 進捗コールバック関数 (current, total, result)
            
        Returns:
            ProcessingResultのリスト
        """
        results = []
        total = len(input_paths)
        log_debug(f"batch_process: total={total} files, output_dir={output_dir}")
        
        for i, input_path in enumerate(input_paths):
            log_debug(f"batch_process: 処理開始 [{i+1}/{total}]: {input_path}")
            result = self.process_file(input_path, output_dir, force_convert, invert)
            log_debug(f"batch_process: 処理完了 [{i+1}/{total}]: status={result.status}, message={result.message}")
            results.append(result)
            
            if progress_callback:
                # コールバックがFalseを返したら処理を中断
                should_continue = progress_callback(i + 1, total, result)
                if should_continue is False:
                    log_debug("batch_process: キャンセルされました")
                    break
        
        log_debug(f"batch_process: 全処理完了: {len(results)}件")
        return results


class PNGInverter:
    """PNG白黒反転クラス"""
    
    @staticmethod
    def load_png(file_path: str) -> Optional[Image.Image]:
        """PNGファイルを読み込み"""
        try:
            # Pathオブジェクトに変換してから文字列に戻すことで、エンコーディング問題を回避
            path = Path(file_path)
            return Image.open(str(path))
        except Exception as e:
            error_msg = f"PNGファイルの読み込みエラー: {file_path}, {e}"
            log_error(error_msg, e)
            print(error_msg)
            return None
    
    @staticmethod
    def invert_image(image: Image.Image) -> Image.Image:
        """画像の白黒を反転"""
        # グレースケールに変換
        gray = image.convert('L')
        pixels = np.array(gray)
        
        # 反転
        inverted = 255 - pixels
        
        return Image.fromarray(inverted, mode='L')
    
    @staticmethod
    def save_png(image: Image.Image, output_path: str) -> bool:
        """PNGファイルを保存"""
        try:
            # Pathオブジェクトを使用してディレクトリ作成とパス処理を行う
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(str(path), 'PNG')
            return True
        except Exception as e:
            error_msg = f"PNGファイルの保存エラー: {output_path}, {e}"
            log_error(error_msg, e)
            print(error_msg)
            return False
