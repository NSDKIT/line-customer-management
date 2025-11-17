from app.services.database import db
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class AppointmentService:
    def __init__(self):
        self.supabase = db.get_client()
    
    def create_appointment(self, data: Dict) -> Optional[Dict]:
        """商談記録を作成"""
        try:
            response = self.supabase.table('appointments').insert(data).execute()
            logger.info(f"Appointment created for client: {data.get('client')}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return None
    
    def get_appointments(self, conversation_id: str, client_name: str = None) -> List[Dict]:
        """商談履歴を取得"""
        try:
            query = self.supabase.table('appointments')\
                .select("*")\
                .eq('sys_conversation_id', conversation_id)
            
            if client_name:
                query = query.eq('client', client_name)
            
            response = query.order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting appointments: {e}")
            return []
    
    def get_latest_appointment(self, conversation_id: str, client_name: str) -> Optional[Dict]:
        """最新の商談記録を取得"""
        try:
            response = self.supabase.table('appointments')\
                .select("*")\
                .eq('sys_conversation_id', conversation_id)\
                .eq('client', client_name)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting latest appointment: {e}")
            return None

# シングルトンインスタンス
appointment_service = AppointmentService()