from app.services.database import db
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class AppointmentService:
    def __init__(self):
        self.db = db
    
    def create_appointment(self, data: Dict) -> Optional[Dict]:
        """商談記録を作成"""
        try:
            query = """
                INSERT INTO appointments 
                (date, time, client, appointment_detail, sys_user_id, sys_conversation_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """
            params = (
                data.get('date'),
                data.get('time'),
                data.get('client'),
                data.get('appointment_detail'),
                data.get('sys_user_id'),
                data.get('sys_conversation_id')
            )
            result = self.db.execute_insert(query, params)
            logger.info(f"Appointment created for client: {data.get('client')}")
            return result
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return None
    
    def get_appointments(self, conversation_id: str, client_name: str = None) -> List[Dict]:
        """商談履歴を取得"""
        try:
            if client_name:
                query = """
                    SELECT * FROM appointments
                    WHERE sys_conversation_id = %s AND client = %s
                    ORDER BY created_at DESC
                """
                results = self.db.execute_query(query, (conversation_id, client_name))
            else:
                query = """
                    SELECT * FROM appointments
                    WHERE sys_conversation_id = %s
                    ORDER BY created_at DESC
                """
                results = self.db.execute_query(query, (conversation_id,))
            
            return results
        except Exception as e:
            logger.error(f"Error getting appointments: {e}")
            return []

# シングルトンインスタンス
appointment_service = AppointmentService()