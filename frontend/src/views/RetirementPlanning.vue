<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-2">Retirement Planning</h1>
        <p class="text-subtitle-1 text-grey">Plan your retirement with AI-powered investment recommendations</p>
      </v-col>
    </v-row>

    <!-- Investment Options Section -->
    <v-row class="mt-4">
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title>Find Investment Options</v-card-title>
          <v-card-text>
            <v-select
              v-model="optionsForm.risk_tolerance"
              :items="['low', 'medium', 'high']"
              label="Risk Tolerance"
              outlined
              dense
            />
            <v-text-field
              v-model.number="optionsForm.investment_amount"
              label="Investment Amount (RM)"
              type="number"
              outlined
              dense
              prefix="RM"
            />
            <v-text-field
              v-model.number="optionsForm.time_horizon"
              label="Years to Retirement"
              type="number"
              outlined
              dense
            />
            <v-btn
              color="primary"
              block
              @click="getInvestmentOptions"
              :loading="loading.options"
            >
              Get Recommendations
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card elevation="2" v-if="investmentOptions">
          <v-card-title>Recommended Investment Options</v-card-title>
          <v-card-text>
            <v-alert type="info" dense class="mb-4">
              Found {{ investmentOptions.total_options }} suitable options for your profile
            </v-alert>
            
            <v-list>
              <v-list-item
                v-for="product in investmentOptions.recommendations"
                :key="product.id"
                class="mb-2"
              >
                <v-list-item-content>
                  <v-list-item-title class="text-h6">
                    {{ product.name }}
                    <v-chip small :color="getRiskColor(product.risk_level)" class="ml-2">
                      {{ product.risk_level }} risk
                    </v-chip>
                    <v-chip small color="success" class="ml-2">
                      Score: {{ product.suitability_score }}
                    </v-chip>
                  </v-list-item-title>
                  <v-list-item-subtitle class="mt-2">
                    {{ product.provider }} • {{ product.type }}
                  </v-list-item-subtitle>
                  <div class="mt-2">
                    <strong>5-Year Avg Return:</strong> {{ product.returns.average_5yr }}%
                    <br>
                    <strong>Management Fee:</strong> {{ product.fees.management_fee }}%
                    <br>
                    <strong>Min Investment:</strong> RM{{ product.minimum_investment }}
                  </div>
                  <v-btn
                    small
                    color="primary"
                    class="mt-2"
                    @click="viewProductDetails(product.id)"
                  >
                    View Details
                  </v-btn>
                  <v-btn
                    small
                    color="success"
                    class="mt-2 ml-2"
                    @click="openInvestDialog(product)"
                  >
                    Invest Now
                  </v-btn>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Retirement Projection Section -->
    <v-row class="mt-6">
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title>Calculate Projection</v-card-title>
          <v-card-text>
            <v-text-field
              v-model.number="projectionForm.current_age"
              label="Current Age"
              type="number"
              outlined
              dense
            />
            <v-text-field
              v-model.number="projectionForm.retirement_age"
              label="Retirement Age"
              type="number"
              outlined
              dense
            />
            <v-text-field
              v-model.number="projectionForm.current_savings"
              label="Current Savings (RM)"
              type="number"
              outlined
              dense
              prefix="RM"
            />
            <v-text-field
              v-model.number="projectionForm.monthly_contribution"
              label="Monthly Contribution (RM)"
              type="number"
              outlined
              dense
              prefix="RM"
            />
            <v-text-field
              v-model.number="projectionForm.expected_return"
              label="Expected Return (%)"
              type="number"
              outlined
              dense
              suffix="%"
            />
            <v-btn
              color="primary"
              block
              @click="calculateProjection"
              :loading="loading.projection"
            >
              Calculate
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card elevation="2" v-if="projection">
          <v-card-title>Your Retirement Projection</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-card outlined>
                  <v-card-text>
                    <div class="text-h4 primary--text">
                      RM{{ formatNumber(projection.projection.total_future_value) }}
                    </div>
                    <div class="text-subtitle-2">Total at Retirement</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="6">
                <v-card outlined>
                  <v-card-text>
                    <div class="text-h4 success--text">
                      RM{{ formatNumber(projection.projection.investment_gains) }}
                    </div>
                    <div class="text-subtitle-2">Investment Gains</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="6">
                <v-card outlined>
                  <v-card-text>
                    <div class="text-h5">
                      RM{{ formatNumber(projection.monthly_income_at_retirement['4_percent_rule']) }}
                    </div>
                    <div class="text-subtitle-2">Monthly Income (4% Rule)</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="6">
                <v-card outlined>
                  <v-card-text>
                    <div class="text-h5">
                      {{ projection.projection.return_on_investment }}%
                    </div>
                    <div class="text-subtitle-2">ROI</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            <v-alert :type="projection.recommendation.includes('track') ? 'success' : 'warning'" class="mt-4">
              {{ projection.recommendation }}
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Product Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="800">
      <v-card v-if="selectedProduct">
        <v-card-title>
          {{ selectedProduct.name }}
          <v-spacer />
          <v-btn icon @click="detailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <h3>Returns</h3>
              <v-simple-table dense>
                <tbody>
                  <tr v-for="(value, year) in selectedProduct.returns" :key="year">
                    <td>{{ year }}</td>
                    <td class="text-right">{{ value }}%</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-col>
            <v-col cols="12" md="6">
              <h3>Fees</h3>
              <v-simple-table dense>
                <tbody>
                  <tr v-for="(value, fee) in selectedProduct.fees" :key="fee">
                    <td>{{ fee.replace('_', ' ') }}</td>
                    <td class="text-right">{{ value }}%</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-col>
          </v-row>
          <div class="mt-4">
            <h3>Description</h3>
            <p>{{ selectedProduct.description }}</p>
          </div>
          <div class="mt-4">
            <h3>Features</h3>
            <v-chip
              v-for="feature in selectedProduct.features"
              :key="feature"
              class="ma-1"
              small
            >
              {{ feature }}
            </v-chip>
          </div>
          <div class="mt-4">
            <h3>Suitable For</h3>
            <v-chip
              v-for="suit in selectedProduct.suitable_for"
              :key="suit"
              class="ma-1"
              small
              color="primary"
            >
              {{ suit }}
            </v-chip>
          </div>
          <div class="mt-4" v-if="selectedProduct.regulatory_info">
            <h3>Regulatory Information</h3>
            <p><strong>Regulated by:</strong> {{ selectedProduct.regulatory_info.regulated_by }}</p>
            <p><strong>Investor Protection:</strong> {{ selectedProduct.regulatory_info.investor_protection }}</p>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="openInvestDialog(selectedProduct)">
            Invest Now
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Investment Dialog -->
    <v-dialog v-model="investDialog" max-width="500">
      <v-card v-if="investProduct">
        <v-card-title>Invest in {{ investProduct.name }}</v-card-title>
        <v-card-text>
          <v-text-field
            v-model.number="investAmount"
            label="Investment Amount (RM)"
            type="number"
            outlined
            prefix="RM"
            :rules="[v => v >= investProduct.minimum_investment || `Minimum: RM${investProduct.minimum_investment}`]"
          />
          <v-select
            v-model="paymentMethod"
            :items="['online_banking', 'fpx', 'credit_card']"
            label="Payment Method"
            outlined
          />
          <v-alert type="info" dense v-if="investProduct.fees.sales_charge">
            Sales charge: {{ investProduct.fees.sales_charge }}%
            (RM{{ (investAmount * investProduct.fees.sales_charge / 100).toFixed(2) }})
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="investDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            @click="createOrder"
            :loading="loading.order"
            :disabled="investAmount < investProduct.minimum_investment"
          >
            Proceed to Payment
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Order Success Dialog -->
    <v-dialog v-model="orderDialog" max-width="600" persistent>
      <v-card v-if="orderResult">
        <v-card-title class="success white--text">
          Order Created Successfully!
        </v-card-title>
        <v-card-text class="pt-4">
          <p><strong>Order ID:</strong> {{ orderResult.order_id }}</p>
          <p><strong>Product:</strong> {{ orderResult.product.name }}</p>
          <p><strong>Investment Amount:</strong> RM{{ orderResult.investment_details.gross_amount }}</p>
          <p><strong>Net Investment:</strong> RM{{ orderResult.investment_details.net_investment }}</p>
          
          <v-divider class="my-4" />
          
          <h3>Next Steps:</h3>
          <ol>
            <li v-for="(step, index) in orderResult.next_steps" :key="index" class="mb-2">
              {{ step }}
            </li>
          </ol>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="orderDialog = false">Close</v-btn>
          <v-btn color="primary" :href="orderResult.payment_url" target="_blank">
            Proceed to Payment
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar for errors -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script>
import { supabase } from '../supabase'

