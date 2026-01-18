<template>
  <v-container fluid class="chatbot-container pa-0" style="height: 100vh;">
    <!-- Top Navigation Bar -->
    <v-app-bar elevation="1" color="white" density="comfortable">
      <v-app-bar-title class="d-flex align-center">
        <img :src="robotIcon" alt="AI" class="robot-icon-nav mr-2" />
        <span class="font-weight-bold">Financial AI Assistant</span>
      </v-app-bar-title>
      
      <v-spacer></v-spacer>
      
      <!-- User Menu -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-icon>mdi-account-circle</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="clearChat">
            <template v-slot:prepend>
              <v-icon>mdi-delete-outline</v-icon>
            </template>
            <v-list-item-title>Clear Chat</v-list-item-title>
          </v-list-item>
          <v-list-item @click="retakeQuestionnaire">
            <template v-slot:prepend>
              <v-icon>mdi-clipboard-text-outline</v-icon>
            </template>
            <v-list-item-title>Retake Questionnaire</v-list-item-title>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="handleLogout">
            <template v-slot:prepend>
              <v-icon>mdi-logout</v-icon>
            </template>
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Loading Overlay - REMOVED -->
    <!-- Loading is now shown inline in chat -->

    <v-row no-gutters style="height: calc(100vh - 64px);">
      <!-- Main Chat Area -->
      <v-col cols="12" style="height: 100%; display: flex; flex-direction: column;">
        <!-- Messages Area -->
        <v-sheet 
          class="messages-container flex-grow-1 overflow-y-auto pa-4" 
          color="grey-lighten-4"
          ref="messagesContainer"
        >
          <!-- Welcome Message -->
          <v-fade-transition>
            <div v-if="messages.length === 0" class="welcome-section text-center py-12">
              <img :src="robotIcon" alt="AI Assistant" class="robot-icon-large mb-4" />
              <h2 class="text-h5 mb-2 text-grey-darken-2">Financial AI Assistant</h2>
              <p class="text-body-2 text-grey mb-6">
                Ask me anything about financial planning, investments, and retirement
              </p>
              
              <!-- Quick Start Suggestions -->
              <v-row justify="center">
                <v-col cols="12" md="8">
                  <div class="text-caption text-left mb-2 text-grey">Try asking:</div>
                  <v-chip
                    v-for="(suggestion, idx) in quickSuggestions"
                    :key="idx"
                    class="ma-1"
                    @click="sendSuggestion(suggestion)"
                    variant="outlined"
                    size="small"
                  >
                    {{ suggestion }}
                  </v-chip>
                </v-col>
              </v-row>
            </div>
          </v-fade-transition>

          <!-- Chat Messages -->
          <v-slide-y-transition group>
            <div
              v-for="(message, idx) in messages"
              :key="idx"
              class="message-wrapper mb-6"
              :class="message.role === 'user' ? 'user-message' : 'assistant-message'"
            >
              <div class="d-flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
                <!-- Assistant Icon (custom image) -->
                <img 
                  v-if="message.role === 'assistant'"
                  :src="robotIcon" 
                  alt="AI" 
                  class="robot-icon-small mr-2 mt-1"
                />

                <!-- Message Content -->
                <div
                  :class="message.role === 'user' ? 'user-bubble' : 'assistant-bubble'"
                  class="message-content-wrapper"
                >
                  <div v-html="formatMessage(message.content)" class="message-content"></div>
                  <!-- Only show timestamp for user messages -->
                  <div v-if="message.role === 'user'" class="text-caption mt-1 message-time">
                    {{ formatTime(message.timestamp) }}
                  </div>
                </div>
              </div>
            </div>
          </v-slide-y-transition>

          <!-- Streaming Message (while AI is responding) -->
          <v-slide-y-transition>
            <div v-if="streaming || loading" class="message-wrapper assistant-message mb-6">
              <div class="d-flex justify-start">
                <img 
                  :src="robotIcon" 
                  alt="AI" 
                  class="robot-icon-small mr-2 mt-1"
                />
                <div class="assistant-bubble message-content-wrapper">
                  <!-- Show current response if available -->
                  <div v-if="currentResponse" v-html="formatMessage(currentResponse)" class="message-content"></div>
                  
                  <!-- Show loading status -->
                  <div class="thinking-status">
                    <span class="status-icon">{{ getStatusIcon() }}</span>
                    <span class="status-text">{{ loadingMessage }}</span>
                    <div class="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </v-slide-y-transition>
        </v-sheet>

        <!-- Input Area -->
        <v-sheet elevation="4" class="input-area pa-4" style="flex: 0 0 auto;">
          <v-row no-gutters align="center">
            <v-col>
              <v-textarea
                v-model="userInput"
                placeholder="Type your message here..."
                rows="1"
                auto-grow
                variant="outlined"
                density="comfortable"
                hide-details
                :disabled="streaming || loading"
                @keydown.enter.exact.prevent="sendMessage"
                @keydown.enter.shift.exact="userInput += '\n'"
                class="message-input"
              >
                <template v-slot:append-inner>
                  <v-btn
                    icon
                    color="black"
                    :disabled="!userInput.trim() || streaming || loading"
                    @click="sendMessage"
                    size="small"
                    variant="flat"
                  >
                    <v-icon color="white">mdi-send</v-icon>
                  </v-btn>
                </template>
              </v-textarea>
            </v-col>
          </v-row>
          <div class="text-caption text-grey text-center mt-2">
            Press Enter to send • Shift+Enter for new line
          </div>
        </v-sheet>
      </v-col>
    </v-row>

    <!-- Error Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="5000" location="top">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">Close</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script>
