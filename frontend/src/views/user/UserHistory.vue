<template>
  <UserLayout>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">使用紀錄</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card>
          <v-tabs v-model="activeTab">
            <v-tab value="chats">聊天紀錄</v-tab>
            <v-tab value="operations">操作紀錄</v-tab>
          </v-tabs>

          <v-card-text>
            <!-- 聊天紀錄 -->
            <div v-if="activeTab === 'chats'">
              <v-data-table
                :headers="chatHeaders"
                :items="chatHistory"
                :loading="loading"
                :items-per-page="10"
                class="elevation-1"
              >
                <!-- 連結名稱 -->
                <template v-slot:item.chat_link_name="{ item }">
                  <v-chip size="small" color="primary">
                    {{ item.chat_link_name }}
                  </v-chip>
                </template>

                <!-- 時間欄位 -->
                <template v-slot:item.created_at="{ item }">
                  {{ formatDate(item.created_at) }}
                </template>
              </v-data-table>

              <div v-if="chatHistory.length === 0 && !loading" class="text-center py-5">
                <v-icon size="48" color="grey-lighten-1">mdi-chat-remove</v-icon>
                <p class="text-body-1 mt-2 text-grey">暫無聊天紀錄</p>
              </div>
            </div>

            <!-- 操作紀錄 -->
            <div v-if="activeTab === 'operations'">
              <v-data-table
                :headers="operationHeaders"
                :items="operationHistory"
                :loading="loading"
                :items-per-page="10"
                class="elevation-1"
              >
                <!-- 操作類型 -->
                <template v-slot:item.action="{ item }">
                  <v-chip 
                    size="small" 
                    :color="getActionColor(item.action)"
                  >
                    {{ item.action }}
                  </v-chip>
                </template>

                <!-- 時間欄位 -->
                <template v-slot:item.timestamp="{ item }">
                  {{ formatDate(item.timestamp) }}
                </template>
              </v-data-table>

              <div v-if="operationHistory.length === 0 && !loading" class="text-center py-5">
                <v-icon size="48" color="grey-lighten-1">mdi-history</v-icon>
                <p class="text-body-1 mt-2 text-grey">暫無操作紀錄</p>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </UserLayout>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import UserLayout from '@/components/UserLayout.vue'
import axios from 'axios'

export default {
  name: 'UserHistory',
  components: {
    UserLayout
  },
  setup() {
    const activeTab = ref('chats')
    const loading = ref(false)
    const chatHistory = ref([])
    const operationHistory = ref([])

    // 表格欄位定義
    const chatHeaders = ref([
      { title: '聊天機器人', key: 'chat_link_name', width: '25%' },
      { title: '訊息內容', key: 'message', width: '50%' },
      { title: '時間', key: 'created_at', width: '25%' }
    ])

    const operationHeaders = ref([
      { title: '操作類型', key: 'action', width: '25%' },
      { title: '詳細資訊', key: 'details', width: '50%' },
      { title: '時間', key: 'timestamp', width: '25%' }
    ])

    // 格式化日期
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return new Intl.DateTimeFormat('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }

    // 獲取操作類型對應的顏色
    const getActionColor = (action) => {
      const actionColors = {
        'LOGIN': 'success',
        'LOGOUT': 'error',
        'VIEW_CHAT_LINK': 'primary',
        'UPDATE_PROFILE': 'info'
      }
      return actionColors[action] || 'secondary'
    }

    // 獲取聊天紀錄
    const fetchChatHistory = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/user-profiles/chat-history')
        if (response.data.success) {
          chatHistory.value = response.data.data || []
        }
      } catch (error) {
        console.error('獲取聊天紀錄失敗:', error)
      } finally {
        loading.value = false
      }
    }

    // 獲取操作紀錄
    const fetchOperationHistory = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/user-profiles/operation-logs')
        
        if (response.data.success) {
          operationHistory.value = response.data.data || []
        }
      } catch (error) {
        console.error('獲取操作紀錄失敗:', error)
      } finally {
        loading.value = false
      }
    }

    // 監聽活動標籤變化
    watch(activeTab, (newTab) => {
      if (newTab === 'chats') {
        fetchChatHistory()
      } else if (newTab === 'operations') {
        fetchOperationHistory()
      }
    })

    onMounted(() => {
      fetchChatHistory()
    })

    return {
      activeTab,
      loading,
      chatHistory,
      operationHistory,
      chatHeaders,
      operationHeaders,
      formatDate,
      getActionColor
    }
  }
}
</script> 