<template>
  <AdminLayout>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">AD 設定</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="bg-primary text-white">
            AD 網域設定
          </v-card-title>
          
          <v-card-text class="pt-4">
            <v-alert
              v-if="adStatus.configured"
              color="success"
              icon="mdi-check-circle"
              class="mb-4"
            >
              AD 設定已配置完成並可用
            </v-alert>
            
            <v-alert
              v-else
              color="info"
              icon="mdi-information"
              class="mb-4"
            >
              AD 設定尚未完成配置，請填寫以下資訊
            </v-alert>
            
            <v-form ref="adForm" @submit.prevent="saveADConfig">
              <v-text-field
                v-model="adConfig.domain_name"
                label="網域名稱"
                hint="例如：hanlin.com.tw"
                variant="outlined"
                :rules="[v => !!v || '請輸入網域名稱']"
                class="mb-3"
              ></v-text-field>
              
              <v-text-field
                v-model="adConfig.primary_dc"
                label="主要網域控制器"
                hint="例如：192.168.1.6"
                variant="outlined"
                :rules="[v => !!v || '請輸入主要網域控制器IP']"
                class="mb-3"
              ></v-text-field>
              
              <v-text-field
                v-model="adConfig.secondary_dcs"
                label="次要網域控制器"
                hint="例如：192.168.1.5,192.168.5.5 (多個以逗號分隔)"
                variant="outlined"
                class="mb-3"
              ></v-text-field>
              
              <v-text-field
                v-model="adConfig.bind_username"
                label="綁定查詢帳號"
                hint="用於LDAP查詢的帳號，例如：ldap_query"
                variant="outlined"
                :rules="[v => !!v || '請輸入綁定查詢帳號']"
                class="mb-3"
              ></v-text-field>
              
              <v-text-field
                v-model="adConfig.bind_password"
                label="綁定查詢密碼"
                hint="用於LDAP查詢的密碼"
                type="password"
                variant="outlined"
                :rules="[v => !!v || '請輸入綁定查詢密碼']"
                class="mb-3"
              ></v-text-field>
              
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  color="secondary"
                  variant="outlined"
                  class="mr-2"
                  @click="testConnection"
                  :loading="loading.test"
                  :disabled="!canTest"
                >
                  <v-icon start>mdi-check-network</v-icon>
                  測試連線
                </v-btn>
                
                <v-btn
                  color="primary"
                  type="submit"
                  :loading="loading.save"
                  :disabled="!canSave"
                >
                  <v-icon start>mdi-content-save</v-icon>
                  儲存設定
                </v-btn>
              </v-card-actions>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title class="bg-primary text-white">
            AD 使用者搜尋
          </v-card-title>
          
          <v-card-text class="pt-4">
            <v-alert
              v-if="!adStatus.configured"
              color="warning"
              icon="mdi-alert"
              class="mb-4"
            >
              請先完成 AD 設定後再使用此功能
            </v-alert>
            
            <v-form ref="searchForm" @submit.prevent="searchAdUsers">
              <v-text-field
                v-model="searchQuery"
                label="搜尋 AD 使用者"
                hint="輸入姓名、帳號或信箱關鍵字"
                variant="outlined"
                append-inner-icon="mdi-magnify"
                clearable
                :rules="[v => !!v || '請輸入搜尋關鍵字']"
                class="mb-3"
                :disabled="!adStatus.configured"
                @click:append-inner="searchAdUsers"
              ></v-text-field>
              
              <v-btn
                color="primary"
                block
                :loading="loading.search"
                :disabled="!adStatus.configured || !searchQuery"
                class="mb-3"
                @click="searchAdUsers"
              >
                <v-icon start>mdi-account-search</v-icon>
                搜尋
              </v-btn>
            </v-form>
            
            <v-divider class="my-4"></v-divider>
            
            <div v-if="adUsers.length > 0">
              <h3 class="text-subtitle-1 mb-2">搜尋結果</h3>
              
              <v-list lines="two">
                <v-list-item
                  v-for="user in adUsers"
                  :key="user.guid"
                  :title="user.full_name"
                  :subtitle="user.username"
                >
                  <template v-slot:prepend>
                    <v-avatar color="info" class="mr-3">
                      <span class="text-white">{{ getUserInitials(user.full_name) }}</span>
                    </v-avatar>
                  </template>
                  
                  <template v-slot:append>
                    <v-btn
                      size="small"
                      icon="mdi-account-plus"
                      variant="text"
                      color="primary"
                      @click="selectAdUser(user)"
                      title="加入系統使用者"
                    ></v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </div>
            
            <div v-else-if="showNoResults" class="text-center py-5">
              <v-icon size="48" color="grey-lighten-1">mdi-account-off</v-icon>
              <p class="text-body-1 mt-2 text-grey">沒有找到符合條件的 AD 使用者</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 加入使用者對話框 -->
    <v-dialog v-model="userDialog.show" max-width="600px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          加入 AD 使用者
        </v-card-title>
        
        <v-card-text class="pt-4">
          <p class="mb-4">將 AD 使用者 <strong>{{ userDialog.user.full_name }}</strong> ({{ userDialog.user.username }}) 加入系統</p>
          
          <v-divider class="mb-4"></v-divider>
          
          <v-sheet max-height="250px" class="overflow-y-auto mb-4">
            <h3 class="text-subtitle-1 mb-2">選擇群組</h3>
            <v-checkbox
              v-for="group in groups"
              :key="group.id"
              v-model="userDialog.selectedGroups"
              :label="group.name"
              :value="group.id"
              hide-details
              class="mb-2"
            ></v-checkbox>
          </v-sheet>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="userDialog.show = false">
            取消
          </v-btn>
          <v-btn color="primary" @click="addAdUser" :loading="loading.addUser">
            加入使用者
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- 操作結果提示 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">
          關閉
        </v-btn>
      </template>
    </v-snackbar>
  </AdminLayout>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from 'axios'

