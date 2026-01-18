<template>
  <div class="landing-page">
    <!-- Animated Background -->
    <div class="animated-bg">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- Navigation Bar -->
    <v-app-bar 
      elevation="0" 
      class="nav-bar"
      :class="{ 'scrolled': scrolled }"
    >
      <v-container class="d-flex align-center">
        <div class="d-flex align-center">
          <v-icon size="32" color="white" class="mr-2">mdi-chart-line</v-icon>
          <span class="nav-logo">Financial GPS</span>
        </div>
        
        <v-spacer></v-spacer>
        
        <v-tabs 
          v-model="activeTab" 
          class="nav-tabs"
          color="white"
          slider-color="white"
        >
          <v-tab value="home">Home</v-tab>
          <v-tab value="features">Features</v-tab>
          <v-tab value="api-docs">API Docs</v-tab>
        </v-tabs>
        
        <v-btn
          class="ml-4 nav-cta-btn"
          variant="flat"
          @click="handleStart"
        >
          Get Started
        </v-btn>
      </v-container>
    </v-app-bar>

    <!-- Main Content -->
    <v-container fluid class="content-wrapper">
      <!-- Home Tab -->
      <div v-show="activeTab === 'home'" class="tab-content">
        <v-row class="hero-section" justify="center" align="center">
          <v-col cols="12" md="10" lg="8" class="text-center">
            <!-- Glass Card -->
            <div class="glass-card" data-aos="fade-up">
              <!-- Logo/Icon -->
              <div class="logo-section mb-6">
                <div class="logo-circle">
                  <v-icon size="48" color="white">mdi-chart-line</v-icon>
                </div>
              </div>

              <!-- Headline -->
              <h1 class="hero-title mb-4" data-aos="fade-up" data-aos-delay="100">
                Your AI-Powered<br />Financial Advisor
              </h1>

              <!-- Subheadline -->
              <p class="hero-subtitle mb-8" data-aos="fade-up" data-aos-delay="200">
                Get personalized financial guidance in minutes.<br />
                Smart planning for your future, powered by AI.
              </p>

              <!-- CTA Button -->
              <div class="d-flex justify-center mb-8">
                <v-btn
                  size="x-large"
                  class="cta-button d-flex align-center justify-center"
                  elevation="0"
                  @click="handleStart"
                  data-aos="fade-up"
                  data-aos-delay="300"
                >
                  <span class="cta-text">Start Your Journey</span>
                  <v-icon class="ml-2">mdi-arrow-right</v-icon>
                </v-btn>
              </div>

              <!-- Trust Indicators -->
              <div class="trust-indicators mt-8" data-aos="fade-up" data-aos-delay="400">
                <div class="trust-item">
                  <v-icon size="20" color="rgba(255,255,255,0.9)">mdi-shield-check</v-icon>
                  <span>Secure & Private</span>
                </div>
                <div class="trust-item">
                  <v-icon size="20" color="rgba(255,255,255,0.9)">mdi-lightning-bolt</v-icon>
                  <span>5-Min Setup</span>
                </div>
                <div class="trust-item">
                  <v-icon size="20" color="rgba(255,255,255,0.9)">mdi-robot</v-icon>
                  <span>AI-Powered</span>
                </div>
              </div>
            </div>
          </v-col>
        </v-row>
      </div>

      <!-- Features Tab -->
      <div v-show="activeTab === 'features'" class="tab-content">
        <v-row class="features-section" justify="center">
          <v-col cols="12" class="text-center mb-8">
            <h2 class="section-title" data-aos="fade-up">Powerful Features</h2>
            <p class="section-subtitle" data-aos="fade-up" data-aos-delay="100">
              Everything you need for smart financial planning
            </p>
          </v-col>
          
          <v-col cols="12" md="10" lg="8">
            <v-row>
              <v-col 
                v-for="(feature, idx) in features" 
                :key="idx"
                cols="12" 
                sm="6" 
                md="4"
                data-aos="fade-up"
                :data-aos-delay="200 + (idx * 100)"
              >
                <div class="feature-card">
                  <div class="feature-icon">
                    <v-icon size="32" color="white">{{ feature.icon }}</v-icon>
                  </div>
                  <h3 class="feature-title">{{ feature.title }}</h3>
                  <p class="feature-description">{{ feature.description }}</p>
                </div>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </div>

      <!-- API Documentation Tab -->
      <div v-show="activeTab === 'api-docs'" class="tab-content api-docs-section">
        <v-row justify="center">
          <v-col cols="12" md="10" lg="10">
            <div class="api-docs-container" data-aos="fade-up">
              <div class="api-header text-center mb-8">
                <v-icon size="64" color="white" class="mb-4">mdi-api</v-icon>
                <h2 class="section-title">Financial GPS API</h2>
                <p class="section-subtitle">
                  Integrate our powerful financial planning APIs into your applications
                </p>
                <v-chip class="mt-4" color="success" variant="flat">
                  <v-icon start>mdi-check-circle</v-icon>
                  RESTful API • JSON • OAuth 2.0
                </v-chip>
              </div>

              <!-- API Categories -->
              <v-row>
                <v-col 
                  v-for="(category, idx) in apiCategories" 
                  :key="idx"
                  cols="12"
                  data-aos="fade-up"
                  :data-aos-delay="100 + (idx * 50)"
                >
                  <div class="api-category-card">
                    <div class="category-header">
                      <v-icon size="32" color="white" class="mr-3">{{ category.icon }}</v-icon>
                      <div>
                        <h3 class="category-title">{{ category.title }}</h3>
                        <p class="category-description">{{ category.description }}</p>
                      </div>
                    </div>

                    <v-expansion-panels class="mt-4" variant="accordion">
                      <v-expansion-panel
                        v-for="(endpoint, endIdx) in category.endpoints"
                        :key="endIdx"
                        class="api-endpoint-panel"
                      >
                        <v-expansion-panel-title>
                          <div class="endpoint-title-content">
                            <v-chip 
                              :color="getMethodColor(endpoint.method)" 
                              size="small" 
                              class="mr-3"
                            >
                              {{ endpoint.method }}
                            </v-chip>
                            <span class="endpoint-path">{{ endpoint.path }}</span>
                          </div>
                        </v-expansion-panel-title>
                        <v-expansion-panel-text>
                          <div class="endpoint-details">
                            <p class="endpoint-description">{{ endpoint.description }}</p>
                            
                            <div v-if="endpoint.auth" class="auth-badge mt-3 mb-3">
                              <v-icon size="16" class="mr-1">mdi-lock</v-icon>
                              Requires Authentication
                            </div>

                            <div v-if="endpoint.params" class="params-section mt-4">
                              <h4 class="params-title">Parameters</h4>
                              <div 
                                v-for="(param, paramIdx) in endpoint.params" 
                                :key="paramIdx"
                                class="param-item"
                              >
                                <code class="param-name">{{ param.name }}</code>
                                <span class="param-type">{{ param.type }}</span>
                                <span v-if="param.required" class="param-required">required</span>
                                <p class="param-description">{{ param.description }}</p>
                              </div>
                            </div>

                            <div v-if="endpoint.example" class="example-section mt-4">
                              <h4 class="example-title">Example Request</h4>
                              <pre class="code-block"><code>{{ endpoint.example }}</code></pre>
                            </div>

                            <div v-if="endpoint.response" class="response-section mt-4">
                              <h4 class="response-title">Example Response</h4>
                              <pre class="code-block"><code>{{ endpoint.response }}</code></pre>
                            </div>
                          </div>
                        </v-expansion-panel-text>
                      </v-expansion-panel>
                    </v-expansion-panels>
                  </div>
                </v-col>
              </v-row>

              <!-- Integration Guide -->
              <div class="integration-guide mt-8" data-aos="fade-up">
                <h3 class="guide-title">Quick Integration Guide</h3>
                <v-row class="mt-4">
                  <v-col cols="12" md="4">
                    <div class="guide-step">
                      <div class="step-number">1</div>
                      <h4>Get API Access</h4>
                      <p>Sign up and obtain your API credentials</p>
                    </div>
                  </v-col>
                  <v-col cols="12" md="4">
                    <div class="guide-step">
                      <div class="step-number">2</div>
                      <h4>Authenticate</h4>
                      <p>Use OAuth 2.0 to get your access token</p>
                    </div>
                  </v-col>
                  <v-col cols="12" md="4">
                    <div class="guide-step">
                      <div class="step-number">3</div>
                      <h4>Make Requests</h4>
                      <p>Start calling our APIs with your token</p>
                    </div>
                  </v-col>
                </v-row>
              </div>
            </div>
          </v-col>
        </v-row>
      </div>
    </v-container>

    <!-- Loading Overlay for Auth -->
    <v-overlay :model-value="loading" class="loading-overlay">
      <v-progress-circular indeterminate size="64" color="white"></v-progress-circular>
      <p class="mt-4 text-white">{{ loadingMessage }}</p>
    </v-overlay>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '../supabase'
