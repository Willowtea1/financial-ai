<template>
  <v-container fluid class="pa-0">
    <v-row no-gutters class="hero-section" justify="center" align="center">
      <v-col cols="12" md="8" lg="6" class="text-center pa-8">
        <h1 class="text-h3 text-md-h2 font-weight-bold mb-4 text-white">
          Get your personalised financial plan in 5 minutes.
        </h1>
        <p class="text-h6 text-md-h5 mb-8 text-black">
          Answer a few questions and let AI build your financial roadmap.
        </p>
        <v-btn
          x-large
          color="primary"
          rounded
          elevation="4"
          @click="goToQuestionnaire"
          class="px-8"
        >
          Start My Financial Plan
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToQuestionnaire = () => {
  router.push('/questionnaire')
}
</script>

<style scoped>
.hero-section {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

@media (max-width: 960px) {
  .hero-section {
    min-height: 80vh;
  }
}
</style>
