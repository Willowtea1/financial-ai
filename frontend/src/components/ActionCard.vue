<template>
  <v-card class="action-card my-4" elevation="2" :class="{ 'completed': action.status === 'completed' }">
    <v-card-title class="d-flex align-center">
      <v-icon :color="getActionIcon().color" class="mr-2" size="large">
        {{ getActionIcon().icon }}
      </v-icon>
      <span>{{ action.title }}</span>
      <v-spacer></v-spacer>
      <v-chip v-if="action.status" :color="getStatusColor()" size="small" variant="flat">
        {{ action.status }}
      </v-chip>
    </v-card-title>

    <v-card-text>
      <p class="text-body-1 mb-3">{{ action.description }}</p>

      <!-- Action-specific content -->
      <div v-if="action.type === 'investment'" class="investment-details">
        <v-row dense>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Product</span>
              <p class="text-body-2 font-weight-bold">{{ action.data.productName }}</p>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Amount</span>
              <p class="text-body-2 font-weight-bold">RM {{ formatNumber(action.data.amount) }}</p>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Expected Return</span>
              <p class="text-body-2 font-weight-bold text-success">{{ action.data.expectedReturn }}% p.a.</p>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Risk Level</span>
              <p class="text-body-2 font-weight-bold">{{ action.data.riskLevel }}</p>
            </div>
          </v-col>
        </v-row>
      </div>

      <div v-else-if="action.type === 'epf_topup'" class="epf-details">
        <v-row dense>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Top-up Amount</span>
              <p class="text-body-2 font-weight-bold">RM {{ formatNumber(action.data.amount) }}</p>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Tax Relief</span>
              <p class="text-body-2 font-weight-bold text-success">RM {{ formatNumber(action.data.taxRelief) }}</p>
            </div>
          </v-col>
          <v-col cols="12">
            <v-alert density="compact" type="info" variant="tonal" class="mt-2">
              Eligible for tax relief up to RM {{ formatNumber(action.data.maxTaxRelief) }}
            </v-alert>
          </v-col>
        </v-row>
      </div>

      <div v-else-if="action.type === 'insurance'" class="insurance-details">
        <v-row dense>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Coverage</span>
              <p class="text-body-2 font-weight-bold">RM {{ formatNumber(action.data.coverage) }}</p>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Monthly Premium</span>
              <p class="text-body-2 font-weight-bold">RM {{ formatNumber(action.data.premium) }}</p>
            </div>
          </v-col>
          <v-col cols="12">
            <div class="detail-item">
              <span class="text-caption text-grey">Benefits</span>
              <v-chip-group>
                <v-chip v-for="benefit in action.data.benefits" :key="benefit" size="small" variant="outlined">
                  {{ benefit }}
                </v-chip>
              </v-chip-group>
            </div>
          </v-col>
        </v-row>
      </div>

      <div v-else-if="action.type === 'savings_goal'" class="savings-details">
        <v-row dense>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Goal</span>
              <p class="text-body-2 font-weight-bold">{{ action.data.goalName }}</p>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Target Amount</span>
              <p class="text-body-2 font-weight-bold">RM {{ formatNumber(action.data.targetAmount) }}</p>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Monthly Savings</span>
              <p class="text-body-2 font-weight-bold">RM {{ formatNumber(action.data.monthlyAmount) }}</p>
            </div>
          </v-col>
          <v-col cols="6">
            <div class="detail-item">
              <span class="text-caption text-grey">Time to Goal</span>
              <p class="text-body-2 font-weight-bold">{{ action.data.months }} months</p>
            </div>
          </v-col>
        </v-row>
      </div>
    </v-card-text>

    <v-card-actions class="pa-4">
      <v-btn
        v-if="action.status !== 'completed' && action.status !== 'processing'"
        color="error"
        variant="outlined"
        @click="$emit('decline', action)"
        :disabled="loading"
      >
        Decline
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        v-if="action.status !== 'completed'"
        color="primary"
        variant="flat"
        size="large"
        @click="$emit('approve', action)"
        :loading="loading"
        :disabled="action.status === 'processing'"
      >
        <v-icon start>{{ getActionButtonIcon() }}</v-icon>
        {{ getActionButtonText() }}
      </v-btn>
      <v-chip v-else color="success" variant="flat">
        <v-icon start>mdi-check-circle</v-icon>
        Completed
      </v-chip>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  action: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['approve', 'decline'])

const getActionIcon = () => {
  const icons = {
    investment: { icon: 'mdi-chart-line', color: 'success' },
    epf_topup: { icon: 'mdi-piggy-bank', color: 'primary' },
    insurance: { icon: 'mdi-shield-check', color: 'info' },
    savings_goal: { icon: 'mdi-target', color: 'warning' },
    bill_payment: { icon: 'mdi-receipt', color: 'secondary' }
  }
  return icons[props.action.type] || { icon: 'mdi-information', color: 'grey' }
}

const getStatusColor = () => {
  const colors = {
    pending: 'warning',
    processing: 'info',
    completed: 'success',
    declined: 'error'
  }
  return colors[props.action.status] || 'grey'
}

const getActionButtonIcon = () => {
  if (props.action.status === 'processing') return 'mdi-loading'
  return 'mdi-check-circle'
}

const getActionButtonText = () => {
  if (props.action.status === 'processing') return 'Processing...'
  
  const texts = {
    investment: 'Invest Now',
    epf_topup: 'Top Up EPF',
    insurance: 'Buy Insurance',
    savings_goal: 'Set Up Goal',
    bill_payment: 'Pay Now'
  }
  return texts[props.action.type] || 'Approve'
}

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-MY').format(num)
}
</script>

<style scoped>
.action-card {
  border-left: 4px solid rgb(var(--v-theme-primary));
  transition: all 0.3s ease;
}

.action-card:hover {
  box-shadow: 0 8px 16px rgba(0,0,0,0.15) !important;
}

.action-card.completed {
  border-left-color: rgb(var(--v-theme-success));
  opacity: 0.8;
}

.detail-item {
  margin-bottom: 8px;
}

.detail-item span {
  display: block;
  margin-bottom: 4px;
}

.investment-details,
.epf-details,
.insurance-details,
.savings-details {
  background: rgba(0,0,0,0.02);
  padding: 12px;
  border-radius: 8px;
  margin-top: 8px;
}
</style>