import AOS from 'aos'
import 'aos/dist/aos.css'

const router = useRouter()
const loading = ref(false)
const loadingMessage = ref('Loading...')
const activeTab = ref('home')
const scrolled = ref(false)

const features = [
  {
    icon: 'mdi-brain',
    title: 'Smart Analysis',
    description: 'AI analyzes your financial situation and goals'
  },
  {
    icon: 'mdi-chart-timeline-variant',
    title: 'Personalized Plans',
    description: 'Custom strategies tailored to your needs'
  },
  {
    icon: 'mdi-chat',
    title: '24/7 Guidance',
    description: 'Ask questions anytime, get instant answers'
  },
  {
    icon: 'mdi-file-document-multiple',
    title: 'Document Analysis',
    description: 'Upload and analyze your financial documents'
  },
  {
    icon: 'mdi-chart-box',
    title: 'Investment Tools',
    description: 'Compare and manage investment products'
  },
  {
    icon: 'mdi-shield-account',
    title: 'Retirement Planning',
    description: 'Calculate and optimize your retirement savings'
  }
]

const apiCategories = [
  {
    icon: 'mdi-brain',
    title: 'AI Financial Planning',
    description: 'Generate and refine personalized financial plans with AI-powered insights',
    endpoints: [
      {
        method: 'POST',
        path: '/api/generate-plan',
        description: 'Generate a personalized financial plan using AI',
        auth: true,
        params: [
          { name: 'aboutYou', type: 'string', required: false, description: 'Personal information' },
          { name: 'income', type: 'string', required: false, description: 'Monthly income' },
          { name: 'expenses', type: 'string', required: false, description: 'Monthly expenses' },
          { name: 'savings', type: 'string', required: false, description: 'Current savings' },
          { name: 'riskTolerance', type: 'string', required: false, description: 'Risk tolerance' }
        ],
        example: `curl -X POST https://api.financialgps.com/api/generate-plan \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"income": "5000", "expenses": "3000", "savings": "10000"}'`,
        response: `{
  "plan": {
    "summary": "...",
    "recommendations": [...],
    "projections": {...}
  }
}`
      },
      {
        method: 'POST',
        path: '/api/query',
        description: 'Stream AI responses with function calling support',
        auth: true,
        params: [
          { name: 'query', type: 'string', required: true, description: 'User question or query' },
          { name: 'chat_history', type: 'array', required: false, description: 'Previous chat messages' },
          { name: 'context', type: 'object', required: false, description: 'Additional context' }
        ],
        example: `curl -X POST https://api.financialgps.com/api/query \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What should I invest in?"}'`,
        response: `// Server-Sent Events (SSE) stream
data: {"content": "Based on your profile..."}
data: {"content": " I recommend..."}
data: {"done": true}`
      }
    ]
  },
  {
    icon: 'mdi-chart-line',
    title: 'Investment & Retirement Tools',
    description: 'Investment products, comparisons, and retirement projections',
    endpoints: [
      {
        method: 'GET',
        path: '/api/retirement/products',
        description: 'List all available investment products',
        auth: true,
        example: `curl -X GET https://api.financialgps.com/api/retirement/products \\
  -H "Authorization: Bearer YOUR_TOKEN"`,
        response: `{
  "products": [
    {
      "id": "asnb_asb",
      "name": "ASB (Amanah Saham Bumiputera)",
      "type": "Unit Trust",
      "risk_level": "Low",
      "expected_return": 5.5,
      ...
    }
  ],
  "total": 10
}`
      },
      {
        method: 'POST',
        path: '/api/retirement/investment-options',
        description: 'Get personalized investment recommendations',
        auth: true,
        params: [
          { name: 'risk_tolerance', type: 'string', required: true, description: 'low, medium, or high' },
          { name: 'investment_amount', type: 'number', required: true, description: 'Amount to invest' },
          { name: 'time_horizon', type: 'number', required: true, description: 'Years until needed' },
          { name: 'goals', type: 'array', required: false, description: 'Investment goals' }
        ],
        example: `curl -X POST https://api.financialgps.com/api/retirement/investment-options \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "risk_tolerance": "medium",
    "investment_amount": 10000,
    "time_horizon": 10
  }'`,
        response: `{
  "recommendations": [
    {
      "product": {...},
      "allocation_percentage": 40,
      "recommended_amount": 4000,
      "rationale": "..."
    }
  ]
}`
      },
      {
        method: 'POST',
        path: '/api/retirement/projection',
        description: 'Calculate retirement savings projection',
        auth: true,
        params: [
          { name: 'current_age', type: 'number', required: true, description: 'Current age' },
          { name: 'retirement_age', type: 'number', required: true, description: 'Target retirement age' },
          { name: 'current_savings', type: 'number', required: true, description: 'Current savings amount' },
          { name: 'monthly_contribution', type: 'number', required: true, description: 'Monthly contribution' },
          { name: 'expected_return', type: 'number', required: true, description: 'Expected annual return %' }
        ],
        example: `curl -X POST https://api.financialgps.com/api/retirement/projection \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "current_age": 30,
    "retirement_age": 60,
    "current_savings": 50000,
    "monthly_contribution": 1000,
    "expected_return": 6.0
  }'`,
        response: `{
  "years_to_retirement": 30,
  "total_contributions": 360000,
  "projected_value": 1234567.89,
  "real_value_after_inflation": 987654.32,
  "monthly_income_at_retirement": 4115.22
}`
      },
      {
        method: 'POST',
        path: '/api/retirement/order',
        description: 'Create an investment purchase order',
        auth: true,
        params: [
          { name: 'product_id', type: 'string', required: true, description: 'Product ID to purchase' },
          { name: 'amount', type: 'number', required: true, description: 'Investment amount' },
          { name: 'payment_method', type: 'string', required: false, description: 'Payment method' }
        ],
        example: `curl -X POST https://api.financialgps.com/api/retirement/order \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "product_id": "asnb_asb",
    "amount": 5000,
    "payment_method": "online_banking"
  }'`,
        response: `{
  "success": true,
  "order_id": "ORD-20260118-ABC123",
  "status": "pending_payment",
  "payment_url": "https://payment.example.com/..."
}`
      }
    ]
  }
]

