import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LINE設定
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    
    # Supabase設定
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_PASSWORD = os.getenv('SUPABASE_PASSWORD')  # この行があることを確認
    
    # AI API設定
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # アプリ設定
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    @classmethod
    def validate(cls):
        """設定の検証"""
        required = [
            'LINE_CHANNEL_SECRET',
            'LINE_CHANNEL_ACCESS_TOKEN',
            'SUPABASE_URL',
            'SUPABASE_PASSWORD',
            'ANTHROPIC_API_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing = []
        for key in required:
            if not getattr(cls, key):
                missing.append(key)
        
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")