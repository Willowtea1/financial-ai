<template>
  <v-dialog
    v-model="dialog"
    max-width="800"
    persistent
    scrollable
  >
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="text-h5">Refine Your Plan with AI</span>
        <v-btn icon variant="text" @click="closeDialog">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <!-- Chat Messages -->
      <v-card-text style="height: 500px;" class="pa-4">
        <div ref="messagesContainer" class="messages-container">
          <v-alert
            type="info"
            variant="tonal"
            class="mb-4"
          >
            Ask me anything about your financial plan. I can help you refine it or answer questions.
          </v-alert>

          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']"
          >
            <v-avatar
              :color="message.role === 'user' ? 'primary' : 'secondary'"
              size="32"
              class="mr-3"
            >
              <v-icon color="white">
                {{ message.role === 'user' ? 'mdi-account' : 'mdi-robot' }}
              </v-icon>
            </v-avatar>
            <div class="message-content">
              <div v-html="formatText(message.content)"></div>
            </div>
          </div>

          <div v-if="loading" class="message ai-message">
            <v-avatar color="secondary" size="32" class="mr-3">
              <v-icon color="white">mdi-robot</v-icon>
            </v-avatar>
            <div class="message-content">
              <v-progress-circular
                indeterminate
                size="24"
                color="primary"
              ></v-progress-circular>
            </div>
          </div>
        </div>
      </v-card-text>

      <v-divider></v-divider>

      <!-- Chat Input -->
      <v-card-actions class="pa-4">
        <v-text-field
          v-model="userMessage"
          placeholder="Ask about your financial plan..."
          variant="outlined"
          density="comfortable"
          hide-details
          @keyup.enter="sendMessage"
          :disabled="loading"
          class="mr-2"
        ></v-text-field>
        <v-btn
          color="primary"
          @click="sendMessage"
          :disabled="!userMessage.trim() || loading"
          :loading="loading"
        >
          <v-icon left>mdi-send</v-icon>
          Send
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import axios from 'axios'

const props = defineProps({
  modelValue: Boolean,
  planData: Object
})

const emit = defineEmits(['update:modelValue', 'plan-updated'])

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const messages = ref([])
const userMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const formatText = (text) => {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const closeDialog = () => {
  dialog.value = false
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!userMessage.value.trim() || loading.value) return

  const message = userMessage.value.trim()
  userMessage.value = ''

  // Add user message
  messages.value.push({
    role: 'user',
    content: message
  })

  loading.value = true
  await scrollToBottom()

  try {
    const response = await axios.post('/api/refine-plan', {
      message: message,
      planData: props.planData,
      chatHistory: messages.value.slice(0, -1) // Exclude the current user message
    })

    const aiResponse = response.data

    // Add AI response
    messages.value.push({
      role: 'assistant',
      content: aiResponse.message
    })

    // If plan was updated, emit the updated plan
    if (aiResponse.updatedPlan) {
      emit('plan-updated', aiResponse.updatedPlan)
    }

    await scrollToBottom()
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.'
    })
    await scrollToBottom()
  } finally {
    loading.value = false
  }
}

watch(dialog, (newVal) => {
  if (newVal) {
    messages.value = []
    userMessage.value = ''
    nextTick(() => {
      scrollToBottom()
    })
  }
})
</script>

<style scoped>
.messages-container {
  height: 100%;
  overflow-y: auto;
}

.message {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}

.user-message {
  flex-direction: row-reverse;
}

.message-content {
  flex: 1;
  padding: 12px 16px;
  border-radius: 16px;
  max-width: 70%;
}

.user-message .message-content {
  background-color: rgb(25, 118, 210);
  color: white;
}

.ai-message .message-content {
  background-color: #f5f5f5;
  color: #333;
}
</style>
