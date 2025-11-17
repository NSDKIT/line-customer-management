from app.services.database import db
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self):
        self.supabase = db.get_client()
    
    def create_customer(self, customer_name: str, user_id: str, conversation_id: str) -> Optional[Dict]:
        """顧客を作成"""
        try:
            data = {
                "client": customer_name,
                "sys_user_id": user_id,
                "sys_conversation_id": conversation_id
            }
            response = self.supabase.table('clients').insert(data).execute()
            logger.info(f"Customer created: {customer_name}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None
    
    def get_customers(self, conversation_id: str) -> List[Dict]:
        """顧客リストを取得"""
        try:
            response = self.supabase.table('clients')\
                .select("*")\
                .eq('sys_conversation_id', conversation_id)\
                .order('created_at', desc=True)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting customers: {e}")
            return []
    
    def get_customer_by_id(self, customer_id: int, conversation_id: str) -> Optional[Dict]:
        """IDで顧客を取得"""
        try:
            response = self.supabase.table('clients')\
                .select("*")\
                .eq('id', customer_id)\
                .eq('sys_conversation_id', conversation_id)\
                .limit(1)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting customer by ID: {e}")
            return None
    
    def customer_exists(self, customer_name: str, conversation_id: str) -> bool:
        """顧客が存在するか確認"""
        try:
            response = self.supabase.table('clients')\
                .select("id")\
                .eq('client', customer_name)\
                .eq('sys_conversation_id', conversation_id)\
                .limit(1)\
                .execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error checking customer existence: {e}")
            return False

# シングルトンインスタンス
customer_service = CustomerService()