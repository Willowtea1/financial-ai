<template>
  <v-container fluid class="chatbot-container pa-0" style="height: 100vh;">
    <!-- Top Navigation Bar -->
    <v-app-bar elevation="1" color="white" density="comfortable">
      <v-app-bar-title class="d-flex align-center">
        <img :src="robotIcon" alt="AI" class="robot-icon-nav mr-2" />
        <span class="font-weight-bold">Financial AI Assistant</span>
      </v-app-bar-title>
      
      <v-spacer></v-spacer>
      
      <!-- Summarize Button - Always visible, disabled until messages exist -->
      <v-btn
        variant="tonal"
        color="primary"
        class="mr-2 get-my-plan-btn"
        @click="summarizeConversation"
        :loading="summarizing"
        :disabled="messages.length === 0"
        prepend-icon="mdi-lightbulb-on"
        id="get-my-plan-button"
      >
        Get My Plan
        <v-tooltip 
          activator="parent" 
          location="bottom"
          v-if="messages.length === 0"
        >
          Start chatting to activate this feature
        </v-tooltip>
      </v-btn>
      
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
              :class="[
                message.role === 'user' ? 'user-message' : 'assistant-message',
                message.isSummary ? 'summary-message' : ''
              ]"
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
                  :class="[
                    message.role === 'user' ? 'user-bubble' : 'assistant-bubble',
                    message.isSummary ? 'summary-bubble' : ''
                  ]"
                  class="message-content-wrapper"
                >
                  <div v-html="formatMessage(message.content)" class="message-content"></div>
                  <!-- Only show timestamp for user messages -->
                  <div v-if="message.role === 'user'" class="text-caption mt-1 message-time">
                    {{ formatTime(message.timestamp) }}
                  </div>
                </div>
              </div>
              
              <!-- Action Card (if message has one) -->
              <div v-if="message.actionCard" class="action-card-wrapper mt-3">
                <ActionCard
                  :action="message.actionCard"
                  :loading="message.actionCard.processing"
                  @approve="handleActionApprove(message.actionCard)"
                  @decline="handleActionDecline(message.actionCard, idx)"
                />
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

    <!-- Onboarding Spotlight -->
    <v-fade-transition>
      <div v-if="showOnboarding" class="onboarding-overlay" @click="dismissOnboarding">
        <!-- Dark overlay -->
        <div class="overlay-background"></div>
        
        <!-- Spotlight on Get My Plan button -->
        <div class="spotlight-container">
          <div class="spotlight-circle"></div>
          
          <!-- Tooltip/Guide -->
          <div class="onboarding-tooltip" @click.stop>
            <div class="tooltip-content">
              <v-icon size="48" color="primary" class="mb-3">mdi-lightbulb-on</v-icon>
              <h3 class="text-h6 mb-2">Get Your Personalized Plan</h3>
              <p class="text-body-2 mb-4">
                After chatting about your financial goals, click <strong>"Get My Plan"</strong> 
                to receive an AI-powered recommendation tailored specifically for you.
              </p>
              <p class="text-body-2 text-grey mb-4">
                💡 The button will activate once you start the conversation. No more decision paralysis - we'll analyze everything and tell you exactly what to do.
              </p>
              <v-btn 
                color="primary" 
                variant="flat" 
                block
                @click="dismissOnboarding"
              >
                Got it!
              </v-btn>
            </div>
            <!-- Arrow pointing to button -->
            <div class="tooltip-arrow"></div>
          </div>
        </div>
      </div>
    </v-fade-transition>
  </v-container>
</template>

