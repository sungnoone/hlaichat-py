<template>
  <AdminLayout>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">操作紀錄</h1>
      </v-col>
    </v-row>

    <!-- 搜尋與過濾 -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search.username"
              label="使用者名稱"
              prepend-inner-icon="mdi-account"
              variant="outlined"
              density="compact"
              hide-details
              class="mb-3 mb-md-0"
              @keyup.enter="fetchLogs"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="search.action"
              label="操作類型"
              :items="actionTypes"
              item-title="title"
              item-value="value"
              variant="outlined"
              density="compact"
              hide-details
              class="mb-3 mb-md-0"
              @update:model-value="fetchLogs"
            ></v-select>
          </v-col>
          <v-col cols="12" md="2">
            <v-btn color="primary" variant="tonal" block @click="fetchLogs">
              搜尋
            </v-btn>
          </v-col>
          <v-col cols="12" md="2">
            <v-btn color="secondary" variant="tonal" block @click="resetSearch">
              重設
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 操作紀錄列表 -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="logs"
        :loading="loading"
        :items-per-page="15"
        class="elevation-1"
      >
        <!-- 使用者欄 -->
        <template v-slot:item.username="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" color="primary" class="mr-2">
              <span class="text-white">{{ getUserInitials(item.user_full_name) }}</span>
            </v-avatar>
            <div>
              <div>{{ item.user_full_name }}</div>
              <div class="text-caption text-grey">{{ item.user_username }}</div>
            </div>
          </div>
        </template>

        <!-- 操作類型欄 -->
        <template v-slot:item.action="{ item }">
          <v-chip
            :color="getActionColor(item.action)"
            size="small"
          >
            {{ item.action }}
          </v-chip>
        </template>

        <!-- 時間欄 -->
        <template v-slot:item.timestamp="{ item }">
          {{ formatDateTime(item.timestamp) }}
        </template>
      </v-data-table>

      <!-- 分頁 -->
      <div class="d-flex justify-center pt-4 pb-3">
        <v-pagination
          v-model="pagination.page"
          :length="pagination.totalPages"
          :total-visible="7"
          @update:model-value="fetchLogs"
        ></v-pagination>
      </div>
    </v-card>
  </AdminLayout>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from 'axios'

export default {
  name: 'Logs',
  components: {
    AdminLayout
  },
  setup() {
    const logs = ref([])
    const loading = ref(false)
    const search = reactive({
      username: '',
      action: ''
    })
    const pagination = reactive({
      page: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 15
    })
    
    // 表格欄位定義
    const headers = ref([
      { title: '使用者', key: 'username', width: '25%' },
      { title: '操作類型', key: 'action', width: '15%' },
      { title: '詳細資訊', key: 'details', width: '35%' },
      { title: '時間', key: 'timestamp', width: '25%' },
    ])
    
    // 操作類型選項
    const actionTypes = [
      { title: '所有操作', value: '' },
      { title: '登入', value: 'LOGIN' },
      { title: '登出', value: 'LOGOUT' },
      { title: '建立使用者', value: 'CREATE_USER' },
      { title: '更新使用者', value: 'UPDATE_USER' },
      { title: '刪除使用者', value: 'DELETE_USER' },
      { title: '建立群組', value: 'CREATE_GROUP' },
      { title: '更新群組', value: 'UPDATE_GROUP' },
      { title: '刪除群組', value: 'DELETE_GROUP' },
      { title: '建立聊天連結', value: 'CREATE_CHAT_LINK' },
      { title: '更新聊天連結', value: 'UPDATE_CHAT_LINK' },
      { title: '刪除聊天連結', value: 'DELETE_CHAT_LINK' },
      { title: '使用聊天連結', value: 'USE_CHAT_LINK' },
      { title: '更新 AD 設定', value: 'UPDATE_AD_CONFIG' }
    ]
    
    // 獲取操作紀錄
    const fetchLogs = async (page = pagination.page) => {
      loading.value = true
      pagination.page = page
      
      try {
        const params = {
          page: pagination.page,
          page_size: pagination.itemsPerPage
        }
        
        if (search.username) {
          params.username = search.username
        }
        
        if (search.action) {
          params.action = search.action
        }
        
        const response = await axios.get('/api/logs', { params })
        
        if (response.data.success) {
          logs.value = response.data.items
          pagination.totalPages = response.data.total_pages
          pagination.totalItems = response.data.total
        }
      } catch (error) {
        console.error('獲取操作紀錄失敗:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 重設搜尋條件
    const resetSearch = () => {
      search.username = ''
      search.action = ''
      fetchLogs(1)
    }
    
    // 獲取操作類型對應的顏色
    const getActionColor = (action) => {
      const actionColors = {
        'LOGIN': 'success',
        'LOGOUT': 'error',
        'CREATE_USER': 'primary',
        'UPDATE_USER': 'info',
        'DELETE_USER': 'error',
        'CREATE_GROUP': 'primary',
        'UPDATE_GROUP': 'info',
        'DELETE_GROUP': 'error',
        'CREATE_CHAT_LINK': 'primary',
        'UPDATE_CHAT_LINK': 'info',
        'DELETE_CHAT_LINK': 'error',
        'USE_CHAT_LINK': 'secondary',
        'UPDATE_AD_CONFIG': 'warning'
      }
      return actionColors[action] || 'secondary'
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
    
    // 格式化日期時間
    const formatDateTime = (dateStr) => {
      const date = new Date(dateStr)
      return new Intl.DateTimeFormat('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).format(date)
    }
    
    onMounted(() => {
      fetchLogs()
    })
    
    return {
      logs,
      loading,
      search,
      pagination,
      headers,
      actionTypes,
      fetchLogs,
      resetSearch,
      getActionColor,
      getUserInitials,
      formatDateTime
    }
  }
}
</script> 