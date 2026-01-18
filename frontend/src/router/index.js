import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import Questionnaire from '../views/Questionnaire.vue'
import FinancialPlan from '../views/FinancialPlan.vue'
import TestUpload from '../views/TestUpload.vue'
import RetirementPlanning from '../views/RetirementPlanning.vue'
import Chatbot from '../views/Chatbot.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage
  },
  {
    path: '/questionnaire',
    name: 'Questionnaire',
    component: Questionnaire
  },
  {
    path: '/plan',
    name: 'FinancialPlan',
    component: FinancialPlan,
    props: route => ({ planData: route.query.planData })
  },
  {
    path: '/test-upload',
    name: 'TestUpload',
    component: TestUpload
  },
  {
    path: '/retirement',
    name: 'RetirementPlanning',
    component: RetirementPlanning
  },
  {
    path: '/chatbot',
    name: 'Chatbot',
    component: Chatbot
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