<script>
import { supabase } from '../supabase'
import { marked } from 'marked'
import { useRouter } from 'vue-router'
import robotIcon from '@/assets/images/robot-icon.png'
import ActionCard from '../components/ActionCard.vue'

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
  components: {
    ActionCard
  },
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
      currentActionCard: null,
      streaming: false,
      loading: false,
      loadingMessage: 'Loading...',
      summarizing: false,
      showOnboarding: false,
      quickSuggestions: [
        'I want to invest RM 5,000',
        'How can I save on taxes?',
        'I need life insurance',
        'Help me save for a car',
        'Calculate my retirement projection'
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
    
    // Check if user has seen onboarding
    this.checkOnboarding()
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
      this.currentActionCard = null
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
                
                // Check for action card
                if (data.action_card) {
                  console.log('[CHATBOT] Action card received:', data.action_card.type)
                  this.currentActionCard = {
                    id: Date.now(),
                    ...data.action_card,
                    status: 'pending',
                    processing: false
                  }
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
                      'create_investment_order': 'Creating order...',
                      'create_epf_topup_action': 'Preparing EPF top-up...',
                      'create_insurance_recommendation': 'Finding insurance...',
                      'create_savings_goal_action': 'Setting up goal...'
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
            if (data.action_card) {
              this.currentActionCard = {
                id: Date.now(),
                ...data.action_card,
                status: 'pending',
                processing: false
              }
            }
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
            timestamp: new Date(),
            actionCard: this.currentActionCard
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
        this.currentActionCard = null
        this.scrollToBottom()
        console.log('[CHATBOT] Streaming finished')
      }
    },
    
    async handleActionApprove(action) {
      console.log('[CHATBOT] Approving action:', action.type)
      action.processing = true
      
      try {
        const { data: { session } } = await supabase.auth.getSession()
        
        if (!session) {
          throw new Error('Please log in to execute actions')
        }
        
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/execute-action`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            action_id: String(action.id),  // Convert to string
            action_type: action.type,
            data: action.data
          })
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail?.message || 'Failed to execute action')
        }
        
        const result = await response.json()
        console.log('[CHATBOT] Action executed:', result)
        
        // Update action status
        action.status = 'completed'
        action.processing = false
        
        // Special handling for EPF top-up - open payment gateway
        if (action.type === 'epf_topup') {
          const paymentUrl = `/payment-gateway?txn_id=${result.result.action_id}&amount=${action.data.amount}&tax_relief=${action.data.taxRelief}`
          window.open(paymentUrl, '_blank', 'width=800,height=900')
          
          // Show message that payment window opened
          this.snackbar.message = 'Payment gateway opened in new tab. Please complete your payment.'
          this.snackbar.color = 'info'
          this.snackbar.show = true
        } else {
          // Show success message for other action types
          this.snackbar.message = result.result?.message || 'Action completed successfully!'
          this.snackbar.color = 'success'
          this.snackbar.show = true
        }
        
        // Add confirmation message to chat
        let confirmationContent = `✅ **Action Completed!**\n\n${result.result?.message || 'Your action has been executed successfully.'}`
        
        if (action.type === 'epf_topup') {
          confirmationContent += '\n\n*Payment gateway has been opened in a new tab. Please complete your payment to finalize the transaction.*'
        }
        
        const confirmationMessage = {
          role: 'assistant',
          content: confirmationContent,
          timestamp: new Date()
        }
        this.messages.push(confirmationMessage)
        this.saveChatHistory()
        
        this.$nextTick(() => {
          this.scrollToBottom()
        })
        
      } catch (error) {
        console.error('[CHATBOT] Action execution error:', error)
        action.processing = false
        this.showError(error.message || 'Failed to execute action')
      }
    },
    
    handleActionDecline(action, messageIndex) {
      console.log('[CHATBOT] Declining action:', action.type)
      
      // Remove action card from message
      if (this.messages[messageIndex]) {
        this.messages[messageIndex].actionCard = null
      }
      
      // Add decline message to chat
      const declineMessage = {
        role: 'assistant',
        content: 'No problem! Let me know if you change your mind or need help with something else.',
        timestamp: new Date()
      }
      this.messages.push(declineMessage)
      this.saveChatHistory()
      
      this.$nextTick(() => {
        this.scrollToBottom()
      })
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
    },

    checkOnboarding() {
      // Check if user has seen the onboarding
      const hasSeenOnboarding = localStorage.getItem('chatbot_onboarding_seen')
      
      if (!hasSeenOnboarding) {
        // Show onboarding after a short delay
        setTimeout(() => {
          this.showOnboarding = true
        }, 500)
      }
    },

    dismissOnboarding() {
      this.showOnboarding = false
      // Mark onboarding as seen
      localStorage.setItem('chatbot_onboarding_seen', 'true')
    },

    async summarizeConversation() {
      if (this.messages.length === 0) return
      
      this.summarizing = true
      console.log('[CHATBOT] Starting conversation summary with final recommendation...')
      
      try {
        const { data: { session } } = await supabase.auth.getSession()
        
        if (!session) {
          throw new Error('Please log in to use this feature')
        }
        
        // Create a summary request
        const conversationText = this.messages
          .map(m => `${m.role.toUpperCase()}: ${m.content}`)
          .join('\n\n')
        
        const summaryPrompt = `You are a decisive financial advisor. Based on our entire conversation, provide a FINAL RECOMMENDATION that eliminates decision paralysis.

**Your task:**
1. **Analyze** the user's profile, goals, and all options discussed
2. **Make THE decision** for them - choose the single best option or allocation
3. **Present it confidently** as "Here's what you should do"
4. **Show comparison table** of all options discussed (for transparency)
5. **Explain why** your recommendation is optimal for their specific situation
6. **Provide the exact action** they need to take (with specific amounts/products)

**Format:**
# 🎯 Your Personalized Financial Plan

## My Recommendation
[State your confident recommendation clearly - "Based on your profile, here's what you should do:"]

## The Plan
[Specific allocation/product with exact amounts]
- Product 1: RM X,XXX (XX%)
- Product 2: RM X,XXX (XX%)
- Total: RM X,XXX

## Why This Works For You
[3-4 bullet points explaining why this is optimal for their specific situation]

## All Options Considered
[Comparison table showing all options discussed]

## Next Step
If you're ready to proceed with this plan, just say "Let's do it" and I'll help you execute it immediately.

**Important:** 
- Be DECISIVE - don't say "you could consider" or "options include"
- Say "Here's what you should do" or "I recommend you invest"
- Make ONE clear recommendation, not multiple options
- Use their actual numbers and profile data
- End with a clear call to action

Conversation:
${conversationText}`

        // Add a temporary "summarizing" message
        const tempMessage = {
          role: 'assistant',
          content: '🎯 **Analyzing your situation and preparing your personalized plan...**',
          timestamp: new Date()
        }
        this.messages.push(tempMessage)
        this.scrollToBottom()
        
        // Call the query endpoint with the summary prompt
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/query`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query: summaryPrompt,
            chat_history: []  // Don't include history for summary
          })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        // Remove the temp message
        this.messages.pop()
        
        // Stream the summary response
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let summaryContent = ''
        
        // Create the summary message
        const summaryMessage = {
          role: 'assistant',
          content: summaryContent,
          timestamp: new Date(),
          isSummary: true
        }
        this.messages.push(summaryMessage)
        const summaryIndex = this.messages.length - 1
        
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          const chunk = decoder.decode(value, { stream: true })
          buffer += chunk
          
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                if (data.done) {
                  if (data.error) {
                    throw new Error(data.error)
                  }
                  break
                }
                
                if (data.content) {
                  summaryContent += data.content
                  this.messages[summaryIndex].content = summaryContent
                  await this.$nextTick()
                  this.scrollToBottom()
                }
              } catch (e) {
                if (!line.slice(6).includes('done')) {
                  console.error('[CHATBOT] Parse error:', e)
                }
              }
            }
          }
        }
        
        // Process remaining buffer
        if (buffer && buffer.startsWith('data: ')) {
          try {
            const data = JSON.parse(buffer.slice(6))
            if (data.content) {
              summaryContent += data.content
              this.messages[summaryIndex].content = summaryContent
            }
          } catch (e) {
            console.error('[CHATBOT] Final buffer parse error:', e)
          }
        }
        
        this.saveChatHistory()
        this.scrollToBottom()
        
        console.log('[CHATBOT] Summary with final recommendation complete')
        
        // Show success message
        this.snackbar.message = '✅ Your personalized plan is ready!'
        this.snackbar.color = 'success'
        this.snackbar.show = true
        
      } catch (error) {
        console.error('[CHATBOT] Summary error:', error)
        this.showError(error.message || 'Failed to generate summary')
        
        // Remove the temp message if it exists
        if (this.messages[this.messages.length - 1]?.content?.includes('Analyzing your situation')) {
          this.messages.pop()
        }
      } finally {
        this.summarizing = false
      }
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

