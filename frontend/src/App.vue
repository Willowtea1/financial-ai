<template>
  <v-app>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { onMounted } from 'vue'
import { handleOAuthCallback, setupAuthListener, getSession, storeTokens } from './utils/auth'

onMounted(async () => {
  // Handle OAuth callback if present in URL
  const tokensHandled = await handleOAuthCallback()
  
  if (tokensHandled) {
    console.log('OAuth tokens processed and URL cleaned')
  }
  
  // Setup auth state listener
  setupAuthListener()
  
  // Ensure current session tokens are stored
  const session = await getSession()
  if (session) {
    storeTokens(session.access_token, session.refresh_token)
  }
})
</script>

<style>
#app {
  font-family: 'Roboto', sans-serif;
}
</style>
