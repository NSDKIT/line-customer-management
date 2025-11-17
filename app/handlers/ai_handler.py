from anthropic import Anthropic
from openai import OpenAI
from app.config import Config
from typing import List, Dict
import logging
import json

logger = logging.getLogger(__name__)

class AIHandler:
    def __init__(self):
        try:
            self.anthropic = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.openai = OpenAI(api_key=Config.OPENAI_API_KEY)
            logger.info("AI clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
            raise
    
    def generate_sales_advice(self, appointments_data: List[Dict]) -> str:
        """営業アドバイスを生成（Claude使用）"""
        try:
            if not appointments_data:
                return "商談履歴がありません。まずは「記録」から商談を記録してください。"
            
            # データを整形
            formatted_data = self._format_appointments_for_prompt(appointments_data)
            
            prompt = f"""
あなたは営業支援アシスタントです。
以下の商談履歴を分析し、営業マンへのアドバイスを提供してください。

【商談履歴】
{formatted_data}

以下の観点で分析してください:
- 📊 営業段階の進捗状況
- 🎯 次のアクション提案（具体的に）
- 💡 成約確度の評価
- ⚠️ 注意点やリスク
- ✨ うまくいっているポイント

簡潔で実用的なアドバイスを、見やすく絵文字を使って提供してください。
"""
            
            message = self.anthropic.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=1500,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            logger.info(f"Sales advice generated successfully")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating sales advice: {e}")
            return "申し訳ありません。アドバイス生成中にエラーが発生しました。"
    
    def format_customer_list(self, customers_data: List[Dict]) -> str:
        """顧客リストをフォーマット（GPT使用）"""
        try:
            if not customers_data:
                return "📋 顧客リスト\n\n顧客データが見つかりません。\n\n「記録」から新しい顧客との商談を記録してください。"
            
            # シンプルなフォーマットに変更（API呼び出しを減らすため）
            result = "📋 顧客リスト\n\n"
            for customer in customers_data:
                result += f"ID {customer['id']}: {customer['client']}\n"
            result += f"\n合計: {len(customers_data)}件の顧客"
            
            logger.info(f"Customer list formatted: {len(customers_data)} customers")
            return result
            
        except Exception as e:
            logger.error(f"Error formatting customer list: {e}")
            return "顧客リストの表示中にエラーが発生しました。"
    
    def _format_appointments_for_prompt(self, appointments: List[Dict]) -> str:
        """商談データをプロンプト用に整形"""
        formatted = []
        for i, apt in enumerate(appointments[:10], 1):  # 最新10件のみ
            formatted.append(
                f"【商談{i}】\n"
                f"日付: {apt.get('date', '不明')}\n"
                f"時間: {apt.get('time', '不明')}\n"
                f"顧客: {apt.get('client', '不明')}\n"
                f"内容: {apt.get('appointment_detail', '不明')}\n"
            )
        return "\n".join(formatted)

# シングルトンインスタンス
ai_handler = AIHandler()