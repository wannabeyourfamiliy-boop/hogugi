# app.py — 호국이 캐릭터용 화이트 테마 웹 UI + 서버

import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

# 👉 파인튜닝된 모델 이름 입력 (예: "ft:gpt-3.5-turbo-0125:personal::CSvnpVKj")
HOGUK_MODEL = "ft:gpt-3.5-turbo-0125:personal::CSvnpVKj"

# OpenAI 클라이언트 설정 (Render 환경변수 OPENAI_API_KEY 사용)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# ---------------------- HTML (화이트 테마) ----------------------
HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>호국이랑 수다 타임 🐯</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      --bg: #f8fafc;
      --card: #ffffff;
      --accent: #16a34a;
      --accent-light: #bbf7d0;
      --border: #e2e8f0;
      --text-main: #111827;
      --text-sub: #475569;
      --user-bubble: #bbf7d0;
      --bot-bubble: #f1f5f9;
      --scrollbar: #cbd5e1;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
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
      .shell { grid-template-columns: 1fr; }
    }
    .card {
      background: var(--card);
      border-radius: 20px;
      border: 1px solid var(--border);
      padding: 20px 18px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.05);
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
      background: radial-gradient(circle at 30% 20%, #bbf7d0 0, #16a34a 80%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      color: #065f46;
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
      background: var(--accent-light);
      font-size: 0.75rem;
      color: #065f46;
    }
    .title-sub { margin: 0; font-size: 0.86rem; color: var(--text-sub); }

    .chat {
      border-radius: 16px;
      border: 1px solid var(--border);
      background: #f9fafb;
      padding: 12px;
      height: 430px;
      overflow-y: auto;
      scroll-behavior: smooth;
    }
    .chat::-webkit-scrollbar { width: 6px; }
    .chat::-webkit-scrollbar-thumb {
      background: var(--scrollbar);
      border-radius: 999px;
    }
    .msg-row { margin: 10px 0; display: flex; }
    .msg-row.user { justify-content: flex-end; }
    .msg-row.bot { justify-content: flex-start; }
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
      color: #064e3b;
      border-bottom-right-radius: 4px;
    }
    .bubble.bot {
      background: var(--bot-bubble);
      border: 1px solid #e2e8f0;
      border-bottom-left-radius: 4px;
    }
    .bubble-label {
      font-size: 0.7rem;
      margin-bottom: 2px;
      opacity: 0.8;
      color: var(--text-sub);
    }
    .row { margin-top: 12px; display: flex; gap: 8px; }
    input {
      flex: 1;
      padding: 11px 12px;
      border-radius: 999px;
      border: 1px solid #d1d5db;
      outline: none;
      background: #fff;
      color: var(--text-main);
      font-size: 0.9rem;
    }
    input::placeholder { color: #94a3b8; }
    button {
      padding: 0 18px;
      border-radius: 999px;
      border: none;
      background: linear-gradient(135deg, #16a34a, #22c55e);
      color: #fff;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 4px 10px rgba(22,163,74,0.3);
      transition: transform 0.07s ease, box-shadow 0.07s ease, filter 0.1s ease;
    }
    button:hover {
      transform: translateY(-1px);
      box-shadow: 0 8px 18px rgba(22,163,74,0.4);
      filter: brightness(1.05);
    }
    button:disabled { opacity: 0.6; cursor: default; box-shadow: none; transform: none; }
    .hint {
      margin-top: 8px;
      font-size: 0.78rem;
      color: var(--text-sub);
    }
    .hint span {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      background: #f1f5f9;
      border: 1px solid #e2e8f0;
      margin-right: 6px;
      margin-top: 4px;
      cursor: pointer;
    }
    .right { display: flex; flex-direction: column; gap: 10px; }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--accent-light);
      color: #065f46;
    }
    .right h2 { font-size: 1.05rem; margin: 6px 0 4px; }
    .right p { margin: 0; font-size: 0.83rem; color: var(--text-sub); line-height: 1.5; }
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
      background: #f9fafb;
      border: 1px solid #e2e8f0;
    }
    .footer {
      margin-top: 10px;
      font-size: 0.7rem;
      color: #94a3b8;
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
    <!-- 왼쪽: 채팅 영역 -->
    <div class="card">
      <div class="left-header">
        <div class="avatar">🐯</div>
        <div class="title-box">
          <h1>호국이 훈련소 <span class="title-pill">화이트 버전 ☁️</span></h1>
          <p class="title-sub">밝고 상큼한 분위기에서 호국이와 수다 떠세요!</p>
        </div>
      </div>

      <div class="chat" id="chat">
        <div class="msg-row bot">
          <div class="bubble bot">
            <div class="bubble-label">🐯 호국이</div>
            안녕! 반가워요 ☀️<br>
            오늘 하루는 어땠어요?<br>
            기분을 말해주면 호국이가 힘차게 응원해줄게요! 💪
          </div>
        </div>
      </div>

      <div class="row">
        <input id="q" placeholder="예: 호국아, 오늘 너무 피곤해..." />
        <button id="sendBtn" onclick="send()">
          <span>보내기</span> <span>🚀</span>
        </button>
      </div>
      <div class="hint">
        <div>예시 질문:</div>
        <span onclick="fill('호국아, 나 오늘 너무 피곤해...')">피곤할 때</span>
        <span onclick="fill('호국아, 나 자신감이 없어.')">자신감 없을 때</span>
        <span onclick="fill('호국아, 나 군대 가기 무서워...')">무서울 때</span>
      </div>
      <div id="status" class="status"></div>
    </div>

    <!-- 오른쪽 설명 영역 -->
    <div class="card right">
      <div class="badge">💡 호국이 소개</div>
      <h2>국민의 든든한 친구, 호국이</h2>
      <p>
        호국이는 대한민국 육군을 모티프로 만든 밝고 유쾌한 AI 캐릭터예요.<br>
        언제나 긍정 에너지로 당신의 하루를 응원합니다 🌱
      </p>

      <div class="pill-list">
        <div class="pill">💪 무한 긍정</div>
        <div class="pill">🐯 씩씩한 매력</div>
        <div class="pill">🌿 따뜻한 공감</div>
        <div class="pill">🚫 정치 · 민원 X</div>
      </div>

      <p style="margin-top:10px;">
        이 화면은 샘플 디자인이에요.<br>
        실제 서비스용으로 색상, 폰트만 조정해도 충분히 사용 가능!
      </p>

      <div class="footer">
        로컬 개발용 데모 화면입니다. 새로고침 시 대화가 초기화됩니다.
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
  statusEl.textContent = '호국이는 대답 준비 중... 🔄';
  sendBtn.disabled = true;
  try {
    const res = await fetch('/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    if (data.reply) appendMessage('bot', data.reply);
    else appendMessage('bot', '⚠️ 오류가 발생했어요. 잠시 후 다시 시도해주세요.');
  } catch(e) {
    appendMessage('bot', '⚠️ 네트워크 오류가 발생했어요.');
  } finally {
    sendBtn.disabled = false;
    statusEl.textContent = '';
  }
}
function fill(text) { input.value = text; input.focus(); }
input.addEventListener('keydown', (e)=>{ if(e.key === 'Enter') send(); });
</script>
</body>
</html>
"""
# ---------------------- HTML 끝 ----------------------


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
                        "밝고 유쾌하며, 따뜻한 말투로 사람들을 응원하고 위로하세요. "
                        "군사 기밀, 정치적 논쟁, 개인 민원은 정중히 거절하세요."
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
