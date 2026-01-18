<template>
  <div class="landing-page">
    <!-- Animated Background -->
    <div class="animated-bg">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- Main Content -->
    <v-container fluid class="content-wrapper">
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
            <v-btn
              size="x-large"
              class="cta-button"
              elevation="0"
              @click="handleStart"
              data-aos="fade-up"
              data-aos-delay="300"
            >
              <span class="cta-text">Start Your Journey</span>
              <v-icon class="ml-2">mdi-arrow-right</v-icon>
            </v-btn>

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

          <!-- Features Section -->
          <v-row class="features-section mt-12" justify="center">
            <v-col 
              v-for="(feature, idx) in features" 
              :key="idx"
              cols="12" 
              sm="6" 
              md="4"
              data-aos="fade-up"
              :data-aos-delay="500 + (idx * 100)"
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
  }
]

onMounted(() => {
  AOS.init({
    duration: 800,
    easing: 'ease-out-cubic',
    once: true
  })
})

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
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Animated Background */
.animated-bg {
  position: absolute;
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

/* Content Wrapper */
.content-wrapper {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 2rem 1rem;
}

.hero-section {
  min-height: 100vh;
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

/* CTA Button */
.cta-button {
  display: inline-flex !important; /* ensure it's flex */
  align-items: center !important;  /* vertical centering */
  justify-content: center !important; /* horizontal centering */
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
}


.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2) !important;
}

.cta-text {
  font-size: 1.1rem;
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
  margin-top: 4rem;
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

  .features-section {
    margin-top: 3rem;
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
}
</style>
