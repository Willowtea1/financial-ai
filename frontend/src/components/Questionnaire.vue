<template>
  <v-container fluid class="py-8 px-4">
    <!-- Header -->
    <v-row>
      <v-col cols="12" class="text-center mb-6">
        <h2 class="text-h3 font-weight-bold mb-3 text-white">Financial Checkup</h2>
        <p class="text-body-large text-medium-emphasis text-white">
          Select options that best describe your financial situation
        </p>
        <v-chip
          v-if="isFormComplete"
          color="success"
          variant="flat"
          class="mt-2"
          prepend-icon="mdi-check-circle"
        >
          All sections completed
        </v-chip>
      </v-col>
    </v-row>

    <!-- Questionnaire Cards -->
    <v-row class="mb-16">
      <v-col
        v-for="(options, section) in sections"
        :key="section"
        cols="12"
        md="6"
        lg="4"
        class="mb-4"
      >
        <v-card
          class="question-section-card"
          :class="{ 'section-complete': formData[section] }"
          elevation="2"
          rounded="lg"
        >
          <v-card-title class="section-title">
            <v-icon :color="formData[section] ? 'primary' : 'grey'" class="mr-2">
              {{ formData[section] ? 'mdi-check-circle' : 'mdi-circle-outline' }}
            </v-icon>
            {{ sectionLabels[section] }}
          </v-card-title>
          <v-divider class="mx-4"></v-divider>
          <v-card-text class="pa-4">
            <v-btn-toggle
              v-model="formData[section]"
              mandatory
              color="primary"
              variant="outlined"
              class="option-toggle-group"
            >
              <v-btn
                v-for="option in options"
                :key="option"
                :value="option"
                class="option-button"
                rounded="lg"
              >
                {{ option }}
              </v-btn>
            </v-btn-toggle>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Generate Button -->
    <div class="save-section">
      <v-card
        v-if="isFormComplete && !isSaving && !saveSuccess"
        class="info-card mb-4"
        color="rgba(255, 255, 255, 0.1)"
        variant="flat"
      >
        <v-card-text class="text-center text-white">
          <v-icon color="info" size="32" class="mb-2">mdi-information</v-icon>
          <p class="text-body-1 mb-0">
            Your profile will be securely saved and used to provide personalized financial advice
          </p>
        </v-card-text>
      </v-card>

      <v-btn
        size="x-large"
        color="primary"
        :disabled="!isFormComplete || isSaving"
        :loading="isSaving"
        @click="saveProfile"
        class="generate-button floating-btn"
        elevation="8"
        rounded="xl"
      >
        <v-icon start size="28">
          {{ saveSuccess ? 'mdi-check-circle' : 'mdi-content-save' }}
        </v-icon>
        {{ saveSuccess ? 'Saved! Redirecting...' : isSaving ? 'Saving Profile...' : 'Save & Continue to Chat' }}
        <v-tooltip activator="parent" location="top" v-if="!isFormComplete && !isSaving">
          Please complete all sections
        </v-tooltip>
      </v-btn>
    </div>

    <!-- Success Snackbar -->
    <v-snackbar
      v-model="saveSuccess"
      color="success"
      timeout="2000"
      location="top"
    >
      <v-icon start>mdi-check-circle</v-icon>
      Profile saved successfully! Redirecting to chat...
    </v-snackbar>

    <!-- Error Snackbar -->
    <v-snackbar
      v-model="showErrorSnackbar"
      color="error"
      timeout="5000"
      location="top"
    >
      <v-icon start>mdi-alert-circle</v-icon>
      {{ saveError }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="saveError = null"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authenticatedFetch } from '../utils/auth'

const router = useRouter()

const formData = ref({
  aboutYou: null,
  income: null,
  expenses: null,
  debt: null,
  savings: null,
  riskTolerance: null
})

const sectionLabels = {
  aboutYou: 'Occupation',
  income: 'Income (per year, RM)',
  expenses: 'Expenses (per month, RM)',
  debt: 'Debt',
  savings: 'Savings',
  riskTolerance: 'Risk Tolerance'
}

