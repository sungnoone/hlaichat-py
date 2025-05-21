<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <h1 class="login-title">AI Chat 管理平台</h1>
        <p class="text-subtitle-1 text-grey-darken-1">登入以管理 AI 聊天流程對話網址</p>
      </div>
      
      <v-tabs v-model="activeTab" grow>
        <v-tab value="platform">平台帳號</v-tab>
        <v-tab value="ad">AD 帳號</v-tab>
      </v-tabs>

      <v-card-text>
        <!-- 平台帳號登入表單 -->
        <v-form v-if="activeTab === 'platform'" ref="platformForm" @submit.prevent="login" class="mt-4">
          <v-text-field
            v-model="platformLogin.username"
            label="使用者名稱"
            :rules="[v => !!v || '請輸入使用者名稱']"
            prepend-inner-icon="mdi-account"
            variant="outlined"
            :disabled="loading"
          ></v-text-field>
          
          <v-text-field
            v-model="platformLogin.password"
            label="密碼"
            type="password"
            :rules="[v => !!v || '請輸入密碼']"
            prepend-inner-icon="mdi-lock"
            variant="outlined"
            :disabled="loading"
          ></v-text-field>
          
          <v-btn
            type="submit"
            color="primary"
            block
            :loading="loading"
            class="mt-4"
          >
            登入
          </v-btn>
        </v-form>

        <!-- AD 帳號登入表單 -->
        <v-form v-if="activeTab === 'ad'" ref="adForm" @submit.prevent="loginWithAD" class="mt-4">
          <v-text-field
            v-model="adLogin.username"
            label="AD 使用者名稱"
            :rules="[v => !!v || '請輸入 AD 使用者名稱']"
            prepend-inner-icon="mdi-account"
            variant="outlined"
            :disabled="loading"
          ></v-text-field>
          
          <v-text-field
            v-model="adLogin.password"
            label="AD 密碼"
            type="password"
            :rules="[v => !!v || '請輸入 AD 密碼']"
            prepend-inner-icon="mdi-lock"
            variant="outlined"
            :disabled="loading"
          ></v-text-field>
          
          <v-btn
            type="submit"
            color="primary"
            block
            :loading="loading"
            class="mt-4"
          >
            AD 登入
          </v-btn>
        </v-form>
      </v-card-text>

      <div class="login-footer">
        <v-img src="/logo.png" alt="翰林雲端 Logo" height="48" class="mb-2 mx-auto"></v-img>
        <p class="text-body-2 text-grey">© {{ new Date().getFullYear() }} AI Chat 管理平台</p>
      </div>
    </div>
    
    <!-- 錯誤提示 -->
    <v-snackbar
      v-model="showError"
      :timeout="3000"
      color="error"
      location="top"
    >
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="showError = false"
        >
          關閉
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const { proxy } = getCurrentInstance()
    const activeTab = ref('platform')
    const loading = ref(false)
    const showError = ref(false)
    const errorMessage = ref('')
    const adConfigured = ref(false)
    
    const platformLogin = ref({
      username: '',
      password: ''
    })
    
    const adLogin = ref({
      username: '',
      password: ''
    })
    
    const platformForm = ref(null)
    const adForm = ref(null)
    
    // 檢查AD設定是否已配置
    onMounted(async () => {
      try {
        const response = await proxy.$axios.get('/api/ad-config/status')
        adConfigured.value = response.data.data.configured
      } catch (error) {
        console.error('無法獲取AD設定狀態:', error)
        adConfigured.value = false
      }
    })
    
    // 平台帳號登入
    const login = async () => {
      const { valid } = await platformForm.value.validate()
      
      if (!valid) return
      
      loading.value = true
      try {
        const response = await proxy.$axios.post('/api/auth/login', platformLogin.value)
        
        // 儲存認證資訊
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        
        // 根據使用者權限導向不同頁面
        const isAdmin = response.data.user.groups.some(group => 
          group.name === 'admins' || group.can_manage_platform === true
        )
        
        router.push(isAdmin ? '/dashboard' : '/user-dashboard')
        
      } catch (error) {
        errorMessage.value = error.response?.data?.detail || '登入失敗，請檢查您的認證信息'
        showError.value = true
      } finally {
        loading.value = false
      }
    }
    
    // AD帳號登入
    const loginWithAD = async () => {
      const { valid } = await adForm.value.validate()
      
      if (!valid) return
      
      loading.value = true
      try {
        const response = await proxy.$axios.post('/api/auth/ad-login', adLogin.value)
        
        // 儲存認證資訊
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        
        // 根據使用者權限導向不同頁面
        const isAdmin = response.data.user.groups.some(group => 
          group.name === 'admins' || group.can_manage_platform === true
        )
        
        router.push(isAdmin ? '/dashboard' : '/user-dashboard')
        
      } catch (error) {
        errorMessage.value = error.response?.data?.detail || 'AD登入失敗，請檢查您的認證信息'
        showError.value = true
      } finally {
        loading.value = false
      }
    }
    
    return {
      activeTab,
      platformLogin,
      adLogin,
      loading,
      showError,
      errorMessage,
      adConfigured,
      platformForm,
      adForm,
      login,
      loginWithAD
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.login-content {
  width: 100%;
  max-width: 480px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.login-footer {
  text-align: center;
  margin-top: 2rem;
}
</style> 