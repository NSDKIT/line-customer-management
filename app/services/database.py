from supabase import create_client, Client
from app.config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Supabaseクライアントの初期化"""
        try:
            self.supabase: Client = create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_KEY
            )
            logger.info("Supabase connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    def get_client(self) -> Client:
        return self.supabase

# シングルトンインスタンス
db = Database()