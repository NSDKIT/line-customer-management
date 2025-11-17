from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import LineBotApiError
from app.config import Config
from app.services.customer_service import customer_service
from app.services.appointment_service import appointment_service
from app.handlers.ai_handler import ai_handler
from app.utils.session import get_session, update_session, reset_session
from app.utils.validators import is_numeric_id, sanitize_input
import logging

logger = logging.getLogger(__name__)

# LINE Bot API 初期化
line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """LINE メッセージハンドラー"""
    try:
        user_id = event.source.user_id
        user_message = sanitize_input(event.message.text)
        
        logger.info(f"Message from {user_id}: {user_message}")
        
        # メッセージ処理
        response = process_message(user_id, user_message)
        
        # 応答送信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
        logger.info(f"Response sent to {user_id}")
        
    except LineBotApiError as e:
        logger.error(f"LINE Bot API Error: {e}")
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="エラーが発生しました。もう一度お試しください。")
            )
        except:
            pass

def process_message(user_id: str, message: str) -> str:
    """メッセージ処理のメインロジック"""
    
    session = get_session(user_id)
    number = session.get('number', 0)
    handle_type = session.get('handle_type', '0')
    
    # 初期化コマンド（記録・履歴）
    if '記録' in message or '履歴' in message:
        return handle_initial_command(user_id, message)
    
    # 履歴モードでの顧客ID入力
    if handle_type == '2' and number == 1:
        return handle_history_customer_selection(user_id, message)
    
    # 記録モードのフロー処理
    if handle_type == '1':
        if number == 1:
            return handle_date_input(user_id, message, session)
        elif number == 2:
            return handle_time_input(user_id, message, session)
        elif number == 3:
            return handle_customer_input(user_id, message, session)
        elif number == 4:
            return handle_appointment_detail_input(user_id, message, session)
        elif number == 0 and message in ['1', '2', '3', '4', '5']:
            return handle_confirmation_choice(user_id, message, session)
    
    # デフォルト応答
    return "「記録」または「履歴」を入力してください。"

def handle_initial_command(user_id: str, message: str) -> str:
    """初期コマンド処理"""
    reset_session(user_id)
    
    if '記録' in message:
        update_session(user_id, {'handle_type': '1', 'number': 1})
        return "📅 日付を入力してください。\n例: 2025/11/17"
    
    elif '履歴' in message:
        update_session(user_id, {'handle_type': '2', 'number': 1})
        customers = customer_service.get_customers(user_id)
        
        if not customers:
            reset_session(user_id)
            return "📋 顧客データがありません。\n\nまずは「記録」から商談を記録してください。"
        
        formatted_list = ai_handler.format_customer_list(customers)
        return f"{formatted_list}\n\n履歴を見たい顧客のIDを入力してください。"
    
    return "「記録」または「履歴」を入力してください。"

def handle_date_input(user_id: str, message: str, session: dict) -> str:
    """日付入力処理"""
    update_session(user_id, {'date': message, 'number': 2})
    return "🕐 時間を入力してください。\n例: 14:30"

def handle_time_input(user_id: str, message: str, session: dict) -> str:
    """時間入力処理"""
    update_session(user_id, {'time': message, 'number': 3})
    return "👤 顧客名を入力してください。\n\n過去に記録した顧客の場合は、顧客IDでも入力できます。"

def handle_customer_input(user_id: str, message: str, session: dict) -> str:
    """顧客名/ID入力処理"""
    if is_numeric_id(message):
        # ID入力の場合
        customer = customer_service.get_customer_by_id(int(message), user_id)
        if customer:
            update_session(user_id, {'client': customer['client'], 'number': 4})
            return f"✅ 顧客: {customer['client']}\n\n📝 商談内容を入力してください。\n※商談できなかった場合は「なし」と送信してください。"
        else:
            return "❌ 該当する顧客が見つかりません。\n\n顧客名を直接入力するか、正しいIDを入力してください。"
    else:
        # 名前入力の場合
        update_session(user_id, {'client': message, 'number': 4})
        return "📝 商談内容を入力してください。\n※商談できなかった場合は「なし」と送信してください。"

def handle_appointment_detail_input(user_id: str, message: str, session: dict) -> str:
    """商談内容入力処理"""
    update_session(user_id, {'appointment_detail': message, 'number': 0})
    
    confirmation = f"""
✅ 以下の内容で記録します:

📅 日付: {session['date']}
🕐 時間: {session['time']}
👤 顧客: {session['client']}
📝 商談内容: {message}

よろしいですか？

1️⃣ 記録する
2️⃣ 日付を修正
3️⃣ 時間を修正
4️⃣ 顧客名を修正
5️⃣ 商談内容を修正
"""
    return confirmation

def handle_confirmation_choice(user_id: str, choice: str, session: dict) -> str:
    """確認画面での選択処理"""
    if choice == '1':
        # 記録実行
        try:
            # 顧客登録（存在しない場合）
            if not customer_service.customer_exists(session['client'], user_id):
                customer_service.create_customer(session['client'], user_id, user_id)
                logger.info(f"New customer created: {session['client']}")
            
            # 商談記録
            appointment_data = {
                'date': session['date'],
                'time': session['time'],
                'client': session['client'],
                'appointment_detail': session['appointment_detail'],
                'sys_user_id': user_id,
                'sys_conversation_id': user_id
            }
            appointment_service.create_appointment(appointment_data)
            
            reset_session(user_id)
            return "✅ 記録しました！\n\n営業お疲れ様でした！💪"
        except Exception as e:
            logger.error(f"Error saving appointment: {e}")
            return "❌ 記録中にエラーが発生しました。もう一度お試しください。"
    
    elif choice == '2':
        update_session(user_id, {'number': 1})
        return "📅 日付を入力してください。"
    
    elif choice == '3':
        update_session(user_id, {'number': 2})
        return "🕐 時間を入力してください。"
    
    elif choice == '4':
        update_session(user_id, {'number': 3})
        return "👤 顧客名を入力してください。"
    
    elif choice == '5':
        update_session(user_id, {'number': 4})
        return "📝 商談内容を入力してください。"
    
    return "1〜5の数字を入力してください。"

def handle_history_customer_selection(user_id: str, message: str) -> str:
    """履歴表示の顧客選択処理"""
    try:
        customer_id = int(message)
        customer = customer_service.get_customer_by_id(customer_id, user_id)
        
        if not customer:
            return "❌ 該当する顧客が見つかりません。\n\n正しいIDを入力してください。"
        
        # 商談履歴取得
        appointments = appointment_service.get_appointments(user_id, customer['client'])
        
        if not appointments:
            reset_session(user_id)
            return f"📋 {customer['client']} の商談履歴はありません。"
        
        # AI アドバイス生成
        advice = ai_handler.generate_sales_advice(appointments)
        
        reset_session(user_id)
        return f"📊 {customer['client']} の営業分析\n\n{advice}"
        
    except ValueError:
        return "❌ 数字で入力してください。"
    except Exception as e:
        logger.error(f"Error in history selection: {e}")
        reset_session(user_id)
        return "エラーが発生しました。もう一度「履歴」から始めてください。"