import re
from typing import Tuple

def is_valid_date(date_str: str) -> Tuple[bool, str]:
    """日付形式の検証"""
    # 様々な日付フォーマットに対応
    patterns = [
        r'^\d{4}/\d{1,2}/\d{1,2}$',  # 2025/11/17
        r'^\d{4}-\d{1,2}-\d{1,2}$',  # 2025-11-17
        r'^\d{1,2}/\d{1,2}$',         # 11/17
        r'^\d{1,2}月\d{1,2}日$',      # 11月17日
    ]
    
    for pattern in patterns:
        if re.match(pattern, date_str):
            return True, date_str
    
    return False, "日付形式が正しくありません。例: 2025/11/17"

def is_valid_time(time_str: str) -> Tuple[bool, str]:
    """時刻形式の検証"""
    patterns = [
        r'^\d{1,2}:\d{2}$',      # 14:30
        r'^\d{1,2}時\d{1,2}分$', # 14時30分
        r'^\d{1,2}時$',          # 14時
    ]
    
    for pattern in patterns:
        if re.match(pattern, time_str):
            return True, time_str
    
    return False, "時刻形式が正しくありません。例: 14:30"

def is_numeric_id(text: str) -> bool:
    """数字IDかどうか判定"""
    return re.match(r'^\d+$', text) is not None

def sanitize_input(text: str) -> str:
    """入力のサニタイズ"""
    # 改行や特殊文字を除去
    return text.strip()