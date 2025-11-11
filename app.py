# app.py — 호국이 캐릭터용 예쁜 웹 UI + 서버

import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

# 👉 여기에 파인튜닝 끝난 "호국이" 모델 이름 넣으세요
# 예시: HOGUK_MODEL = "ft:gpt-3.5-turbo-0125:org:hoguki-cheerful-v2:abc123"
HOGUK_MODEL = "ft:gpt-3.5-turbo-0125:personal::CSvnpVKj"  # 임시값, 나중에 바꾸기!

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>호국이랑 수다 타임 🐯</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      --bg: #0f172a;
      --card: #111827;
      --accent: #22c55e;
      --accent-soft: rgba(34,197,94,0.1);
      --border: #1f2937;
      --text-main: #e5e7eb;
      --text-sub: #9ca3af;
      --user-bubble: #22c55e;
      --bot-bubble: #111827;
      --scrollbar: #4b5563;
    }
    * {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top, #1f2937 0, #020617 55%, #000 100%);
      color: var(--text-main);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px 12px;
    }
    .shell {
      width: 100%;
      max-width: 960px;
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
      gap: 20px;
    }
    @media (max-width: 800px) {
      .shell {
        grid-template-columns: minmax(0, 1fr);
      }
    }
    .card {
      background: rgba(15,23,42,0.95);
      border-radius: 20px;
      border: 1px solid var(--border);
      padding: 20px 18px;
      box-shadow: 0 18px 45px rgba(0,0,0,0.55);
      backdrop-filter: blur(16px);
    }
    .left-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
    }
    .avatar {
      width: 46px;
      height: 46px;
      border-radius: 999px;
      background: radial-gradient(circle at 30% 20%, #bbf7d0 0, #22c55e 35%, #16a34a 75%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      box-shadow: 0 0 0 3px rgba(34,197,94,0.35);
    }
    .title-box h1 {
      font-size: 1.25rem;
      margin: 0 0 2px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .title-pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--accent-soft);
      font-size: 0.75rem;
      color: #bbf7d0;
    }
    .title-sub {
      margin: 0;
      font-size: 0.86rem;
      color: var(--text-sub);
    }

    .chat {
      border-radius: 16px;
      border: 1px solid var(--border);
      background: radial-gradient(circle at top left, rgba(34,197,94,0.09), rgba(15,23,42,0.98));
      padding: 12px;
      height: 430px;
      overflow-y: auto;
      scroll-behavior: smooth;
    }
    .chat::-webkit-scrollbar {
      width: 6px;
    }
    .chat::-webkit-scrollbar-thumb {
      background: var(--scrollbar);
      border-radius: 999px;
    }
    .msg-row {
      margin: 10px 0;
      display: flex;
    }
    .msg-row.user {
      justify-content: flex-end;
    }
    .msg-row.bot {
      justify-content: flex-start;
    }
    .bubble {
      max-width: 82%;
      padding: 9px 12px;
      border-radius: 14px;
      font-size: 0.9rem;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
      position: relative;
    }
    .bubble.user {
      background: var(--user-bubble);
      color: #052e16;
      border-bottom-right-radius: 4px;
    }
    .bubble.bot {
      background: rgba(15,23,42,0.96);
      border: 1px solid rgba(148,163,184,0.3);
      border-bottom-left-radius: 4px;
      color: var(--text-main);
    }
    .bubble-label {
      font-size: 0.7rem;
      margin-bottom: 2px;
      opacity: 0.8;
    }
    .row {
      margin-top: 12px;
      display: flex;
      gap: 8px;
    }
    input {
      flex: 1;
      padding: 11px 12px;
      border-radius: 999px;
      border: 1px solid #4b5563;
      outline: none;
      background: #020617;
      color: var(--text-main);
      font-size: 0.9rem;
    }
    input::placeholder {
      color: #6b7280;
    }
    button {
      padding: 0 18px;
      border-radius: 999px;
      border: none;
      background: linear-gradient(135deg, #22c55e, #16a34a);
      color: #022c22;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 10px 25px rgba(22,163,74,0.45);
      transition: transform 0.07s ease, box-shadow 0.07s ease, filter 0.1s ease;
      white-space: nowrap;
    }
    button:hover {
      transform: translateY(-1px);
      box-shadow: 0 16px 35px rgba(22,163,74,0.6);
      filter: brightness(1.03);
    }
    button:active {
      transform: translateY(0);
      box-shadow: 0 8px 18px rgba(22,163,74,0.45);
    }
    button:disabled {
      opacity: 0.6;
      cursor: default;
      box-shadow: none;
      transform: none;
    }
    .hint {
      margin-top: 8px;
      font-size: 0.78rem;
      color: var(--text-sub);
    }
    .hint span {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      background: rgba(15,23,42,0.8);
      border: 1px solid rgba(148,163,184,0.4);
      margin-right: 6px;
      margin-top: 4px;
      cursor: pointer;
    }
    .right {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(34,197,94,0.1);
      color: #bbf7d0;
    }
    .right h2 {
      font-size: 1.05rem;
      margin: 6px 0 4px;
    }
    .right p {
      margin: 0;
      font-size: 0.83rem;
      color: var(--text-sub);
      line-height: 1.5;
    }
    .pill-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }
    .pill {
      font-size: 0.78rem;
      padding: 4px 9px;
      border-radius: 999px;
      background: rgba(15,23,42,0.9);
      border: 1px solid rgba(55,65,81,0.9);
    }
    .footer {
      margin-top: 10px;
      font-size: 0.7rem;
      color: #6b7280;
    }
    .status {
      margin-top: 4px;
      font-size: 0.75rem;
      color: var(--text-sub);
      min-height: 1em;
    }
  </style>