export default {
  name: 'RetirementPlanning',
  data() {
    return {
      optionsForm: {
        risk_tolerance: 'medium',
        investment_amount: 10000,
        time_horizon: 20
      },
      projectionForm: {
        current_age: 30,
        retirement_age: 60,
        current_savings: 50000,
        monthly_contribution: 1000,
        expected_return: 6.5
      },
      investmentOptions: null,
      projection: null,
      selectedProduct: null,
      investProduct: null,
      investAmount: 0,
      paymentMethod: 'online_banking',
      orderResult: null,
      detailsDialog: false,
      investDialog: false,
      orderDialog: false,
      loading: {
        options: false,
        projection: false,
        order: false
      },
      snackbar: {
        show: false,
        message: '',
        color: 'error'
      }
    }
  },
  methods: {
    async getInvestmentOptions() {
      this.loading.options = true
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/retirement/investment-options`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`
          },
          body: JSON.stringify(this.optionsForm)
        })
        
        if (!response.ok) throw new Error('Failed to get investment options')
        
        this.investmentOptions = await response.json()
      } catch (error) {
        this.showError(error.message)
      } finally {
        this.loading.options = false
      }
    },
    
    async calculateProjection() {
      this.loading.projection = true
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/retirement/projection`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`
          },
          body: JSON.stringify(this.projectionForm)
        })
        
        if (!response.ok) throw new Error('Failed to calculate projection')
        
        this.projection = await response.json()
      } catch (error) {
        this.showError(error.message)
      } finally {
        this.loading.projection = false
      }
    },
    
    async viewProductDetails(productId) {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/retirement/product/${productId}`, {
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        })
        
        if (!response.ok) throw new Error('Failed to get product details')
        
        this.selectedProduct = await response.json()
        this.detailsDialog = true
      } catch (error) {
        this.showError(error.message)
      }
    },
    
    openInvestDialog(product) {
      this.investProduct = product
      this.investAmount = product.minimum_investment || 1000
      this.investDialog = true
      this.detailsDialog = false
    },
    
    async createOrder() {
      this.loading.order = true
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/retirement/order`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`
          },
          body: JSON.stringify({
            product_id: this.investProduct.id,
            amount: this.investAmount,
            payment_method: this.paymentMethod
          })
        })
        
        if (!response.ok) throw new Error('Failed to create order')
        
        this.orderResult = await response.json()
        this.investDialog = false
        this.orderDialog = true
      } catch (error) {
        this.showError(error.message)
      } finally {
        this.loading.order = false
      }
    },
    
    getRiskColor(risk) {
      const colors = {
        low: 'green',
        medium: 'orange',
        high: 'red'
      }
      return colors[risk] || 'grey'
    },
    
    formatNumber(num) {
      return new Intl.NumberFormat('en-MY').format(num)
    },
    
    showError(message) {
      this.snackbar.message = message
      this.snackbar.color = 'error'
      this.snackbar.show = true
    }
  }
}
</script>