const sections = {
  aboutYou: ['Student', 'Not working', 'Professional', 'Business owner', 'Retired'],
  income: ['0–36,000', '36,001–60,000', '60,001–100,000', '100,000+'],
  expenses: ['0–1,000', '1,001–2,500', '2,501–4,000', '4,000+'],
  debt: ['None', 'Credit card', 'Student loan', 'Car loan', 'Mortgage'],
  savings: ['0', '1k–10k', '10k–50k', '50k+'],
  riskTolerance: ['Low', 'Medium', 'High']
}

const isFormComplete = computed(() =>
  Object.values(formData.value).every((v) => v !== null && v !== undefined)
)

// Loading and status states
const isSaving = ref(false)
const saveError = ref(null)
const saveSuccess = ref(false)

// Computed property for error snackbar visibility
const showErrorSnackbar = computed({
  get: () => !!saveError.value,
  set: (value) => {
    if (!value) saveError.value = null
  }
})

const saveProfile = async () => {
  if (!isFormComplete.value) return
  
  isSaving.value = true
  saveError.value = null
  saveSuccess.value = false
  
  try {
    // Get API base URL from environment
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001'
    
    // Use authenticated fetch utility
    const response = await authenticatedFetch(`${apiBaseUrl}/api/profile`, {
      method: 'POST',
      body: JSON.stringify(formData.value)
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || 'Failed to save profile')
    }
    
    const result = await response.json()
    console.log('Profile saved successfully:', result)
    
    // Save to localStorage as backup
    localStorage.setItem('questionnaire_data', JSON.stringify(formData.value))
    localStorage.setItem('questionnaire_completed', 'true')
    
    // Show success message
    saveSuccess.value = true
    
    // Wait 1.5 seconds to show success message, then redirect
    setTimeout(() => {
      router.push({ name: 'Chatbot' })
    }, 1500)
    
  } catch (error) {
    console.error('Error saving profile:', error)
    saveError.value = error.message || 'Failed to save profile. Please try again.'
    isSaving.value = false
  }
}
</script>

<style scoped>
/* ---------------------- Modern Animated Background ---------------------- */
.v-container {
  position: relative;
  overflow: hidden;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Animated floating circles for modern effect */
.v-container::before {
  content: "";
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
  background: radial-gradient(circle at 20% 30%, rgba(255,255,255,0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 70%, rgba(255,255,255,0.1) 0%, transparent 50%);
  animation: floatBackground 30s linear infinite;
  z-index: 0;
}

@keyframes floatBackground {
  0% { transform: rotate(0deg) translate(0, 0); }
  50% { transform: rotate(180deg) translate(50px, -50px); }
  100% { transform: rotate(360deg) translate(0, 0); }
}

/* ---------------------- Cards & Buttons Stay Above Background ---------------------- */
.question-section-card {
  position: relative;
  z-index: 1;
  min-height: 280px;
  transition: all 0.3s ease;
}

.section-title {
  display: flex;
  align-items: center;
  font-weight: 600;
}

.option-toggle-group {
  display: flex !important;
  flex-direction: column !important;
  overflow: visible !important;
  width: 100%;
  gap: 8px;
}

.option-button {
  width: 100%;
  text-transform: none;
  font-weight: 500;
  justify-content: center;
}

:deep(.option-toggle-group .v-btn--selected) {
  background-color: rgb(var(--v-theme-primary)) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.4);
}

.save-section {
  position: fixed;
  bottom: 24px;
  right: 24px;
  left: 24px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  max-width: 500px;
  margin-left: auto;
}

.info-card {
  width: 100%;
  backdrop-filter: blur(10px);
}

.floating-btn {
  min-width: 280px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: none;
}

.floating-btn:not(.v-btn--disabled):hover {
  transform: scale(1.02);
  box-shadow: 0 8px 16px rgba(var(--v-theme-primary), 0.4) !important;
}

@media (max-width: 600px) {
  .save-section {
    right: 16px;
    left: 16px;
    bottom: 16px;
  }

  .floating-btn {
    min-width: auto;
    width: 100%;
    padding: 0 16px;
    font-size: 0.875rem;
  }
}
</style>