import { supabase } from '../supabase'
import { marked } from 'marked'
import { useRouter } from 'vue-router'
import robotIcon from '@/assets/images/robot-icon.png'

// Configure marked for better table rendering
marked.setOptions({
  gfm: true, // GitHub Flavored Markdown
  breaks: true, // Convert \n to <br>
  tables: true, // Enable tables
  sanitize: false, // Allow HTML (be careful with user input)
  smartLists: true,
  smartypants: true
})

export default {
  name: 'Chatbot',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      robotIcon,
      messages: [],
      userInput: '',
      currentResponse: '',
      streaming: false,
      loading: false,
      loadingMessage: 'Loading...',
      quickSuggestions: [
        'How should I start investing in Malaysia?',
        'What is EPF and how does it work?',
        'Best retirement planning strategies',
        'How to create an emergency fund?',
        'Tax-efficient investment options'
      ],
      snackbar: {
        show: false,
        message: '',
        color: 'error'
      }
    }
  },
  
  mounted() {
    // Load chat history from localStorage
    this.loadChatHistory()
  },
  
  methods: {
    async sendMessage() {
      if (!this.userInput.trim() || this.streaming || this.loading) return
      
      const query = this.userInput.trim()
      
      // Add user message
      const userMessage = {
        role: 'user',
        content: query,
        timestamp: new Date()
      }
      this.messages.push(userMessage)
      
      // Clear input
      this.userInput = ''
      
      // Scroll to bottom
      this.$nextTick(() => {
        this.scrollToBottom()
      })
      
      // Start streaming
      this.currentResponse = ''
      this.streaming = true
      this.loading = true
      this.loadingMessage = 'Thinking...'
      
      console.log('[CHATBOT] Starting to send message:', query)
      
      try {
        const { data: { session } } = await supabase.auth.getSession()
        
        if (!session) {
          throw new Error('Please log in to use the chatbot')
        }
        
        console.log('[CHATBOT] Fetching from API...')
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/query`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query,
            chat_history: this.messages.slice(-10).map(m => ({
              role: m.role,
              content: m.content
            }))
          })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        console.log('[CHATBOT] Response received, starting to stream...')
        this.loading = false
        
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let chunkCount = 0
        
        while (true) {
          const { done, value } = await reader.read()
          if (done) {
            console.log('[CHATBOT] Stream complete. Total chunks:', chunkCount)
            break
          }
          
          // Decode the chunk
          const chunk = decoder.decode(value, { stream: true })
          buffer += chunk
          
          // Process complete lines
          const lines = buffer.split('\n')
          // Keep the last incomplete line in the buffer
          buffer = lines.pop() || ''
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                if (data.done) {
                  if (data.error) {
                    console.error('[CHATBOT] Error from server:', data.error)
                    throw new Error(data.error)
                  }
                  console.log('[CHATBOT] Received done signal')
                  break
                }
                
                if (data.content) {
                  chunkCount++
                  
                  // Update loading message based on content
                  if (data.toolCall) {
                    const toolMessages = {
                      'get_user_financial_profile': 'Analyzing your profile...',
                      'get_investment_options': 'Finding investments...',
                      'compare_investments': 'Comparing options...',
                      'calculate_retirement_projection': 'Calculating projections...',
                      'get_product_details': 'Getting details...',
                      'create_investment_order': 'Creating order...'
                    }
                    this.loadingMessage = toolMessages[data.toolCall] || 'Using tools...'
                  } else if (chunkCount === 1) {
                    this.loadingMessage = 'Generating response...'
                  }
                  
                  if (chunkCount <= 5) {
                    console.log(`[CHATBOT] Chunk ${chunkCount}:`, data.content.substring(0, 50))
                  }
                  this.currentResponse += data.content
                  // Force Vue to update immediately
                  await this.$nextTick()
                  // Auto-scroll while streaming
                  this.scrollToBottom()
                }
              } catch (e) {
                if (!line.slice(6).includes('done')) {
                  console.error('[CHATBOT] Parse error:', e, 'Line:', line)
                }
              }
            }
          }
        }
        
        // Process any remaining buffer
        if (buffer && buffer.startsWith('data: ')) {
          try {
            const data = JSON.parse(buffer.slice(6))
            if (data.content) {
              this.currentResponse += data.content
            }
          } catch (e) {
            console.error('[CHATBOT] Final buffer parse error:', e)
          }
        }
        
        console.log('[CHATBOT] Final response length:', this.currentResponse.length)
        
        // Save complete response
        if (this.currentResponse) {
          const assistantMessage = {
            role: 'assistant',
            content: this.currentResponse,
            timestamp: new Date()
          }
          this.messages.push(assistantMessage)
          this.saveChatHistory()
          console.log('[CHATBOT] Message saved to history')
        }
        
      } catch (error) {
        console.error('[CHATBOT] Streaming error:', error)
        this.showError(error.message || 'Failed to get response from AI')
        
        // Add error message
        this.messages.push({
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date()
        })
      } finally {
        this.streaming = false
        this.loading = false
        this.loadingMessage = 'Loading...'
        this.currentResponse = ''
        this.scrollToBottom()
        console.log('[CHATBOT] Streaming finished')
      }
    },
    
    sendSuggestion(suggestion) {
      this.userInput = suggestion
      this.sendMessage()
    },
    
    clearChat() {
      if (confirm('Are you sure you want to clear the chat history?')) {
        this.messages = []
        localStorage.removeItem('chatbot_history')
      }
    },
    
    formatMessage(content) {
      // Convert markdown to HTML
      try {
        return marked.parse(content || '')
      } catch (e) {
        return content || ''
      }
    },
    
    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    saveChatHistory() {
      try {
        localStorage.setItem('chatbot_history', JSON.stringify(this.messages))
      } catch (e) {
        console.error('Failed to save chat history:', e)
      }
    },
    
    loadChatHistory() {
      try {
        const history = localStorage.getItem('chatbot_history')
        if (history) {
          this.messages = JSON.parse(history)
          this.$nextTick(() => {
            this.scrollToBottom()
          })
        }
      } catch (e) {
        console.error('Failed to load chat history:', e)
      }
    },
    
    showError(message) {
      this.snackbar.message = message
      this.snackbar.color = 'error'
      this.snackbar.show = true
    },

    async handleLogout() {
      try {
        await supabase.auth.signOut()
        // Clear all local data
        localStorage.removeItem('chatbot_history')
        localStorage.removeItem('questionnaire_completed')
        localStorage.removeItem('questionnaire_data')
        // Redirect to landing page
        this.router.push('/')
      } catch (error) {
        console.error('Logout error:', error)
        this.showError('Failed to logout. Please try again.')
      }
    },

    retakeQuestionnaire() {
      // Clear questionnaire data but keep chat history
      localStorage.removeItem('questionnaire_completed')
      localStorage.removeItem('questionnaire_data')
      // Redirect to questionnaire
      this.router.push('/questionnaire')
    },

    getStatusIcon() {
      const icons = {
        'Thinking...': '',
        'Analyzing your profile...': '',
        'Finding investments...': '',
        'Comparing options...': '',
        'Calculating projections...': '',
        'Getting details...': '',
        'Creating order...': '',
        'Using tools...': '',
        'Generating response...': ''
      }
      return icons[this.loadingMessage] || ''
    }
  }
}
</script>

<style scoped>
.chatbot-container {
  background: #f5f5f5;
}

/* Navigation Bar */
.robot-icon-nav {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.messages-container {
  background: #f5f5f5;
  position: relative;
}

/* Robot Icon Styling */
.robot-icon-large {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.robot-icon-small {
  width: 24px;
  height: 24px;
  object-fit: contain;
  flex-shrink: 0;
}

.welcome-section {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-wrapper {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* User Message Bubble */
.user-bubble {
  background: white !important;
  color: #000 !important;
  padding: 12px 16px;
  border-radius: 24px;
  max-width: 70%;
  word-wrap: break-word;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Assistant Message Bubble - No background, no border */
.assistant-bubble {
  max-width: 70%;
  word-wrap: break-word;
  padding: 0;
}

.message-content-wrapper {
  position: relative;
}

.message-content {
  line-height: 1.6;
  color: #000;
}

.message-time {
  color: #999;
  font-size: 0.75em;
  margin-top: 4px;
}

.message-content :deep(p) {
  margin-bottom: 0.5em;
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin-left: 1.5em;
  margin-bottom: 0.5em;
}

.message-content :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.message-content :deep(pre) {
  background: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5em 0;
}

.message-content :deep(strong) {
  font-weight: 600;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.thinking-status {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 16px;
  margin-top: 8px;
  color: #666;
  font-size: 0.95em;
}

.status-icon {
  font-size: 1.2em;
  margin-right: 8px;
}

.status-text {
  font-weight: 500;
  color: #555;
}

.input-area {
  background: white;
  border-top: 1px solid #e0e0e0;
}

.message-input :deep(.v-field) {
  border-radius: 24px !important;
}

.opacity-70 {
  opacity: 0.7;
}

/* Scrollbar styling */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #999;
}

/* Markdown Content Styling */
.message-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.message-content :deep(thead) {
  background: #f5f5f5;
  color: #000;
  border-bottom: 2px solid #e0e0e0;
}

.message-content :deep(th) {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 0.9em;
  color: #000;
  border-bottom: 2px solid #e0e0e0;
}

.message-content :deep(td) {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 0.95em;
}

.message-content :deep(tbody tr) {
  transition: background-color 0.2s;
}

.message-content :deep(tbody tr:hover) {
  background-color: #f5f5f5;
}

.message-content :deep(tbody tr:last-child td) {
  border-bottom: none;
}

/* Alternating row colors */
.message-content :deep(tbody tr:nth-child(even)) {
  background-color: #fafafa;
}

/* Headings */
.message-content :deep(h1) {
  font-size: 1.8em;
  font-weight: 700;
  margin: 1em 0 0.5em 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.3em;
}

.message-content :deep(h2) {
  font-size: 1.5em;
  font-weight: 600;
  margin: 1em 0 0.5em 0;
  color: #444;
}

.message-content :deep(h3) {
  font-size: 1.3em;
  font-weight: 600;
  margin: 0.8em 0 0.4em 0;
  color: #555;
}

.message-content :deep(h4) {
  font-size: 1.1em;
  font-weight: 600;
  margin: 0.6em 0 0.3em 0;
  color: #666;
}

/* Lists */
.message-content :deep(ul),
.message-content :deep(ol) {
  margin: 0.5em 0 0.5em 1.5em;
  padding-left: 0.5em;
}

.message-content :deep(li) {
  margin: 0.3em 0;
  line-height: 1.6;
}

.message-content :deep(ul li) {
  list-style-type: disc;
}

.message-content :deep(ol li) {
  list-style-type: decimal;
}

/* Nested lists */
.message-content :deep(ul ul),
.message-content :deep(ol ul) {
  list-style-type: circle;
  margin-top: 0.2em;
}

.message-content :deep(ul ol),
.message-content :deep(ol ol) {
  list-style-type: lower-alpha;
  margin-top: 0.2em;
}

/* Blockquotes */
.message-content :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding-left: 1em;
  margin: 1em 0;
  color: #666;
  font-style: italic;
  background: #f9f9f9;
  padding: 0.5em 1em;
  border-radius: 4px;
}

/* Horizontal rules */
.message-content :deep(hr) {
  border: none;
  border-top: 2px solid #e0e0e0;
  margin: 1.5em 0;
}

/* Links */
.message-content :deep(a) {
  color: #667eea;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

.message-content :deep(a:hover) {
  border-bottom-color: #667eea;
}

/* Inline elements */
.message-content :deep(em) {
  font-style: italic;
  color: #555;
}

.message-content :deep(del) {
  text-decoration: line-through;
  color: #999;
}

/* Images */
.message-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1em 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Responsive tables */
@media (max-width: 768px) {
  .message-content :deep(table) {
    font-size: 0.85em;
  }
  
  .message-content :deep(th),
  .message-content :deep(td) {
    padding: 8px 12px;
  }
}

</style>
