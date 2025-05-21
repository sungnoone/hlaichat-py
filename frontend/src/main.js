import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

// MDI Icons
import '@mdi/font/css/materialdesignicons.css'

// Font Awesome
import '@fortawesome/fontawesome-free/css/all.css'

// 判斷是否為開發環境
const isDev = import.meta.env.MODE === 'development' || import.meta.env.DEV

// Axios 設置
import axios from 'axios'
// 從環境變數讀取 API 基礎 URL，如果未設定則使用預設值
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
axios.defaults.withCredentials = true // 允許跨域請求時發送 cookies
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    // 確保 token 未過期
    try {
      const tokenData = JSON.parse(atob(token.split('.')[1]))
      const expTime = tokenData.exp * 1000
      if (Date.now() >= expTime) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject('Token 已過期')
      }
    } catch (error) {
      console.error('Token 解析錯誤:', error)
    }
  }
  return config
})
axios.interceptors.response.use(
  response => response,
  error => {
    console.error('API 錯誤:', error.response || error)
    
    if (error.response) {
      // 伺服器回應錯誤
      if (error.response.status === 401) {
        console.log('認證失敗，重新導向到登入頁面')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
      } else if (error.response.status === 403) {
        console.log('權限不足')
        // 可以顯示錯誤訊息或重定向
      } else if (error.response.status >= 500) {
        console.log('伺服器錯誤')
        // 可以顯示錯誤訊息
      }
    } else if (error.request) {
      // 請求已發送但未收到回應
      console.log('無法連接到伺服器，請檢查網路連線')
    } else {
      // 請求設置出錯
      console.log('請求錯誤')
    }
    
    return Promise.reject(error)
  }
)

// 載入自訂樣式
import './assets/styles.css'

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#3498db',
          secondary: '#2c3e50',
          accent: '#9C27B0',
          error: '#e74c3c',
          warning: '#f39c12',
          info: '#3498db',
          success: '#2ecc71'
        },
      },
    },
  },
})

const app = createApp(App)

// 全局註冊axios
app.config.globalProperties.$axios = axios

app.use(router)
app.use(vuetify)

app.mount('#app') 