<template>
  <div>
    <h1>Chat</h1>
    <div class="chat-container">
      <div v-for="msg in messages" :key="msg.id" class="message">
        <strong>{{ msg.user ? "You" : "Bot" }}:</strong> {{ msg.text }}
      </div>
    </div>
    <input v-model="message" @keyup.enter="sendMessage" placeholder="Type a message..." />
    <button @click="sendMessage">Send</button>
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
      if (!this.message.trim()) return;
      this.messages.push({ id: Date.now(), text: this.message, user: true });

      try {
        const response = await axios.post("http://127.0.0.1:8000/api/chat", { message: this.message });
        this.messages.push({ id: Date.now() + 1, text: response.data.reply, user: false });
      } catch (error) {
        console.error("Error sending message:", error);
      }

      this.message = "";
    },
  },
};
</script>

<style scoped>
.chat-container {
  border: 1px solid #ddd;
  padding: 10px;
  height: 300px;
  overflow-y: auto;
  background: #f9f9f9;
  margin-bottom: 10px;
}
.message {
  margin-bottom: 5px;
}
input {
  width: 80%;
  padding: 8px;
}
button {
  padding: 8px;
}
</style>
