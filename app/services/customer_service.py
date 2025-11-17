from app.services.database import db
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self):
        self.db = db
    
    def create_customer(self, customer_name: str, user_id: str, conversation_id: str) -> Optional[Dict]:
        """顧客を作成"""
        try:
            query = """
                INSERT INTO clients (client, sys_user_id, sys_conversation_id)
                VALUES (%s, %s, %s)
                RETURNING *
            """
            result = self.db.execute_insert(query, (customer_name, user_id, conversation_id))
            logger.info(f"Customer created: {customer_name}")
            return result
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None
    
    def get_customers(self, conversation_id: str) -> List[Dict]:
        """顧客リストを取得"""
        try:
            query = """
                SELECT * FROM clients
                WHERE sys_conversation_id = %s
                ORDER BY created_at DESC
            """
            results = self.db.execute_query(query, (conversation_id,))
            return results
        except Exception as e:
            logger.error(f"Error getting customers: {e}")
            return []
    
    def get_customer_by_id(self, customer_id: int, conversation_id: str) -> Optional[Dict]:
        """IDで顧客を取得"""
        try:
            query = """
                SELECT * FROM clients
                WHERE id = %s AND sys_conversation_id = %s
                LIMIT 1
            """
            results = self.db.execute_query(query, (customer_id, conversation_id))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting customer by ID: {e}")
            return None
    
    def customer_exists(self, customer_name: str, conversation_id: str) -> bool:
        """顧客が存在するか確認"""
        try:
            query = """
                SELECT id FROM clients
                WHERE client = %s AND sys_conversation_id = %s
                LIMIT 1
            """
            results = self.db.execute_query(query, (customer_name, conversation_id))
            return bool(results)
        except Exception as e:
            logger.error(f"Error checking customer existence: {e}")
            return False

# シングルトンインスタンス
customer_service = CustomerService()