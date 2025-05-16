<script lang="ts" setup>
import { ref, reactive } from 'vue'

interface Message {
  id: number
  sender: 'user' | 'bot'
  text: string
}

const messages = ref<Message[]>([])
const input = ref('')
const loading = ref(false)
const suggestedMessages = ref([
  'Suggest enhancements',
  'Suggest optimization',
  'Suggest indexes',
  'Validate structure',
  'Refine structure',
])

let messageId = 0

function addMessage(sender: 'user' | 'bot', text: string) {
  messages.value.push({ id: ++messageId, sender, text })
}

async function sendMessage() {
  if (!input.value.trim()) return

  addMessage('user', input.value)
  loading.value = true
  const userInput = input.value
  input.value = ''

  // Create reactive bot message
  const botMessage = reactive<Message>({
    id: ++messageId,
    sender: 'bot',
    text: '',
  })
  messages.value.push(botMessage)

  try {
    const response = await fetch('http://127.0.0.1:8000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: userInput }),
    })

    if (!response.body) throw new Error('ReadableStream not supported')

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let done = false

    while (!done) {
      const { value, done: doneReading } = await reader.read()
      done = doneReading
      if (value) {
        // Update reactive botMessage's text
        botMessage.text += decoder.decode(value)
      }
    }
  } catch (error) {
    botMessage.text += '\n[Error fetching response]'
    console.error(error)
  } finally {
    loading.value = false
  }
}

function handleSuggestion(msg: string) {
  input.value = msg
  sendMessage()
}
</script>

<template>
  <div class="chat-container">
    <header class="chat-header">
      <h1>Database Assistant</h1>
      <p>Get expert help with database optimization and structure</p>
    </header>

    <main class="chat-main">
      <div v-if="!messages.length" class="suggestions">
        <div class="suggestion-grid">
          <button
            v-for="(msg, index) in suggestedMessages"
            :key="index"
            @click="handleSuggestion(msg)"
            class="suggestion-button"
          >
            {{ msg }}
          </button>
        </div>
      </div>

      <div class="messages-container">
        <div v-for="msg in messages" :key="msg.id" :class="['chat-message', msg.sender]">
          <div class="message-content" v-html="msg.text.replace(/\n/g, '<br>')"></div>
        </div>
        <div v-if="loading" class="chat-message bot">
          <div class="message-content typing">Analyzing your request...</div>
        </div>
      </div>
    </main>

    <form @submit.prevent="sendMessage" class="chat-input-area">
      <input
        type="text"
        v-model="input"
        :disabled="loading"
        placeholder="Ask about your database structure..."
        autocomplete="off"
        autofocus
      />
      <button type="submit" :disabled="loading || !input.trim()">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    </form>
  </div>
</template>

<style scoped>
.chat-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  font-family:
    'Inter',
    system-ui,
    -apple-system,
    sans-serif;
}

.chat-header {
  padding: 1.5rem 2rem;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e2e8f0;
  text-align: center;
}

.chat-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.chat-header p {
  color: #64748b;
  font-size: 0.875rem;
}

.chat-main {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: linear-gradient(to bottom right, #f8fafc 0%, #f1f5f9 100%);
}

.suggestions {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.suggestion-button {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem;
  text-align: left;
  font-size: 0.875rem;
  color: #1e293b;
  transition: all 0.2s ease;
  cursor: pointer;
}

.suggestion-button:hover {
  background: #f1f5f9;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.messages-container {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-message {
  max-width: 80%;
  padding: 1rem 1.25rem;
  border-radius: 1rem;
  line-height: 1.5;
  font-size: 0.9375rem;
  position: relative;
}

.chat-message.user {
  background: #3b82f6;
  color: white;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

.chat-message.bot {
  background: #ffffff;
  color: #1e293b;
  align-self: flex-start;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chat-input-area {
  padding: 1.5rem 2rem;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 1rem;
}

.chat-input-area input {
  flex: 1;
  padding: 0.875rem 1.25rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  font-size: 0.9375rem;
  background: #ffffff;
  transition: all 0.2s ease;
}

.chat-input-area input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.chat-input-area button {
  padding: 0.75rem 1.25rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-input-area button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background: #94a3b8;
}

.chat-input-area button:hover:not(:disabled) {
  background: #2563eb;
}

.typing {
  color: #64748b;
  font-style: italic;
}

@media (max-width: 768px) {
  .chat-main {
    padding: 1rem;
  }

  .chat-message {
    max-width: 90%;
  }

  .suggestion-grid {
    grid-template-columns: 1fr;
  }
}
</style>
