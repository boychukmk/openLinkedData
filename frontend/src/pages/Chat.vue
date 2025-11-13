<template>
  <div class="chat-page">
    <div class="chat-layout">
      <aside class="sidebar">
        <h3>FAQ</h3>
        <ul>
          <li @click="quickSend('Headache?')">🧠 Headache</li>
          <li @click="quickSend('itchy skin')">💓 Itchy skin</li>
          <li @click="quickSend('Drugs for Immunity')">💊 Immunity Vitamins</li>
          <li @click="quickSend('Diabetes')">🍭 Diabetes </li>
        </ul>
      </aside>

      <!-- Чат -->
      <div class="chat-box">
        <h2>Chat </h2>
        <div class="messages" ref="chatContainer">
          <div
            v-for="msg in messages"
            :key="msg.id"
            :class="['message', msg.user ? 'user' : 'bot']"
          >
            <p>{{ msg.text }}</p>
          </div>
        </div>
        <div class="input-row">
          <input
            v-model="message"
            @keyup.enter="sendMessage"
            placeholder="Enter your question..."
          />
          <button @click="sendMessage">Send</button>
        </div>
      </div>
    </div>

    <div class="background-decoration" />
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      message: "",
      messages: [],
    };
  },
  methods: {
    async sendMessage() {
      const text = this.message.trim();
      if (!text) return;

      this.messages.push({ id: Date.now(), text, user: true });
      this.scrollToBottom();

      try {
        const { data } = await axios.post("http://127.0.0.1:8000/api/chat", {
          message: text,
        });

        this.messages.push({
          id: Date.now() + 1,
          text: data.reply || "⚠️ No response!",
          user: false,
        });
      } catch (err) {
        this.messages.push({
          id: Date.now() + 2,
          text: "❌ Error while connecting to server.",
          user: false,
        });
      } finally {
        this.message = "";
        this.scrollToBottom();
      }
    },
    quickSend(text) {
      this.message = text;
      this.sendMessage();
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.chatContainer;
        el.scrollTop = el.scrollHeight;
      });
    },
  },
};
</script>

<style>
.chat-page {
  padding-top: 120px;
  position: relative;
  min-height: 100vh;
  background: var(--bg-gradient);
  display: flex;
  align-items: stretch;
  justify-content: center;
  box-sizing: border-box;
  overflow: hidden;
}

.chat-layout {
  display: flex;
  width: 100%;
  max-width: 1200px;
  gap: 24px;
  z-index: 2;
}

/* Ліва колонка */
.sidebar {
  width: 300px;
  background: var(--card-bg);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  color: var(--text-color);
  height: 80vh;
  overflow-y: auto;
}

.sidebar h3 {
  margin-bottom: 12px;
  font-size: 1.1rem;
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.sidebar li:hover {
  background: var(--chat-bg);
}

/* Чат */
.chat-box {
  flex-grow: 1;
  background-color: var(--card-bg);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 80vh;
}

.chat-box h2 {
  text-align: center;
  margin-bottom: 16px;
  color: var(--text-color);
}

.messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: var(--chat-bg);
  border-radius: 12px;
  margin-bottom: 12px;
  scroll-behavior: smooth;
}

.message {
  margin-bottom: 12px;
  max-width: 75%;
  word-wrap: break-word;
  padding: 12px 16px;
  border-radius: 16px;
  line-height: 1.5;
  font-size: 0.95rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.message.user {
  margin-left: auto;
  background: var(--user-bubble);
  color: white;
}

.message.bot {
  background: var(--bot-bubble);
  color: var(--text-color);
}

.input-row {
  display: flex;
  gap: 10px;
}

input {
  flex-grow: 1;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--input-bg);
  color: var(--text-color);
  font-size: 1rem;
}

button {
  padding: 12px 20px;
  border: none;
  background: var(--accent);
  color: white;
  border-radius: 12px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
}

button:hover {
  background: var(--accent-hover);
}

.background-decoration {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top left, rgba(0, 200, 255, 0.08), transparent 70%),
  radial-gradient(circle at bottom right, rgba(128, 0, 255, 0.08), transparent 70%);
  z-index: 0;
  pointer-events: none;
}

/* Теми */
:root[data-theme="light"] {
  --bg-gradient: linear-gradient(to right, #f5f9ff, #eaf3fa);
  --card-bg: #ffffff;
  --chat-bg: #f3f7fb;
  --text-color: #1a1a1a;
  --border-color: #ccc;
  --input-bg: #fff;
  --user-bubble: #26a69a;
  --bot-bubble: #e0ecf7;
  --accent:#26a69a;
  --accent-hover: #43cea2;
}

:root[data-theme="dark"] {
  --bg-gradient: linear-gradient(to right, #111827, #1f2937);
  --card-bg: #1e1e2f;
  --chat-bg: #2c2c3f;
  --text-color: #f9f9f9;
  --border-color: #444;
  --input-bg: #2a2a3a;
  --user-bubble: #00796b;
  --bot-bubble: #374151;
  --accent: #00796b;
  --accent-hover: #26a69a;
}
</style>
