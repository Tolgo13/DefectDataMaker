"""
PSDファイル処理モジュール
PSDファイルの読み込み、二値化チェック、PNG変換を行う
"""

import os
from pathlib import Path
from typing import Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np
from PIL import Image
from psd_tools import PSDImage


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
            psd = PSDImage.open(file_path)
            image = psd.composite()
            return image
        except Exception as e:
            print(f"Error loading PSD: {file_path}, {e}")
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
            # PSD読み込み
            image = self.load_psd(input_path)
            if image is None:
                return ProcessingResult(
                    file_path=input_path,
                    status=BinarizationStatus.ERROR,
                    message="PSDファイルの読み込みに失敗しました"
                )
            
            # 二値化チェック
            is_binary, non_binary_ratio = self.is_binarized(image)
            
            # 出力パスを生成
            input_name = Path(input_path).stem
            output_path = os.path.join(output_dir, f"{input_name}.png")
            
            # 二値化して保存
            binary_image = self.convert_to_binary(image, invert=invert)
            
            # 出力ディレクトリがなければ作成
            os.makedirs(output_dir, exist_ok=True)
            binary_image.save(output_path, 'PNG')
            
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
            return ProcessingResult(
                file_path=input_path,
                status=BinarizationStatus.ERROR,
                message=f"処理エラー: {str(e)}"
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
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.psd'):
                    psd_files.append(os.path.join(root, file))
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
        
        for i, input_path in enumerate(input_paths):
            result = self.process_file(input_path, output_dir, force_convert, invert)
            results.append(result)
            
            if progress_callback:
                # コールバックがFalseを返したら処理を中断
                should_continue = progress_callback(i + 1, total, result)
                if should_continue is False:
                    break
        
        return results


class PNGInverter:
    """PNG白黒反転クラス"""
    
    @staticmethod
    def load_png(file_path: str) -> Optional[Image.Image]:
        """PNGファイルを読み込み"""
        try:
            return Image.open(file_path)
        except Exception as e:
            print(f"Error loading PNG: {file_path}, {e}")
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
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path, 'PNG')
            return True
        except Exception as e:
            print(f"Error saving PNG: {output_path}, {e}")
            return False
