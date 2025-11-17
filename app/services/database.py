import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import Config
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def _initialize(self):
        """PostgreSQL接続パラメータの初期化（接続テストなし）"""
        if self._initialized:
            return
            
        try:
            # Supabase URLからproject_idを抽出
            project_id = Config.SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
            
            self.conn_params = {
                'host': f'db.{project_id}.supabase.co',
                'database': 'postgres',
                'user': 'postgres',
                'password': Config.SUPABASE_PASSWORD,
                'port': 5432,
                'sslmode': 'require',
                'connect_timeout': 10
            }
            
            self._initialized = True
            logger.info("PostgreSQL connection parameters configured")
        except Exception as e:
            logger.error(f"Failed to configure PostgreSQL parameters: {e}")
            raise
    
    def _get_connection(self):
        """新しい接続を取得"""
        if not self._initialized:
            self._initialize()
        return psycopg2.connect(**self.conn_params, cursor_factory=RealDictCursor)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """SELECT クエリを実行"""
        if not self._initialized:
            self._initialize()
            
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def execute_insert(self, query: str, params: tuple = None) -> Optional[Dict]:
        """INSERT クエリを実行"""
        if not self._initialized:
            self._initialize()
            
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            if cursor.rowcount > 0:
                result = cursor.fetchone()
                return dict(result) if result else None
            return None
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Insert execution error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """UPDATE クエリを実行"""
        if not self._initialized:
            self._initialize()
            
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            affected = cursor.rowcount
            return affected
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Update execution error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# シングルトンインスタンス
db = Database()