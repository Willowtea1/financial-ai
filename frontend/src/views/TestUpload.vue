<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="text-h5">
            Test Document Upload
          </v-card-title>
          
          <v-card-text>
            <!-- Auth Status -->
            <v-alert v-if="!user" type="warning" class="mb-4">
              Please sign in with Google to upload documents
            </v-alert>
            
            <v-alert v-else type="success" class="mb-4">
              Signed in as: {{ user.email }}
            </v-alert>

            <!-- Sign In Button -->
            <v-btn
              v-if="!user"
              color="primary"
              @click="signInWithGoogle"
              prepend-icon="mdi-google"
              class="mb-4"
            >
              Sign in with Google
            </v-btn>

            <!-- Test Auth Button -->
            <v-btn
              v-if="user"
              color="secondary"
              @click="testAuth"
              class="mb-4 ml-2"
            >
              Test Auth
            </v-btn>

            <!-- Sign Out Button -->
            <v-btn
              v-if="user"
              color="error"
              @click="signOut"
              class="mb-4 ml-2"
            >
              Sign Out
            </v-btn>

            <!-- File Upload -->
            <v-file-input
              v-model="files"
              label="Select files to upload"
              multiple
              chips
              show-size
              accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg"
              :disabled="!user || uploading"
              class="mb-4"
            ></v-file-input>

            <v-btn
              color="primary"
              @click="uploadFiles"
              :disabled="!files || files.length === 0 || !user || uploading"
              :loading="uploading"
              block
            >
              Upload Files
            </v-btn>

            <!-- Upload Results -->
            <v-alert v-if="uploadResult" :type="uploadResult.type" class="mt-4">
              {{ uploadResult.message }}
            </v-alert>

            <!-- Uploaded Documents -->
            <v-card v-if="uploadedDocs.length > 0" class="mt-4">
              <v-card-title>Uploaded Documents</v-card-title>
              <v-list>
                <v-list-item
                  v-for="doc in uploadedDocs"
                  :key="doc.documentId"
                >
                  <v-list-item-title>{{ doc.fileName }}</v-list-item-title>
                  <v-list-item-subtitle>
                    Status: {{ doc.extractionStatus }}
                    <v-chip
                      v-if="doc.extractionStatus === 'pending'"
                      color="orange"
                      size="small"
                      class="ml-2"
                    >
                      Processing...
                    </v-chip>
                    <v-chip
                      v-else-if="doc.extractionStatus === 'completed'"
                      color="green"
                      size="small"
                      class="ml-2"
                    >
                      Ready
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card>

            <!-- Document Details -->
            <v-card v-if="selectedDoc" class="mt-4">
              <v-card-title>Document Summary</v-card-title>
              <v-card-text>
                <p><strong>File:</strong> {{ selectedDoc.fileName }}</p>
                <p><strong>Status:</strong> {{ selectedDoc.extractionStatus }}</p>
                <v-divider class="my-3"></v-divider>
                <p v-if="selectedDoc.summary">{{ selectedDoc.summary }}</p>
                <p v-else class="text-grey">Summary not yet available...</p>
              </v-card-text>
            </v-card>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { supabase, API_BASE_URL } from '../supabase'

const user = ref(null)
const files = ref([])
const uploading = ref(false)
const uploadResult = ref(null)
const uploadedDocs = ref([])
const selectedDoc = ref(null)

// Check if user is signed in
onMounted(async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session) {
    user.value = session.user
    loadUserDocuments()
  }

  // Listen for auth changes
  supabase.auth.onAuthStateChange((event, session) => {
    user.value = session?.user || null
    if (user.value) {
      loadUserDocuments()
    }
  })
})

// Sign in with Google
async function signInWithGoogle() {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: window.location.origin
    }
  })
  
  if (error) {
    console.error('Sign in error:', error)
    uploadResult.value = {
      type: 'error',
      message: `Sign in failed: ${error.message}`
    }
  }
}

// Sign out
async function signOut() {
  await supabase.auth.signOut()
  user.value = null
  uploadedDocs.value = []
  uploadResult.value = null
}

// Test authentication
async function testAuth() {
  try {
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      throw new Error('No session')
    }
    
    console.log('Testing auth with token...')
    
    const response = await fetch(`${API_BASE_URL}/api/auth/test`, {
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      }
    })
    
    const result = await response.json()
    console.log('Auth test result:', result)
    
    uploadResult.value = {
      type: result.status === 'success' ? 'success' : 'error',
      message: result.status === 'success' 
        ? 'Authentication working!' 
        : `Auth failed: ${result.message}`
    }
  } catch (error) {
    console.error('Test auth error:', error)
    uploadResult.value = {
      type: 'error',
      message: `Test failed: ${error.message}`
    }
  }
}

// Upload files
async function uploadFiles() {
  if (!files.value || files.value.length === 0) return
  
  uploading.value = true
  uploadResult.value = null
  
  try {
    // Get session token
    const { data: { session }, error: sessionError } = await supabase.auth.getSession()
    
    if (sessionError || !session) {
      throw new Error('Not authenticated. Please sign in again.')
    }
    
    console.log('Session token:', session.access_token.substring(0, 20) + '...')
    
    // Create FormData
    const formData = new FormData()
    files.value.forEach(file => {
      formData.append('files', file)
      console.log('Adding file:', file.name)
    })
    
    console.log('Uploading to:', `${API_BASE_URL}/api/upload`)
    
    // Upload to backend
    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      },
      body: formData
    })
    
    console.log('Response status:', response.status)
    
    const result = await response.json()
    console.log('Response data:', result)
    
    if (response.ok) {
      uploadResult.value = {
        type: 'success',
        message: `Successfully uploaded ${result.successCount} file(s). Extraction is processing in the background.`
      }
      
      // Add to uploaded docs list
      uploadedDocs.value.push(...result.successful)
      
      // Clear file input
      files.value = []
      
      // Check status after 10 seconds
      setTimeout(() => {
        result.successful.forEach(doc => {
          checkDocumentStatus(doc.documentId)
        })
      }, 10000)
    } else {
      throw new Error(result.detail || JSON.stringify(result))
    }
  } catch (error) {
    console.error('Upload error:', error)
    uploadResult.value = {
      type: 'error',
      message: `Upload failed: ${error.message}`
    }
  } finally {
    uploading.value = false
  }
}

// Load user's documents
async function loadUserDocuments() {
  try {
    const { data, error } = await supabase
      .from('user_uploaded_documents')
      .select('id, fileName, extractionStatus, summary')
      .order('created_at', { ascending: false })
      .limit(10)
    
    if (error) throw error
    
    uploadedDocs.value = data.map(doc => ({
      documentId: doc.id,
      fileName: doc.fileName,
      extractionStatus: doc.extractionStatus,
      summary: doc.summary
    }))
  } catch (error) {
    console.error('Error loading documents:', error)
  }
}

// Check document status
async function checkDocumentStatus(documentId) {
  try {
    const { data, error } = await supabase
      .from('user_uploaded_documents')
      .select('extractionStatus, summary')
      .eq('id', documentId)
      .single()
    
    if (error) throw error
    
    // Update the document in the list
    const doc = uploadedDocs.value.find(d => d.documentId === documentId)
    if (doc) {
      doc.extractionStatus = data.extractionStatus
      doc.summary = data.summary
      
      if (data.extractionStatus === 'completed') {
        selectedDoc.value = doc
      }
    }
  } catch (error) {
    console.error('Error checking status:', error)
  }
}
</script>
