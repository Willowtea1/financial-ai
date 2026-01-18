import { createRouter, createWebHistory } from 'vue-router'
import { supabase } from '../supabase'
import LandingPage from '../views/LandingPage.vue'
import Questionnaire from '../views/Questionnaire.vue'
import Chatbot from '../views/Chatbot.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/questionnaire',
    name: 'Questionnaire',
    component: Questionnaire,
    meta: { requiresAuth: true }
  },
  {
    path: '/chatbot',
    name: 'Chatbot',
    component: Chatbot,
    meta: { requiresAuth: true }
  },
  // Redirect old routes to new structure
  {
    path: '/plan',
    redirect: '/chatbot'
  },
  {
    path: '/test-upload',
    redirect: '/chatbot'
  },
  {
    path: '/retirement',
    redirect: '/chatbot'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for auth and questionnaire check
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth) {
    // Check if user is authenticated
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      // Not authenticated, redirect to landing
      return next('/')
    }

    // Check if going to chatbot
    if (to.name === 'Chatbot') {
      // Check if questionnaire is completed
      const questionnaireCompleted = localStorage.getItem('questionnaire_completed')
      
      if (!questionnaireCompleted || questionnaireCompleted !== 'true') {
        // Questionnaire not completed, redirect to questionnaire
        return next('/questionnaire')
      }
    }
  }

  next()
})

export default router
