import google.generativeai as genai
import requests
import os
import schedule
import time
import datetime

# ==========================================
# 🔑 1. 鍵の設定（Renderの環境変数から自動取得）
# ==========================================
# GitHubにパスワードを載せない安全な書き方に変更しました
GEMINI_API_KEY = os.environ.get('AIzaSyClEL9T-jmoris2TYsxQUez4EwOZSZLrko')
NEWS_API_KEY = os.environ.get('170a8c8ad637438993234b2bb1340573')
LINE_ACCESS_TOKEN = os.environ.get('SJS8vWjHrhMa8Zd9bhmxX1HkxZN/mhIhPVTkLua7hGE1kBfg/TjyV0M2EZkitpkHqi2LQb4CxTZPJd4+7wVOhRice/qUm/wilYMvVBSpevcypFaM9zwbx0u/IsUdno1mn046y7GeHAxP0kT+ANyfigdB04t89/1O/w1cDnyilFU=')
LINE_USER_ID = os.environ.get('U3bc1f38552d1dfba930c8349b6fa19fc')

# ==========================================
# 📦 2. ニュース取得〜LINE送信のメイン処理
# ==========================================
def my_daily_news():
    print(f"⏰ 実行開始：{datetime.datetime.now()}")
    
    # AIの準備
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') # 最新の安定版モデル名

    # ニュースを集める
    url = "https://newsapi.org/v2/everything"
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    params = {
        "q": '(Windows 11 OR "Copilot+" OR NPU OR Intel OR AMD OR NVIDIA) AND "窓の杜"',
        "from": yesterday.isoformat(),
        "language": "jp",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("status") == "ok":
            articles = data["articles"]
            news_text = ""
            for i in range(min(5, len(articles))):
                news_text += f"【ニュース{i+1}】{articles[i]['title']}\n内容：{articles[i]['description']}\n\n"
            
            # Geminiでレポート作成
            prompt = f"""
            あなたは「窓の杜」の鋭い記者です。
            今日届いたばかりの最新トピックを、Windowsユーザーの視点で分析してください。

            【編集方針】
            1. 昨日の情報の焼き直しではなく、今日明らかになった「差分（新しい事実）」フォーカスすること。
            2. もしニュースが少ない場合は、無理に水増しせず、1件を深く掘り下げるか「今日は平穏です」と正直に伝えること。

            【出力構成】
            ・【タイトル】：目を引く絵文字付きの見出し
            ・【最新の事実】：箇条書きで、技術的な変更点を正確に。
            ・【窓の杜的な視点】：このニュースが今のWindows環境にどう影響するか。

            【重要：合計1,500文字以内で簡潔に！】
            {news_text}
            """
            
            ai_response = model.generate_content(prompt)
            report_text = ai_response.text 
            
            # LINEへ送信
            line_url = "https://api.line.me/v2/bot/message/push"
            line_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
            }
            line_payload = {
                "to": LINE_USER_ID,
                "messages": [{"type": "text", "text": report_text}]
            }
            
            line_res = requests.post(line_url, headers=line_headers, json=line_payload)
            
            if line_res.status_code == 200:
                print("✨ LINE送信に成功しました！")
            else:
                print(f"⚠️ LINE送信失敗: {line_res.text}")
        else:
            print("❌ ニュースの取得に失敗しました。")

    except Exception as e:
        print(f"❌ 予期せぬエラーが発生しました: {e}")

# ==========================================
# ⏰ 3. 予約と待機
# ==========================================
# 毎日「07:00」に実行（RenderのTZ設定がAsia/Tokyoなら日本時間になります）
schedule.every().day.at("07:00").do(my_daily_news)

print("⏰ 待機モード起動。毎朝07:00に窓の杜風ニュースをお届けします。")

while True:
    schedule.run_pending()
    time.sleep(60)