onMounted(() => {
  AOS.init({
    duration: 800,
    easing: 'ease-out-cubic',
    once: true
  })

  // Handle scroll for navbar
  window.addEventListener('scroll', () => {
    scrolled.value = window.scrollY > 50
  })
})

const getMethodColor = (method) => {
  const colors = {
    'GET': 'blue',
    'POST': 'green',
    'PUT': 'orange',
    'DELETE': 'red',
    'PATCH': 'purple'
  }
  return colors[method] || 'grey'
}

const handleStart = async () => {
  loading.value = true
  loadingMessage.value = 'Checking authentication...'

  try {
    // Check if user is already logged in
    const { data: { session } } = await supabase.auth.getSession()

    if (session) {
      // User is logged in, check questionnaire status
      const questionnaireCompleted = localStorage.getItem('questionnaire_completed')
      
      if (questionnaireCompleted === 'true') {
        // Go directly to chatbot
        router.push('/chatbot')
      } else {
        // Go to questionnaire
        router.push('/questionnaire')
      }
    } else {
      // User not logged in, trigger social auth
      loadingMessage.value = 'Redirecting to login...'
      
      // Sign in with Google
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/questionnaire`
        }
      })

      if (error) {
        console.error('Auth error:', error)
        alert('Authentication failed. Please try again.')
        loading.value = false
      }
      // If successful, user will be redirected by Supabase
    }
  } catch (error) {
    console.error('Error:', error)
    alert('An error occurred. Please try again.')
    loading.value = false
  }
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Animated Background */
.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 20s infinite ease-in-out;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.8) 0%, transparent 70%);
  top: -10%;
  left: -10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(118, 75, 162, 0.8) 0%, transparent 70%);
  bottom: -10%;
  right: -10%;
  animation-delay: -7s;
}

.orb-3 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 30px) scale(0.9);
  }
}

/* Navigation Bar */
.nav-bar {
  background: rgba(102, 126, 234, 0.8) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  position: fixed !important;
  z-index: 100;
}

.nav-bar.scrolled {
  background: rgba(102, 126, 234, 0.98) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.nav-logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.5px;
}

.nav-tabs {
  background: transparent !important;
}

.nav-tabs :deep(.v-tab) {
  color: rgba(255, 255, 255, 0.8) !important;
  font-weight: 500;
  text-transform: none;
  letter-spacing: 0.3px;
}

.nav-tabs :deep(.v-tab--selected) {
  color: white !important;
}

.nav-cta-btn {
  background: white !important;
  color: #667eea !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  padding: 0 24px !important;
}

/* Content Wrapper */
.content-wrapper {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  padding-top: 80px;
}

.tab-content {
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
  padding: 2rem 1rem;
}

.hero-section {
  min-height: calc(100vh - 80px);
}

/* Glass Card - Glassmorphism */
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 32px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 4rem 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-5px);
}

/* Logo */
.logo-section {
  display: flex;
  justify-content: center;
}

.logo-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

/* Typography */
.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  color: white;
  line-height: 1.2;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.2);
}

.hero-subtitle {
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
}

.section-title {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  color: white;
  margin-bottom: 1rem;
}

.section-subtitle {
  font-size: clamp(1rem, 2vw, 1.2rem);
  color: rgba(255, 255, 255, 0.85);
  max-width: 700px;
  margin: 0 auto;
}

/* CTA Button */
.cta-button {
  background: white !important;
  color: #667eea !important;
  border-radius: 16px !important;
  padding: 1.5rem 3rem !important;
  font-size: 1.1rem !important;
  font-weight: 700 !important;
  text-transform: none !important;
  letter-spacing: 0.5px !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2) !important;
}

.cta-text {
  font-size: 1.1rem;
  display: inline-flex;
  align-items: center;
}

/* Trust Indicators */
.trust-indicators {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.trust-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  font-weight: 500;
}

/* Features Section */
.features-section {
  padding: 4rem 0;
}

.feature-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 2rem 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
  height: 100%;
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-5px);
  border-color: rgba(255, 255, 255, 0.3);
}

.feature-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.75rem;
}

.feature-description {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin: 0;
}

/* API Documentation Section */
.api-docs-section {
  padding: 4rem 0;
}

.api-docs-container {
  background: linear-gradient(135deg, #7c8fd9 0%, #8b6bb0 100%);
  border-radius: 32px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  padding: 3rem 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.api-header {
  margin-bottom: 3rem;
}

.api-category-card {
  background: linear-gradient(135deg, #8b9de0 0%, #9a7dbd 100%);
  border-radius: 20px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.category-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.category-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.category-description {
  font-size: 0.95rem;
  color: white;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.api-endpoint-panel {
  background: linear-gradient(135deg, #9aabe7 0%, #a88ec4 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  margin-bottom: 0.5rem !important;
}

.api-endpoint-panel :deep(.v-expansion-panel-title) {
  color: white !important;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.api-endpoint-panel :deep(.v-expansion-panel-text__wrapper) {
  padding: 1.5rem;
  background: linear-gradient(135deg, #a5b5ed 0%, #b39ccb 100%);
}

.endpoint-title-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.endpoint-path {
  font-family: 'Courier New', monospace;
  font-size: 0.95rem;
  color: white;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.endpoint-details {
  color: white;
}

.endpoint-description {
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1rem;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.auth-badge {
  display: inline-flex;
  align-items: center;
  background: #ffa726;
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid #ff9800;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.params-section,
.example-section,
.response-section {
  margin-top: 1.5rem;
}

.params-title,
.example-title,
.response-title {
  font-size: 1rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.param-item {
  background: linear-gradient(135deg, #b0bff3 0%, #bea8d2 100%);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  border-left: 4px solid #667eea;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.param-name {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: #fff;
  background: #667eea;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  margin-right: 0.5rem;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.param-type {
  font-size: 0.85rem;
  color: #a8ff60;
  margin-right: 0.5rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.param-required {
  font-size: 0.75rem;
  color: #fff;
  background: #f44336;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 700;
  border: 1px solid #d32f2f;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.param-description {
  font-size: 0.9rem;
  color: white;
  margin-top: 0.5rem;
  margin-bottom: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.code-block {
  background: #2d2d2d;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
  color: #f8f8f2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.code-block code {
  color: #f8f8f2;
}

/* Integration Guide */
.integration-guide {
  background: linear-gradient(135deg, #7c8fd9 0%, #8b6bb0 100%);
  border-radius: 20px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  padding: 2rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.guide-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  text-align: center;
  margin-bottom: 2rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.guide-step {
  background: linear-gradient(135deg, #8b9de0 0%, #9a7dbd 100%);
  border-radius: 16px;
  padding: 2rem 1.5rem;
  text-align: center;
  height: 100%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.guide-step:hover {
  background: linear-gradient(135deg, #9aabe7 0%, #a88ec4 100%);
  transform: translateY(-5px);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  border: 2px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.guide-step h4 {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.75rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.guide-step p {
  font-size: 0.95rem;
  color: white;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Loading Overlay */
.loading-overlay {
  background: rgba(102, 126, 234, 0.95) !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* Responsive */
@media (max-width: 960px) {
  .glass-card {
    padding: 3rem 1.5rem;
  }

  .trust-indicators {
    gap: 1rem;
  }

  .nav-tabs {
    display: none;
  }

  .api-docs-container {
    padding: 2rem 1rem;
  }

  .endpoint-title-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

@media (max-width: 600px) {
  .glass-card {
    padding: 2rem 1rem;
    border-radius: 24px;
  }

  .cta-button {
    padding: 1.25rem 2rem !important;
    font-size: 1rem !important;
  }

  .trust-indicators {
    flex-direction: column;
    gap: 0.75rem;
  }

  .nav-cta-btn {
    display: none;
  }

  .api-category-card {
    padding: 1.5rem 1rem;
  }

  .code-block {
    font-size: 0.75rem;
  }
}
</style>
