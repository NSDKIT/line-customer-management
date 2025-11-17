from typing import Dict
import logging

logger = logging.getLogger(__name__)

# ユーザーごとのセッションデータ
# 本番環境ではRedisやMemcachedの使用を推奨
user_sessions: Dict[str, Dict] = {}

def get_session(user_id: str) -> Dict:
    """セッション取得"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'number': 0,
            'handle_type': '0',
            'date': '0',
            'time': '0',
            'client': '0',
            'appointment_detail': '0',
            'deal_with_result': '0'
        }
        logger.info(f"New session created for user: {user_id}")
    return user_sessions[user_id]

def update_session(user_id: str, data: Dict):
    """セッション更新"""
    session = get_session(user_id)
    session.update(data)
    logger.debug(f"Session updated for user {user_id}: {data}")

def reset_session(user_id: str):
    """セッションリセット"""
    user_sessions[user_id] = {
        'number': 0,
        'handle_type': '0',
        'date': '0',
        'time': '0',
        'client': '0',
        'appointment_detail': '0',
        'deal_with_result': '0'
    }
    logger.info(f"Session reset for user: {user_id}")

def get_all_sessions() -> Dict:
    """全セッションを取得（デバッグ用）"""
    return user_sessions