.action-card-wrapper {
  max-width: 70%;
  margin-left: 32px; /* Align with assistant messages (icon width + margin) */
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

/* Summary Message Styling */
.summary-message {
  margin: 2em 0 !important;
}

.summary-bubble {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
  border-radius: 16px !important;
  padding: 24px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
  border: 2px solid #667eea !important;
  max-width: 85% !important;
}

.summary-bubble .message-content {
  color: #2c3e50 !important;
}

.summary-bubble .message-content :deep(h1) {
  color: #667eea !important;
  font-size: 1.6em !important;
  margin-top: 0 !important;
  border-bottom: 2px solid #667eea !important;
}

.summary-bubble .message-content :deep(h2) {
  color: #5568d3 !important;
  font-size: 1.3em !important;
  margin-top: 1.5em !important;
}

.summary-bubble .message-content :deep(h3) {
  color: #4a5fc1 !important;
}

.summary-bubble .message-content :deep(strong) {
  color: #667eea !important;
  font-weight: 700 !important;
}

.summary-bubble .message-content :deep(table) {
  background: white !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
  border: 1px solid #667eea !important;
}

.summary-bubble .message-content :deep(thead) {
  background: #667eea !important;
  color: white !important;
}

.summary-bubble .message-content :deep(th) {
  color: white !important;
  border-bottom: 2px solid #5568d3 !important;
}

.summary-bubble .message-content :deep(tbody tr:hover) {
  background-color: #f0f3ff !important;
}

.summary-bubble .message-content :deep(ul) {
  background: rgba(255, 255, 255, 0.5);
  padding: 1em 1em 1em 2.5em;
  border-radius: 8px;
  margin: 0.5em 0;
}

.summary-bubble .message-content :deep(li) {
  margin: 0.5em 0;
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
  
  .summary-bubble {
    max-width: 95% !important;
    padding: 16px !important;
  }
}

/* Onboarding Overlay */
.onboarding-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1000;
  pointer-events: all;
}

