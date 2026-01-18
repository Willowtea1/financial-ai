<template>
  <v-container fluid class="questionnaire-page pa-0">
    <!-- Header -->
    <v-app-bar elevation="0" color="primary" dark>
      <v-app-bar-title class="text-h5 font-weight-bold">
        Financial Profile Setup
      </v-app-bar-title>
      <v-spacer></v-spacer>
      <v-chip color="white" text-color="primary" variant="flat">
        Step {{ currentStep }} of {{ totalSteps }}
      </v-chip>
    </v-app-bar>

    <v-main>
      <v-container class="py-8">
        <!-- Progress Stepper -->
        <v-row justify="center" class="mb-8">
          <v-col cols="12" md="10" lg="8">
            <v-stepper
              v-model="currentStep"
              alt-labels
              elevation="0"
              class="custom-stepper"
            >
              <v-stepper-header>
                <v-stepper-item
                  :complete="currentStep > 1"
                  :value="1"
                  title="Basic Info"
                  icon="mdi-account"
                ></v-stepper-item>

                <v-divider></v-divider>

                <v-stepper-item
                  :complete="currentStep > 2"
                  :value="2"
                  title="Financial Details"
                  icon="mdi-cash"
                ></v-stepper-item>

                <v-divider></v-divider>

                <v-stepper-item
                  :complete="currentStep > 3"
                  :value="3"
                  title="Documents"
                  icon="mdi-file-upload"
                ></v-stepper-item>

                <v-divider></v-divider>

                <v-stepper-item
                  :complete="currentStep > 4"
                  :value="4"
                  title="Review"
                  icon="mdi-check-circle"
                ></v-stepper-item>
              </v-stepper-header>

              <v-stepper-window>
                <!-- Step 1: Basic Info -->
                <v-stepper-window-item :value="1">
                  <v-card flat class="pa-6">
                    <h2 class="text-h5 mb-6">Tell us about yourself</h2>
                    
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-card outlined class="question-card" :class="{ 'selected': formData.aboutYou }">
                          <v-card-title class="text-subtitle-1 font-weight-bold">
                            <v-icon :color="formData.aboutYou ? 'primary' : 'grey'" class="mr-2">
                              {{ formData.aboutYou ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                            </v-icon>
                            Occupation
                          </v-card-title>
                          <v-card-text>
                            <v-radio-group v-model="formData.aboutYou" hide-details>
                              <v-radio
                                v-for="option in sections.aboutYou"
                                :key="option"
                                :label="option"
                                :value="option"
                                color="primary"
                              ></v-radio>
                            </v-radio-group>
                          </v-card-text>
                        </v-card>
                      </v-col>

                      <v-col cols="12" md="6">
                        <v-card outlined class="question-card" :class="{ 'selected': formData.riskTolerance }">
                          <v-card-title class="text-subtitle-1 font-weight-bold">
                            <v-icon :color="formData.riskTolerance ? 'primary' : 'grey'" class="mr-2">
                              {{ formData.riskTolerance ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                            </v-icon>
                            Risk Tolerance
                          </v-card-title>
                          <v-card-text>
                            <v-radio-group v-model="formData.riskTolerance" hide-details>
                              <v-radio
                                v-for="option in sections.riskTolerance"
                                :key="option"
                                :label="option"
                                :value="option"
                                color="primary"
                              ></v-radio>
                            </v-radio-group>
                          </v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                  </v-card>
                </v-stepper-window-item>

                <!-- Step 2: Financial Details -->
                <v-stepper-window-item :value="2">
                  <v-card flat class="pa-6">
                    <h2 class="text-h5 mb-6">Your financial situation</h2>
                    
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-card outlined class="question-card" :class="{ 'selected': formData.income }">
                          <v-card-title class="text-subtitle-1 font-weight-bold">
                            <v-icon :color="formData.income ? 'primary' : 'grey'" class="mr-2">
                              {{ formData.income ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                            </v-icon>
                            Annual Income (RM)
                          </v-card-title>
                          <v-card-text>
                            <v-radio-group v-model="formData.income" hide-details>
                              <v-radio
                                v-for="option in sections.income"
                                :key="option"
                                :label="option"
                                :value="option"
                                color="primary"
                              ></v-radio>
                            </v-radio-group>
                          </v-card-text>
                        </v-card>
                      </v-col>

                      <v-col cols="12" md="6">
                        <v-card outlined class="question-card" :class="{ 'selected': formData.expenses }">
                          <v-card-title class="text-subtitle-1 font-weight-bold">
                            <v-icon :color="formData.expenses ? 'primary' : 'grey'" class="mr-2">
                              {{ formData.expenses ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                            </v-icon>
                            Monthly Expenses (RM)
                          </v-card-title>
                          <v-card-text>
                            <v-radio-group v-model="formData.expenses" hide-details>
                              <v-radio
                                v-for="option in sections.expenses"
                                :key="option"
                                :label="option"
                                :value="option"
                                color="primary"
                              ></v-radio>
                            </v-radio-group>
                          </v-card-text>
                        </v-card>
                      </v-col>

                      <v-col cols="12" md="6">
                        <v-card outlined class="question-card" :class="{ 'selected': formData.debt }">
                          <v-card-title class="text-subtitle-1 font-weight-bold">
                            <v-icon :color="formData.debt ? 'primary' : 'grey'" class="mr-2">
                              {{ formData.debt ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                            </v-icon>
                            Debt Type
                          </v-card-title>
                          <v-card-text>
                            <v-radio-group v-model="formData.debt" hide-details>
                              <v-radio
                                v-for="option in sections.debt"
                                :key="option"
                                :label="option"
                                :value="option"
                                color="primary"
                              ></v-radio>
                            </v-radio-group>
                          </v-card-text>
                        </v-card>
                      </v-col>

                      <v-col cols="12" md="6">
                        <v-card outlined class="question-card" :class="{ 'selected': formData.savings }">
                          <v-card-title class="text-subtitle-1 font-weight-bold">
                            <v-icon :color="formData.savings ? 'primary' : 'grey'" class="mr-2">
                              {{ formData.savings ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                            </v-icon>
                            Current Savings (RM)
                          </v-card-title>
                          <v-card-text>
                            <v-radio-group v-model="formData.savings" hide-details>
                              <v-radio
                                v-for="option in sections.savings"
                                :key="option"
                                :label="option"
                                :value="option"
                                color="primary"
                              ></v-radio>
                            </v-radio-group>
                          </v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                  </v-card>
                </v-stepper-window-item>

                <!-- Step 3: Document Upload -->
                <v-stepper-window-item :value="3">
                  <v-card flat class="pa-6">
                    <h2 class="text-h5 mb-2">Upload Financial Documents (Optional)</h2>
                    <p class="text-body-2 text-grey-darken-1 mb-6">
                      Upload your payslips, bank statements, or expense reports for more personalized advice
                    </p>
                    
                    <v-card outlined class="upload-zone pa-8 text-center" @click="triggerFileInput">
                      <input
                        ref="fileInput"
                        type="file"
                        multiple
                        accept=".pdf,.jpg,.jpeg,.png"
                        @change="handleFileSelect"
                        style="display: none"
                      />
                      
                      <v-icon size="64" color="primary" class="mb-4">mdi-cloud-upload</v-icon>
                      <h3 class="text-h6 mb-2">Drag & drop files here</h3>
                      <p class="text-body-2 text-grey mb-4">or click to browse</p>
                      <v-chip size="small" variant="outlined">PDF, JPG, PNG (Max 10MB each)</v-chip>
                    </v-card>

                    <!-- Uploaded Files List -->
                    <v-list v-if="uploadedFiles.length > 0" class="mt-4">
                      <v-list-subheader>Uploaded Documents ({{ uploadedFiles.length }})</v-list-subheader>
                      <v-list-item
                        v-for="(file, index) in uploadedFiles"
                        :key="index"
                        class="file-item"
                      >
                        <template v-slot:prepend>
                          <v-icon :color="getFileIcon(file.name).color">
                            {{ getFileIcon(file.name).icon }}
                          </v-icon>
                        </template>
                        <v-list-item-title>{{ file.name }}</v-list-item-title>
                        <v-list-item-subtitle>{{ formatFileSize(file.size) }}</v-list-item-subtitle>
                        <template v-slot:append>
                          <v-btn
                            icon="mdi-delete"
                            size="small"
                            variant="text"
                            color="error"
                            @click="removeFile(index)"
                          ></v-btn>
                        </template>
                      </v-list-item>
                    </v-list>

                    <v-alert v-if="uploadError" type="error" class="mt-4" closable @click:close="uploadError = null">
                      {{ uploadError }}
                    </v-alert>
                  </v-card>
                </v-stepper-window-item>

                <!-- Step 4: Review -->
                <v-stepper-window-item :value="4">
                  <v-card flat class="pa-6">
                    <h2 class="text-h5 mb-6">Review Your Information</h2>
                    
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-card outlined class="pa-4 mb-4">
                          <h3 class="text-subtitle-1 font-weight-bold mb-3">Basic Information</h3>
                          <v-list density="compact">
                            <v-list-item>
                              <v-list-item-title class="text-caption text-grey">Occupation</v-list-item-title>
                              <v-list-item-subtitle class="text-body-2">{{ formData.aboutYou || 'Not specified' }}</v-list-item-subtitle>
                            </v-list-item>
                            <v-list-item>
                              <v-list-item-title class="text-caption text-grey">Risk Tolerance</v-list-item-title>
                              <v-list-item-subtitle class="text-body-2">{{ formData.riskTolerance || 'Not specified' }}</v-list-item-subtitle>
                            </v-list-item>
                          </v-list>
                        </v-card>
                      </v-col>

                      <v-col cols="12" md="6">
                        <v-card outlined class="pa-4 mb-4">
                          <h3 class="text-subtitle-1 font-weight-bold mb-3">Financial Details</h3>
                          <v-list density="compact">
                            <v-list-item>
                              <v-list-item-title class="text-caption text-grey">Annual Income</v-list-item-title>
                              <v-list-item-subtitle class="text-body-2">RM {{ formData.income || 'Not specified' }}</v-list-item-subtitle>
                            </v-list-item>
                            <v-list-item>
                              <v-list-item-title class="text-caption text-grey">Monthly Expenses</v-list-item-title>
                              <v-list-item-subtitle class="text-body-2">RM {{ formData.expenses || 'Not specified' }}</v-list-item-subtitle>
                            </v-list-item>
                            <v-list-item>
                              <v-list-item-title class="text-caption text-grey">Debt</v-list-item-title>
                              <v-list-item-subtitle class="text-body-2">{{ formData.debt || 'Not specified' }}</v-list-item-subtitle>
                            </v-list-item>
                            <v-list-item>
                              <v-list-item-title class="text-caption text-grey">Savings</v-list-item-title>
                              <v-list-item-subtitle class="text-body-2">RM {{ formData.savings || 'Not specified' }}</v-list-item-subtitle>
                            </v-list-item>
                          </v-list>
                        </v-card>
                      </v-col>

                      <v-col cols="12">
                        <v-card outlined class="pa-4">
                          <h3 class="text-subtitle-1 font-weight-bold mb-3">Documents</h3>
                          <p v-if="uploadedFiles.length === 0" class="text-body-2 text-grey">No documents uploaded</p>
                          <v-chip-group v-else>
                            <v-chip v-for="(file, index) in uploadedFiles" :key="index" size="small">
                              <v-icon start size="small">{{ getFileIcon(file.name).icon }}</v-icon>
                              {{ file.name }}
                            </v-chip>
                          </v-chip-group>
                        </v-card>
                      </v-col>
                    </v-row>

                    <v-alert type="info" variant="tonal" class="mt-6">
                      <v-alert-title>Ready to get started?</v-alert-title>
                      Your information will be securely saved and used to provide personalized financial advice.
                    </v-alert>
                  </v-card>
                </v-stepper-window-item>
              </v-stepper-window>

              <!-- Navigation Buttons -->
              <v-card-actions class="pa-6">
                <v-btn
                  v-if="currentStep > 1"
                  variant="outlined"
                  @click="previousStep"
                  prepend-icon="mdi-chevron-left"
                >
                  Back
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn
                  v-if="currentStep < totalSteps"
                  color="primary"
                  @click="nextStep"
                  append-icon="mdi-chevron-right"
                  :disabled="!isCurrentStepValid"
                >
                  Next
                </v-btn>
                <v-btn
                  v-else
                  color="primary"
                  size="large"
                  :loading="isSaving"
                  :disabled="!isFormComplete || isSaving"
                  @click="saveProfile"
                  prepend-icon="mdi-content-save"
                >
                  {{ saveSuccess ? 'Saved! Redirecting...' : 'Save & Continue to Chat' }}
                </v-btn>
              </v-card-actions>
            </v-stepper>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

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

const currentStep = ref(1)
const totalSteps = 4

const formData = ref({
  aboutYou: null,
  income: null,
  expenses: null,
  debt: null,
  savings: null,
  riskTolerance: null
})

const sections = {
  aboutYou: ['Student', 'Not working', 'Professional', 'Business owner', 'Retired'],
  income: ['0–36,000', '36,001–60,000', '60,001–100,000', '100,000+'],
  expenses: ['0–1,000', '1,001–2,500', '2,501–4,000', '4,000+'],
  debt: ['None', 'Credit card', 'Student loan', 'Car loan', 'Mortgage'],
  savings: ['0', '1k–10k', '10k–50k', '50k+'],
  riskTolerance: ['Low', 'Medium', 'High']
}

// File upload
const fileInput = ref(null)
const uploadedFiles = ref([])
const uploadError = ref(null)

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

const isFormComplete = computed(() =>
  Object.values(formData.value).every((v) => v !== null && v !== undefined)
)

const isCurrentStepValid = computed(() => {
  switch (currentStep.value) {
    case 1:
      return formData.value.aboutYou && formData.value.riskTolerance
    case 2:
      return formData.value.income && formData.value.expenses && 
             formData.value.debt && formData.value.savings
    case 3:
      return true // Documents are optional
    case 4:
      return isFormComplete.value
    default:
      return false
  }
})

const nextStep = () => {
  if (currentStep.value < totalSteps && isCurrentStepValid.value) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  const maxSize = 10 * 1024 * 1024 // 10MB
  
  for (const file of files) {
    if (file.size > maxSize) {
      uploadError.value = `File ${file.name} exceeds 10MB limit`
      continue
    }
    
    if (!uploadedFiles.value.find(f => f.name === file.name)) {
      uploadedFiles.value.push(file)
    }
  }
  
  // Reset input
  event.target.value = ''
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
}

const getFileIcon = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  if (ext === 'pdf') return { icon: 'mdi-file-pdf-box', color: 'error' }
  if (['jpg', 'jpeg', 'png'].includes(ext)) return { icon: 'mdi-file-image', color: 'info' }
  return { icon: 'mdi-file', color: 'grey' }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const saveProfile = async () => {
  if (!isFormComplete.value) return
  
  isSaving.value = true
  saveError.value = null
  saveSuccess.value = false
  
  try {
    // Get API base URL from environment
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001'
    
    // Save profile data
    const response = await authenticatedFetch(`${apiBaseUrl}/api/profile`, {
      method: 'POST',
      body: JSON.stringify(formData.value)
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || 'Failed to save profile')
    }
    
    console.log('Profile saved successfully')
    
    // Upload documents if any
    if (uploadedFiles.value.length > 0) {
      const formDataUpload = new FormData()
      uploadedFiles.value.forEach(file => {
        formDataUpload.append('files', file)
      })
      
      try {
        const token = localStorage.getItem('supabase_token')
        const uploadResponse = await fetch(`${apiBaseUrl}/api/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formDataUpload
        })
        
        if (uploadResponse.ok) {
          console.log('Documents uploaded successfully')
        }
      } catch (uploadErr) {
        console.error('Document upload failed:', uploadErr)
        // Continue anyway - documents are optional
      }
    }
    
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
.questionnaire-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.custom-stepper {
  background: transparent !important;
}

.question-card {
  transition: all 0.3s ease;
  border: 2px solid #e0e0e0;
}

.question-card.selected {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.05);
}

.question-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.upload-zone {
  border: 2px dashed #ccc;
  transition: all 0.3s ease;
  cursor: pointer;
  background: #fafafa;
}

.upload-zone:hover {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.05);
}

.file-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 8px;
}

:deep(.v-stepper-header) {
  box-shadow: none !important;
}

:deep(.v-stepper-item) {
  padding: 16px;
}

:deep(.v-stepper-item__avatar) {
  margin: 0 auto 8px;
}
</style>