</head>
<body>
  <div class="shell">
    <!-- 왼쪽: 실제 채팅 -->
    <div class="card">
      <div class="left-header">
        <div class="avatar">🐯</div>
        <div class="title-box">
          <h1>호국이 훈련소 <span class="title-pill">실험실 버전 💻</span></h1>
          <p class="title-sub">귀엽고 유쾌한 육군 캐릭터 ‘호국이’와 대화해 보세요!</p>
        </div>
      </div>

      <div class="chat" id="chat">
        <div class="msg-row bot">
          <div class="bubble bot">
            <div class="bubble-label">🐯 호국이</div>
            안녕안녕~ 호국이에요! 💪<br>
            오늘은 어떤 하루였나요?<br>
            편하게 말 걸어주시면, 호국이가 힘껏 응원해 드릴게요! 🎺
          </div>
        </div>
      </div>

      <div class="row">
        <input id="q" placeholder="예: 호국아, 오늘 너무 지쳤어..." />
        <button id="sendBtn" onclick="send()">
          <span>보내기</span> <span>🚀</span>
        </button>
      </div>
      <div class="hint">
        <div>예시 질문:</div>
        <span onclick="fill('호국아, 나 오늘 너무 피곤해...')">호국아, 나 오늘 너무 피곤해...</span>
        <span onclick="fill('호국아, 나 자신감이 없어.')">나 자신감이 없어.</span>
        <span onclick="fill('호국아, 나 군대 가기 무서워...')">군대가 무서워...</span>
      </div>
      <div id="status" class="status"></div>
    </div>

    <!-- 오른쪽: 설명 / 컨셉 -->
    <div class="card right">
      <div class="badge">💡 호국이 소개</div>
      <h2>국민의 든든한 친구, 호국이</h2>
      <p>
        호국이는 대한민국 육군을 모티프로 만든 귀엽고 유쾌한 AI 캐릭터입니다.<br>
        힘들 땐 응원, 지칠 땐 위로, 불안할 땐 “할 수 있어요!”를 외쳐주는 마음 근육 트레이너예요.
      </p>

      <div class="pill-list">
        <div class="pill">💪 무한 긍정 모드</div>
        <div class="pill">🐯 귀엽고 씩씩한 말투</div>
        <div class="pill">🌿 따뜻한 공감</div>
        <div class="pill">🚫 군사 기밀 · 정치 X</div>
      </div>

      <p style="margin-top:10px;">
        실제 서비스에 쓸 때는 이 화면을 디자인 가이드 삼아<br>
        로고, 색상, 폰트만 육군 스타일로 맞춰도 깔끔하게 쓸 수 있어요.
      </p>

      <div class="footer">
        로컬 개발용 데모 화면입니다. 새로고침하면 대화 내용이 초기화돼요.
      </div>
    </div>
  </div>

<script>
const chatBox = document.getElementById('chat');
const input = document.getElementById('q');
const sendBtn = document.getElementById('sendBtn');
const statusEl = document.getElementById('status');

function appendMessage(who, text) {
  const row = document.createElement('div');
  row.className = 'msg-row ' + who;
  const bubble = document.createElement('div');
  bubble.className = 'bubble ' + who;

  const label = document.createElement('div');
  label.className = 'bubble-label';
  label.textContent = (who === 'user') ? '👤 나' : '🐯 호국이';

  bubble.appendChild(label);
  bubble.appendChild(document.createTextNode(text));
  row.appendChild(bubble);
  chatBox.appendChild(row);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function send() {
  const msg = input.value.trim();
  if (!msg) return;

  appendMessage('user', msg);
  input.value = '';
  input.focus();
  statusEl.textContent = '호국이는 훈련 중이에요... 🔄';
  sendBtn.disabled = true;

  try {
    const res = await fetch('/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    if (data.reply) {
      appendMessage('bot', data.reply);
      statusEl.textContent = '';
    } else {
      appendMessage('bot', '⚠️ 오류가 발생했어요. 잠시 후 다시 시도해 주세요.');
      statusEl.textContent = '';
    }
  } catch(e) {
    appendMessage('bot', '⚠️ 네트워크 오류가 발생했어요.');
    statusEl.textContent = '';
  } finally {
    sendBtn.disabled = false;
  }
}

function fill(text) {
  input.value = text;
  input.focus();
}

input.addEventListener('keydown', (e)=>{
  if(e.key === 'Enter') send();
});
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_msg = (data.get("message") or "").strip()
    if not user_msg:
        return jsonify({"error": "message is required"}), 400

    try:
        resp = client.chat.completions.create(
            model=HOGUK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 ‘호국이’라는 이름의 대한민국 육군 공식 AI 캐릭터입니다. "
                        "귀엽고 유쾌한 말투로, 항상 밝고 긍정적으로 응원하세요. "
                        "군사 기밀, 정치적 논쟁, 개인 민원은 정중히 거절하고 안전한 범위에서 대답하세요."
                    ),
                },
                {"role": "user", "content": user_msg},
            ],
            max_tokens=400,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content
        return jsonify({"reply": answer})
    except Exception as e:
        print("OpenAI error:", e)
        return jsonify({"error": "OpenAI request failed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