.overlay-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.65);
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.spotlight-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.spotlight-circle {
  position: absolute;
  top: 8px;
  right: 80px;
  width: 180px;
  height: 48px;
  border-radius: 24px;
  background: transparent;
  box-shadow: 
    0 0 0 9999px rgba(0, 0, 0, 0.65),
    0 0 40px 10px rgba(102, 126, 234, 0.6),
    inset 0 0 20px rgba(102, 126, 234, 0.3);
  animation: pulse 2s ease-in-out infinite;
  pointer-events: none;
  z-index: 1001;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 
      0 0 0 9999px rgba(0, 0, 0, 0.65),
      0 0 40px 10px rgba(102, 126, 234, 0.6),
      inset 0 0 20px rgba(102, 126, 234, 0.3);
  }
  50% {
    box-shadow: 
      0 0 0 9999px rgba(0, 0, 0, 0.65),
      0 0 60px 20px rgba(102, 126, 234, 0.8),
      inset 0 0 30px rgba(102, 126, 234, 0.5);
  }
}

.onboarding-tooltip {
  position: absolute;
  top: 80px;
  right: 20px;
  width: 360px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: slideDown 0.4s ease-out 0.2s both;
  z-index: 1002;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tooltip-content {
  padding: 24px;
  text-align: center;
}

.tooltip-content h3 {
  color: #333;
  font-weight: 700;
}

.tooltip-content p {
  color: #666;
  line-height: 1.6;
}

.tooltip-content strong {
  color: #667eea;
  font-weight: 600;
}

.tooltip-arrow {
  position: absolute;
  top: -10px;
  right: 80px;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-bottom: 10px solid white;
}

/* Highlight the Get My Plan button during onboarding */
.get-my-plan-btn {
  position: relative;
  z-index: 1003 !important;
  transition: all 0.3s ease;
}

/* Disabled state styling */
.get-my-plan-btn:disabled {
  opacity: 0.5;
}

/* Animation when button becomes enabled */
@keyframes buttonActivate {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.get-my-plan-btn:not(:disabled) {
  animation: buttonActivate 0.6s ease-out;
}

/* Ensure app bar is above overlay but below spotlight */
.v-app-bar {
  z-index: 1001 !important;
}

/* Mobile responsive onboarding */
@media (max-width: 768px) {
  .spotlight-circle {
    top: 8px;
    right: 60px;
    width: 140px;
    height: 40px;
  }
  
  .onboarding-tooltip {
    top: 70px;
    right: 10px;
    left: 10px;
    width: auto;
    max-width: 360px;
  }
  
  .tooltip-arrow {
    right: 60px;
  }
  
  .tooltip-content {
    padding: 20px;
  }
}

@media (max-width: 600px) {
  .spotlight-circle {
    display: none; /* Hide spotlight on very small screens */
  }
  
  .onboarding-tooltip {
    top: 60px;
    right: 10px;
    left: 10px;
  }
  
  .tooltip-arrow {
    display: none;
  }
}
</style>
