import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import Questionnaire from '../views/Questionnaire.vue'
import FinancialPlan from '../views/FinancialPlan.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