export default {
  name: 'ADConfig',
  components: {
    AdminLayout
  },
  setup() {
    const adStatus = ref({
      configured: false
    })
    
    const adConfig = ref({
      domain_name: '',
      primary_dc: '',
      secondary_dcs: '',
      bind_username: '',
      bind_password: ''
    })
    
    const loading = reactive({
      test: false,
      save: false,
      search: false,
      addUser: false
    })
    
    const searchQuery = ref('')
    const adUsers = ref([])
    const showNoResults = ref(false)
    const groups = ref([])
    
    const userDialog = reactive({
      show: false,
      user: {
        username: '',
        full_name: '',
        email: '',
        guid: ''
      },
      selectedGroups: []
    })
    
    const snackbar = reactive({
      show: false,
      text: '',
      color: 'success'
    })
    
    const adForm = ref(null)
    const searchForm = ref(null)
    
    // 計算屬性：是否可以測試連線
    const canTest = computed(() => {
      return adConfig.value.domain_name &&
             adConfig.value.primary_dc &&
             adConfig.value.bind_username &&
             adConfig.value.bind_password
    })
    
    // 計算屬性：是否可以儲存設定
    const canSave = computed(() => {
      return canTest.value
    })
    
    // 獲取 AD 設定
    const fetchADConfig = async () => {
      try {
        const status = await axios.get('/api/ad-config/status')
        adStatus.value = status.data.data
        
        if (adStatus.value.configured) {
          const config = await axios.get('/api/ad-config')
          if (config.data.success) {
            adConfig.value = config.data.data
          }
        }
      } catch (error) {
        console.error('獲取 AD 設定失敗:', error)
        showSnackbar('獲取 AD 設定失敗', 'error')
      }
    }
    
    // 獲取群組列表
    const fetchGroups = async () => {
      try {
        const response = await axios.get('/api/groups')
        if (response.data.success) {
          groups.value = response.data.items || []
        }
      } catch (error) {
        console.error('獲取群組失敗:', error)
      }
    }
    
    // 測試 AD 連線
    const testConnection = async () => {
      if (!canTest.value) return
      
      loading.test = true
      try {
        const response = await axios.post('/api/ad-config/test-connection', {
          domain_name: adConfig.value.domain_name,
          primary_dc: adConfig.value.primary_dc,
          bind_username: adConfig.value.bind_username,
          bind_password: adConfig.value.bind_password
        })
        
        if (response.data.success) {
          showSnackbar('AD 連線測試成功', 'success')
        }
      } catch (error) {
        console.error('AD 連線測試失敗:', error)
        showSnackbar(error.response?.data?.detail || 'AD 連線測試失敗', 'error')
      } finally {
        loading.test = false
      }
    }
    
    // 儲存 AD 設定
    const saveADConfig = async () => {
      const { valid } = await adForm.value.validate()
      
      if (!valid) return
      
      loading.save = true
      try {
        const response = await axios.put('/api/ad-config', adConfig.value)
        
        if (response.data.success) {
          adStatus.value.configured = true
          showSnackbar('AD 設定已儲存', 'success')
        }
      } catch (error) {
        console.error('儲存 AD 設定失敗:', error)
        showSnackbar(error.response?.data?.detail || '儲存 AD 設定失敗', 'error')
      } finally {
        loading.save = false
      }
    }
    
    // 搜尋 AD 使用者
    const searchAdUsers = async () => {
      const { valid } = await searchForm.value.validate()
      
      if (!valid || !adStatus.value.configured) return
      
      loading.search = true
      adUsers.value = []
      showNoResults.value = false
      
      try {
        const response = await axios.post('/api/ad-config/search-users', {
          search_term: searchQuery.value,
          max_results: 10
        })
        
        if (response.data.success) {
          adUsers.value = response.data.data || []
          showNoResults.value = adUsers.value.length === 0
        }
      } catch (error) {
        console.error('搜尋 AD 使用者失敗:', error)
        showSnackbar(error.response?.data?.detail || '搜尋 AD 使用者失敗', 'error')
      } finally {
        loading.search = false
      }
    }
    
    // 選擇 AD 使用者
    const selectAdUser = (user) => {
      userDialog.user = user
      userDialog.selectedGroups = []
      userDialog.show = true
    }
    
    // 加入 AD 使用者
    const addAdUser = async () => {
      if (userDialog.selectedGroups.length === 0) {
        showSnackbar('請至少選擇一個群組', 'warning')
        return
      }
      
      loading.addUser = true
      try {
        // 為AD使用者產生一個隨機密碼，因為系統要求密碼欄位
        const randomPassword = Math.random().toString(36).slice(-10)
        
        const response = await axios.post('/api/users', {
          username: userDialog.user.username,
          full_name: userDialog.user.full_name,
          email: userDialog.user.email,
          department: userDialog.user.department,
          is_active: true,
          is_ad_user: true,
          ad_guid: userDialog.user.guid,
          group_ids: userDialog.selectedGroups,
          password: randomPassword // 添加隨機密碼
        })
        
        if (response.data.success) {
          userDialog.show = false
          showSnackbar('AD 使用者已成功加入系統', 'success')
        }
      } catch (error) {
        console.error('加入 AD 使用者失敗:', error)
        showSnackbar(error.response?.data?.detail || '加入 AD 使用者失敗', 'error')
      } finally {
        loading.addUser = false
      }
    }
    
    // 獲取使用者縮寫
    const getUserInitials = (fullName) => {
      if (!fullName) return '?'
      return fullName
        .split(' ')
        .map(name => name.charAt(0))
        .join('')
        .toUpperCase()
        .substr(0, 2)
    }
    
    // 顯示提示訊息
    const showSnackbar = (text, color = 'success') => {
      snackbar.text = text
      snackbar.color = color
      snackbar.show = true
    }
    
    onMounted(() => {
      fetchADConfig()
      fetchGroups()
    })
    
    return {
      adStatus,
      adConfig,
      loading,
      searchQuery,
      adUsers,
      showNoResults,
      groups,
      userDialog,
      snackbar,
      adForm,
      searchForm,
      canTest,
      canSave,
      testConnection,
      saveADConfig,
      searchAdUsers,
      selectAdUser,
      addAdUser,
      getUserInitials
    }
  }
}
</script> 