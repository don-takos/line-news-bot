import requests
import google.generativeai as genai

# ==========================================
# 🔑 1. あなたの魔法の鍵たち（4つに増えました！）
# ==========================================
NEWS_API_KEY = "170a8c8ad637438993234b2bb1340573"
GOOGLE_API_KEY = "AIzaSyClEL9T-jmoris2TYsxQUez4EwOZSZLrko"
LINE_ACCESS_TOKEN = "SJS8vWjHrhMa8Zd9bhmxX1HkxZN/mhIhPVTkLua7hGE1kBfg/TjyV0M2EZkitpkHqi2LQb4CxTZPJd4+7wVOhRice/qUm/wilYMvVBSpevcypFaM9zwbx0u/IsUdno1mn046y7GeHAxP0kT+ANyfigdB04t89/1O/w1cDnyilFU="
LINE_USER_ID = "U3bc1f38552d1dfba930c8349b6fa19fc"

# ==========================================
# 🧠 2. AI（Gemini）の準備
# ==========================================
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================
# 🎣 3. ニュースを集める
# ==========================================
print("🌍 インターネットの海から最新情報を一本釣りしています...")
url = "https://newsapi.org/v2/everything"
# 3. ニュースを集める（「最新」かつ「窓の杜」らしさを強制！）
import datetime

# 今日の日付を取得（24時間以内の記事に絞るため）
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

params = {
    # 検索ワードに「窓の杜」を必須としつつ、OSやチップの核心ワードを組み合わせる
    "q": '(Windows 11 OR "Copilot+" OR NPU OR Intel OR AMD OR NVIDIA) AND "窓の杜"',
    "from": yesterday.isoformat(), # 【重要】24時間以内に公開された記事だけに限定
    "language": "jp",
    "sortBy": "publishedAt",      # 【重要】関連度ではなく「公開日時順」で最新を拾う
    "pageSize": 5,
    "apiKey": NEWS_API_KEY
}

response = requests.get(url, params=params)
data = response.json()

if data.get("status") == "ok":
    articles = data["articles"]
    
    news_text = ""
    for i in range(min(5, len(articles))):
        news_text += f"【ニュース{i+1}】{articles[i]['title']}\n内容：{articles[i]['description']}\n\n"
        
    # ==========================================
    # 📝 4. Geminiに「プロの分析官」として指示を出す
    # ==========================================
    print("🧠 Geminiが記事を読み込み、投資家＆ガジェット好き目線で分析中...")
    prompt = f"""
    あなたは「窓の杜」の鋭い記者です。
    今日届いたばかりの最新トピックを、Windowsユーザーの視点で分析してください。

    【編集方針】
    1. 昨日の情報の焼き直しではなく、今日明らかになった「差分（新しい事実）」にフォーカスすること。
    2. もしニュースが少ない場合は、無理に水増しせず、1件を深く掘り下げるか「今日は平穏です」と正直に伝えること。

    【出力構成】
    ・【タイトル】：目を引く絵文字付きの見出し
    ・【最新の事実】：箇条書きで、技術的な変更点を正確に。
    ・【窓の杜的・考察】：このニュースが今のWindows環境にどう影響するか。

    【重要：合計1,500文字以内で簡潔に！】
    {news_text}
    """
    
    ai_response = model.generate_content(prompt)
    report_text = ai_response.text  # Geminiが書いたレポートを変数に保存
    
    print("\n==================================================")
    print(" 📰 レポート完成！画面に表示しつつ、LINEにも送信します ")
    print("==================================================\n")
    print(report_text)
    
    # ==========================================
    # 📱 5. LINEにレポートを送信する！
    # ==========================================
    print("\n🚀 LINEへメッセージを送信中...")
    line_url = "https://api.line.me/v2/bot/message/push"
    line_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    line_payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": report_text}]
    }
    
    # LINEのサーバーに送信！
    line_res = requests.post(line_url, headers=line_headers, json=line_payload)
    
    if line_res.status_code == 200:
        print("✨ LINEへの送信が大成功しました！スマホを確認してください！")
    else:
        print(f"⚠️ LINE送信エラー: {line_res.status_code}")
        print(line_res.text)

else:
    print("ニュースの取得に失敗しました。鍵が間違っていないか確認してください。")