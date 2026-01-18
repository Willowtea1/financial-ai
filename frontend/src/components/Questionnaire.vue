<template>
  <v-container fluid class="py-8 px-4">
    <!-- Header -->
    <v-row>
      <v-col cols="12" class="text-center mb-6">
        <h2 class="text-h3 font-weight-bold mb-3 text-white">Financial Checkup</h2>
        <p class="text-body-large text-medium-emphasis text-white">
          Select options that best describe your financial situation
        </p>
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
    <v-btn
      size="x-large"
      color="primary"
      :disabled="!isFormComplete"
      @click="generatePlan"
      class="generate-button floating-btn"
      elevation="8"
      rounded="xl"
    >
      <v-icon start size="28">mdi-rocket-launch</v-icon>
      Generate My Financial Plan
      <v-tooltip activator="parent" location="top" v-if="!isFormComplete">
        Please complete all sections
      </v-tooltip>
    </v-btn>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

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

const generatePlan = async () => {
  if (!isFormComplete.value) return
  
  // Save questionnaire data to localStorage
  localStorage.setItem('questionnaire_data', JSON.stringify(formData.value))
  
  // Mark questionnaire as completed
  localStorage.setItem('questionnaire_completed', 'true')
  
  // Redirect to chatbot
  router.push({ name: 'Chatbot' })
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

.floating-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1;
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
  .floating-btn {
    min-width: auto;
    padding: 0 16px;
    font-size: 0.875rem;
    right: 16px;
    bottom: 16px;
  }
}
</style>
