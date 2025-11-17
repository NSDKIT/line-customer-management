# LINE 顧客管理システム

LINEと連携した顧客管理・商談記録システム

## セットアップ

1. 仮想環境作成
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 依存関係インストール
```bash
pip install -r requirements.txt
```

3. 環境変数設定
```bash
cp .env.example .env
# .env ファイルを編集して実際の値を設定
```

4. アプリ起動
```bash
python app.py
```

## 機能

- 商談記録の登録
- 顧客情報管理
- AI による営業支援アドバイス
- 履歴検索・表示

## 技術スタック

- Python 3.11
- Flask
- LINE Messaging API
- Supabase
- Anthropic Claude API
- OpenAI GPT-4 API