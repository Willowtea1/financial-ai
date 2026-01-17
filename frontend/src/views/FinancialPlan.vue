<template>
  <v-container class="py-8">
    <v-row v-if="planData">
      <v-col cols="12" class="text-center mb-8">
        <h1 class="text-h3 font-weight-bold mb-2">Your Personalised Financial Plan</h1>
        <p class="text-body-1 text--secondary">Tailored to your financial situation</p>
      </v-col>
    </v-row>

    <!-- Your Situation -->
    <v-row v-if="planData">
      <v-col cols="12" md="6">
        <v-card elevation="3" class="pa-4 mb-4">
          <v-card-title class="text-h5 mb-3">
            <v-icon left color="primary">mdi-account-circle</v-icon>
            Your Situation
          </v-card-title>
          <v-card-text>
            <p class="text-body-1" v-html="formatText(planData.situation)"></p>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Top 3 Priorities -->
      <v-col cols="12" md="6">
        <v-card elevation="3" class="pa-4 mb-4">
          <v-card-title class="text-h5 mb-3">
            <v-icon left color="primary">mdi-star-circle</v-icon>
            Your Top 3 Priorities
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="(priority, index) in planData.priorities"
                :key="index"
                class="px-0"
              >
                <v-list-item-avatar>
                  <v-avatar color="primary" size="32">
                    <span class="white--text">{{ index + 1 }}</span>
                  </v-avatar>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title v-html="formatText(priority)"></v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 12-Month Roadmap -->
    <v-row v-if="planData">
      <v-col cols="12">
        <v-card elevation="3" class="pa-4 mb-4">
          <v-card-title class="text-h5 mb-3">
            <v-icon left color="primary">mdi-calendar-month</v-icon>
            12-Month Roadmap
          </v-card-title>
          <v-card-text>
            <div v-html="formatText(planData.roadmap)"></div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- What To Do This Month -->
    <v-row v-if="planData">
      <v-col cols="12" md="6">
        <v-card elevation="3" class="pa-4 mb-4">
          <v-card-title class="text-h5 mb-3">
            <v-icon left color="primary">mdi-calendar-today</v-icon>
            What To Do This Month
          </v-card-title>
          <v-card-text>
            <div v-html="formatText(planData.thisMonthActions)"></div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Long-Term Strategy -->
      <v-col cols="12" md="6">
        <v-card elevation="3" class="pa-4 mb-4">
          <v-card-title class="text-h5 mb-3">
            <v-icon left color="primary">mdi-chart-line</v-icon>
            Long-Term Strategy
          </v-card-title>
          <v-card-text>
            <div v-html="formatText(planData.longTermStrategy)"></div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Refine Button -->
    <v-row v-if="planData">
      <v-col cols="12" class="text-center">
        <v-btn
          x-large
          color="primary"
          rounded
          elevation="4"
          @click="openChatModal"
          class="px-8"
        >
          <v-icon left>mdi-chat</v-icon>
          Refine My Plan with AI
        </v-btn>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-else>
      <v-col cols="12" class="text-center">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <p class="mt-4">Loading your financial plan...</p>
      </v-col>
    </v-row>

    <!-- Chat Modal -->
    <ChatModal
      v-model="chatDialog"
      :plan-data="planData"
      @plan-updated="handlePlanUpdate"
    />
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ChatModal from '../components/ChatModal.vue'

const route = useRoute()
const chatDialog = ref(false)
const planData = ref(null)

onMounted(() => {
  // Try to get plan data from sessionStorage first
  const storedPlan = sessionStorage.getItem('financialPlan')
  if (storedPlan) {
    try {
      planData.value = JSON.parse(storedPlan)
      return
    } catch (e) {
      console.error('Error parsing stored plan data:', e)
    }
  }

  // Fallback to query parameter (for backward compatibility)
  const planDataParam = route.query.planData
  if (planDataParam) {
    try {
      planData.value = JSON.parse(decodeURIComponent(planDataParam))
    } catch (e) {
      console.error('Error parsing plan data from query:', e)
    }
  }
})

const formatText = (text) => {
  if (!text) return ''
  // Convert markdown-style formatting to HTML
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const openChatModal = () => {
  chatDialog.value = true
}

const handlePlanUpdate = (updatedPlan) => {
  planData.value = updatedPlan
  // Update sessionStorage with new plan data
  sessionStorage.setItem('financialPlan', JSON.stringify(updatedPlan))
}
</script>

<style scoped>
</style>
