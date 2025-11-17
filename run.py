from flask import Flask, request, abort
from linebot.exceptions import InvalidSignatureError
from app.config import Config
from app.handlers.line_handler import handler
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 設定検証
try:
    Config.validate()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

# Flask アプリ初期化
app = Flask(__name__)

@app.route("/")
def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "running",
        "service": "LINE Customer Management System",
        "version": "1.0.0"
    }, 200

@app.route("/webhook", methods=['POST'])
def webhook():
    """LINE Webhook エンドポイント"""
    # 署名検証
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        logger.warning("Missing X-Line-Signature header")
        abort(400)
    
    body = request.get_data(as_text=True)
    logger.info(f"Webhook received: {body[:100]}...")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        abort(500)
    
    return 'OK'

@app.errorhandler(404)
def not_found(error):
    return {"error": "Not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return {"error": "Internal server error"}, 500

if __name__ == "__main__":
    logger.info(f"Starting application on port {Config.PORT}")
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )