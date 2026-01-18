<template>
  <div class="payment-gateway-classic">
    <!-- Header -->
    <div class="header">
      <div class="header-content">
        <h1 class="tagline">Simple. Convenient. Secure.</h1>
        <img src="https://www.ipay88.com.my/epayment/images/ipay88_logo.png" alt="iPay88" class="logo" />
        <p class="provider-text">*iPay88 is Online Payment Service provided by Mobile88.Com Sdn. Bhd.</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div v-if="!processing && !completed" class="payment-form">
        <!-- Summary Section -->
        <div class="summary-section">
          <div class="section-header">
            <span class="icon">📝</span>
            <span class="title">Summary Of Transaction</span>
          </div>
          <table class="summary-table">
            <tbody>
              <tr>
                <td class="label">Net Charges</td>
                <td class="value">MYR {{ formatAmount(amount) }}</td>
              </tr>
              <tr>
                <td class="label">Pay To</td>
                <td class="value">EPF Malaysia</td>
              </tr>
              <tr>
                <td class="label">Payment of</td>
                <td class="value">{{ transactionId }}</td>
              </tr>
              <tr>
                <td class="label">Reference No / Payment ID</td>
                <td class="value">{{ referenceNo }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Credit Card Details Section -->
        <div class="card-details-section">
          <div class="section-title">Credit Card Details</div>
          
          <div class="timeout">
            Timeout in : <span class="timeout-value">{{ timeoutMinutes }}:{{ timeoutSeconds }}</span>
          </div>

          <div class="form-group">
            <label>Cardholder Name</label>
            <input 
              type="text" 
              v-model="cardholderName" 
              placeholder="JOHN DOE"
              class="form-input"
            />
            <span class="example-link">Example <span class="help-icon">?</span></span>
          </div>

          <div class="form-group">
            <label>Credit Card No.</label>
            <input 
              type="text" 
              v-model="cardNumber" 
              placeholder="1234 5678 9012 3456"
              maxlength="19"
              class="form-input"
            />
            <div class="card-logos">
              <img src="https://upload.wikimedia.org/wikipedia/commons/0/04/Visa.svg" alt="Visa" />
              <img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg" alt="Mastercard" />
            </div>
          </div>

          <div class="form-group">
            <label>CVC/CVV2</label>
            <input 
              type="text" 
              v-model="cvv" 
              placeholder="123"
              maxlength="4"
              class="form-input small"
            />
            <span class="example-link">CVC/CVV2 <span class="help-icon">?</span></span>
          </div>

          <div class="form-group">
            <label>Expiry Date</label>
            <div class="expiry-inputs">
              <select v-model="expiryMonth" class="form-select">
                <option value="">--</option>
                <option v-for="m in 12" :key="m" :value="String(m).padStart(2, '0')">{{ String(m).padStart(2, '0') }}</option>
              </select>
              <span class="separator">/</span>
              <select v-model="expiryYear" class="form-select">
                <option value="">----</option>
                <option v-for="y in 10" :key="y" :value="2024 + y">{{ 2024 + y }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Card Issuing Country</label>
            <select v-model="country" class="form-select full">
              <option value="Malaysia">Malaysia</option>
              <option value="Singapore">Singapore</option>
              <option value="Thailand">Thailand</option>
              <option value="Indonesia">Indonesia</option>
            </select>
          </div>

          <div class="form-group">
            <label>Card Issuing Bank</label>
            <select v-model="bank" class="form-select full">
              <option value="">Please Select</option>
              <option value="Maybank">Maybank</option>
              <option value="CIMB">CIMB Bank</option>
              <option value="Public Bank">Public Bank</option>
              <option value="RHB">RHB Bank</option>
              <option value="Hong Leong">Hong Leong Bank</option>
              <option value="AmBank">AmBank</option>
            </select>
          </div>

          <!-- Terms Checkbox -->
          <div class="terms-section">
            <label class="checkbox-label">
              <input type="checkbox" v-model="agreedToTerms" />
              I authorize Mobile88.com Sdn Bhd to debit the above net charges from my credit card and I have read & agreed to 
              <a href="#" class="terms-link">iPay88 Privacy Statement</a>
            </label>
          </div>

          <div class="note">
            Note: *iPAY88* will be shown on your credit card statement
          </div>

          <!-- Action Buttons -->
          <div class="button-group">
            <button 
              class="btn btn-proceed" 
              @click="handlePayment"
              :disabled="!isFormValid"
            >
              » Proceed
            </button>
            <button class="btn btn-cancel" @click="handleCancel">
              Cancel
            </button>
          </div>
        </div>
      </div>

      <!-- Processing State -->
      <div v-else-if="processing" class="processing-state">
        <div class="spinner"></div>
        <h3>Processing Payment...</h3>
        <p>Please wait while we process your transaction</p>
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
      </div>

      <!-- Success State -->
      <div v-else-if="completed" class="success-state">
        <div class="success-icon">✓</div>
        <h2>Payment Successful!</h2>
        <p>Your EPF top-up has been processed successfully</p>
        
        <div class="receipt-box">
          <div class="receipt-row">
            <span>Transaction ID:</span>
            <strong>{{ transactionId }}</strong>
          </div>
          <div class="receipt-row">
            <span>Amount Paid:</span>
            <strong>RM {{ formatAmount(amount) }}</strong>
          </div>
          <div class="receipt-row">
            <span>Tax Relief:</span>
            <strong>RM {{ formatAmount(taxRelief) }}</strong>
          </div>
        </div>

        <div class="info-box">
          <strong>What's Next?</strong>
          <ul>
            <li>Receipt sent to your email</li>
            <li>Funds will be credited within 2-3 business days</li>
            <li>Tax relief will be reflected in your EA form</li>
          </ul>
        </div>

        <button class="btn btn-proceed" @click="handleClose">
          Close & Return to Chat
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaymentGateway',
  data() {
    return {
      transactionId: '',
      referenceNo: '',
      amount: 0,
      taxRelief: 0,
      cardholderName: '',
      cardNumber: '',
      cvv: '',
      expiryMonth: '',
      expiryYear: '',
      country: 'Malaysia',
      bank: '',
      agreedToTerms: false,
      processing: false,
      completed: false,
      timeoutMinutes: 7,
      timeoutSeconds: 27,
      countdownInterval: null
    }
  },
  computed: {
    isFormValid() {
      return this.cardholderName && 
             this.cardNumber.length >= 16 && 
             this.cvv.length >= 3 && 
             this.expiryMonth && 
             this.expiryYear && 
             this.bank &&
             this.agreedToTerms
    }
  },
  mounted() {
    // Get payment details from URL query params
    const urlParams = new URLSearchParams(window.location.search)
    this.transactionId = urlParams.get('txn_id') || this.generateTransactionId()
    this.amount = parseFloat(urlParams.get('amount')) || 3000
    this.taxRelief = parseFloat(urlParams.get('tax_relief')) || this.amount
    this.referenceNo = this.generateReferenceNo()
    
    // Start countdown timer
    this.startCountdown()
  },
  beforeUnmount() {
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval)
    }
  },
  methods: {
    generateTransactionId() {
      return `INV${Date.now().toString().slice(-5)}`
    },
    
    generateReferenceNo() {
      return `${Math.floor(Math.random() * 9000) + 1000} / ${Date.now()}`
    },
    
    formatAmount(amount) {
      return new Intl.NumberFormat('en-MY', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount)
    },
    
    startCountdown() {
      this.countdownInterval = setInterval(() => {
        if (this.timeoutSeconds > 0) {
          this.timeoutSeconds--
        } else if (this.timeoutMinutes > 0) {
          this.timeoutMinutes--
          this.timeoutSeconds = 59
        } else {
          clearInterval(this.countdownInterval)
          alert('Session timeout! Please try again.')
          this.handleCancel()
        }
      }, 1000)
    },
    
    async handlePayment() {
      if (!this.isFormValid) return
      
      this.processing = true
      
      // Simulate payment processing (2-3 seconds)
      await new Promise(resolve => setTimeout(resolve, 2500))
      
      this.processing = false
      this.completed = true
      
      // Stop countdown
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval)
      }
    },
    
    handleCancel() {
      if (confirm('Are you sure you want to cancel this transaction?')) {
        window.close()
      }
    },
    
    handleClose() {
      window.close()
      setTimeout(() => {
        window.location.href = '/'
      }, 500)
    }
  }
}
</script>

<style scoped>
.payment-gateway-classic {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  min-height: 100vh;
  padding: 20px;
}

/* Header */
.header {
  background: white;
  padding: 30px 20px;
  text-align: center;
  border-bottom: 3px solid #e0e0e0;
  margin-bottom: 30px;
}

.header-content {
  max-width: 900px;
  margin: 0 auto;
}

.tagline {
  color: #ff8c42;
  font-size: 32px;
  font-weight: normal;
  margin: 0 0 20px 0;
  letter-spacing: 1px;
}

.logo {
  height: 60px;
  margin-bottom: 10px;
}

.provider-text {
  color: #666;
  font-size: 12px;
  margin: 10px 0 0 0;
}

/* Main Content */
.main-content {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border: 1px solid #ddd;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Summary Section */
.summary-section {
  border-bottom: 2px solid #e0e0e0;
  padding: 20px;
}

.section-header {
  background: linear-gradient(to right, #4a90e2, #7ab8f5);
  color: white;
  padding: 10px 15px;
  margin: -20px -20px 15px -20px;
  font-size: 16px;
  font-weight: bold;
}

.section-header .icon {
  margin-right: 8px;
}

.summary-table {
  width: 100%;
  border-collapse: collapse;
}

.summary-table tr {
  border-bottom: 1px solid #e0e0e0;
}

.summary-table td {
  padding: 12px 10px;
}

.summary-table .label {
  color: #666;
  width: 40%;
}

.summary-table .value {
  color: #333;
  font-weight: bold;
}

/* Card Details Section */
.card-details-section {
  padding: 30px;
}

.section-title {
  color: #4a90e2;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #4a90e2;
}

.timeout {
  text-align: center;
  color: #28a745;
  font-size: 16px;
  margin-bottom: 30px;
  font-weight: bold;
}

.timeout-value {
  font-size: 18px;
}

/* Form Groups */
.form-group {
  margin-bottom: 20px;
  position: relative;
}

.form-group label {
  display: block;
  color: #333;
  font-weight: bold;
  margin-bottom: 8px;
  font-size: 14px;
}

.form-input {
  width: 100%;
  max-width: 400px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 3px;
  font-size: 14px;
}

.form-input.small {
  max-width: 150px;
}

.form-select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 3px;
  font-size: 14px;
  background: white;
}

.form-select.full {
  width: 100%;
  max-width: 400px;
}

.expiry-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.separator {
  font-size: 18px;
  color: #666;
}

.example-link {
  margin-left: 10px;
  color: #4a90e2;
  font-size: 13px;
  cursor: pointer;
}

.help-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  background: #4a90e2;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 16px;
  font-size: 12px;
  cursor: help;
}

.card-logos {
  display: inline-flex;
  gap: 10px;
  margin-left: 15px;
  vertical-align: middle;
}

.card-logos img {
  height: 24px;
}

/* Terms Section */
.terms-section {
  margin: 25px 0;
  padding: 15px;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  color: #333;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  margin-top: 3px;
  cursor: pointer;
}

.terms-link {
  color: #4a90e2;
  text-decoration: none;
}

.terms-link:hover {
  text-decoration: underline;
}

.note {
  color: #dc3545;
  font-size: 13px;
  font-style: italic;
  margin: 15px 0;
}

/* Buttons */
.button-group {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 12px 40px;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-proceed {
  background: #4a7ba7;
  color: white;
}

.btn-proceed:hover:not(:disabled) {
  background: #3a6b97;
}

.btn-proceed:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-cancel {
  background: #95a5b3;
  color: white;
}

.btn-cancel:hover {
  background: #7a8a98;
}

/* Processing State */
.processing-state {
  text-align: center;
  padding: 80px 40px;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4a90e2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 30px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.progress-bar {
  width: 100%;
  max-width: 400px;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  margin: 30px auto 0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4a90e2;
  animation: progress 2s ease-in-out infinite;
}

@keyframes progress {
  0% { width: 0%; }
  50% { width: 70%; }
  100% { width: 100%; }
}

/* Success State */
.success-state {
  text-align: center;
  padding: 60px 40px;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: #28a745;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  margin: 0 auto 30px;
}

.success-state h2 {
  color: #28a745;
  margin-bottom: 15px;
}

.success-state p {
  color: #666;
  margin-bottom: 30px;
}

.receipt-box {
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  padding: 20px;
  margin: 30px auto;
  max-width: 400px;
  text-align: left;
}

.receipt-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #e0e0e0;
}

.receipt-row:last-child {
  border-bottom: none;
}

.info-box {
  background: #e7f3ff;
  border: 1px solid #4a90e2;
  padding: 20px;
  margin: 30px auto;
  max-width: 400px;
  text-align: left;
  border-radius: 5px;
}

.info-box ul {
  margin: 10px 0 0 20px;
  padding: 0;
}

.info-box li {
  margin: 8px 0;
  color: #333;
}
</style>
