<template>
  <AdminLayout>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">儀表板</h1>
      </v-col>
    </v-row>

    <v-row>
      <!-- 統計卡片 -->
      <v-col cols="12" md="4">
        <v-card class="mb-4">
          <v-card-item>
            <template v-slot:prepend>
              <v-avatar color="primary" size="48" rounded="0">
                <v-icon icon="mdi-account-multiple" size="large"></v-icon>
              </v-avatar>
            </template>
            <v-card-title>使用者數量</v-card-title>
            <v-card-subtitle class="mt-2">
              <span class="text-h4">{{ stats.userCount || 0 }}</span>
            </v-card-subtitle>
          </v-card-item>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="mb-4">
          <v-card-item>
            <template v-slot:prepend>
              <v-avatar color="info" size="48" rounded="0">
                <v-icon icon="mdi-account-group" size="large"></v-icon>
              </v-avatar>
            </template>
            <v-card-title>群組數量</v-card-title>
            <v-card-subtitle class="mt-2">
              <span class="text-h4">{{ stats.groupCount || 0 }}</span>
            </v-card-subtitle>
          </v-card-item>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="mb-4">
          <v-card-item>
            <template v-slot:prepend>
              <v-avatar color="success" size="48" rounded="0">
                <v-icon icon="mdi-link-variant" size="large"></v-icon>
              </v-avatar>
            </template>
            <v-card-title>聊天連結數量</v-card-title>
            <v-card-subtitle class="mt-2">
              <span class="text-h4">{{ stats.chatLinkCount || 0 }}</span>
            </v-card-subtitle>
          </v-card-item>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <!-- 最近操作記錄 -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-history" class="mr-2"></v-icon>
            最近操作記錄
            <v-spacer></v-spacer>
            <v-btn variant="text" size="small" to="/logs" class="text-none">
              查看全部
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-table v-if="logs.length > 0">
              <thead>
                <tr>
                  <th>使用者</th>
                  <th>操作</th>
                  <th>時間</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in logs" :key="log.id">
                  <td>{{ log.user_full_name }}</td>
                  <td>{{ log.action }}</td>
                  <td>{{ formatDate(log.timestamp) }}</td>
                </tr>
              </tbody>
            </v-table>
            <div v-else class="text-center py-5 text-grey">
              尚無操作記錄
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 最新聊天連結 -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-link-variant" class="mr-2"></v-icon>
            最新聊天連結
            <v-spacer></v-spacer>
            <v-btn variant="text" size="small" to="/chat-links" class="text-none">
              查看全部
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-table v-if="chatLinks.length > 0">
              <thead>
                <tr>
                  <th>名稱</th>
                  <th>類型</th>
                  <th>建立時間</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="link in chatLinks" :key="link.id">
                  <td>{{ link.name }}</td>
                  <td>
                    <v-chip size="small" :color="link.link_type === 'hosted' ? 'primary' : 'secondary'">
                      {{ link.link_type === 'hosted' ? 'Hosted' : 'Embedded' }}
                    </v-chip>
                  </td>
                  <td>{{ formatDate(link.created_at) }}</td>
                </tr>
              </tbody>
            </v-table>
            <div v-else class="text-center py-5 text-grey">
              尚無聊天連結
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </AdminLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from 'axios'

export default {
  name: 'Dashboard',
  components: {
    AdminLayout
  },
  setup() {
    const loading = ref(false)
    const stats = ref({
      userCount: 0,
      groupCount: 0,
      chatLinkCount: 0
    })
    const logs = ref([])
    const chatLinks = ref([])

    // 格式化日期
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-TW')
    }

    // 獲取統計數據
    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/stats', {
          timeout: 5000 // 設定請求超時時間
        })
        if (response.data && response.data.success) {
          stats.value = response.data.data || {
            userCount: 0,
            groupCount: 0,
            chatLinkCount: 0
          }
        } else {
          console.error('獲取統計數據失敗:', response.data?.message || '未知錯誤')
        }
      } catch (error) {
        console.error('獲取統計數據失敗:', error)
      }
    }

    // 獲取最近操作記錄
    const fetchRecentLogs = async () => {
      try {
        const response = await axios.get('/api/logs/recent', { 
          params: { limit: 5 },
          timeout: 5000 // 設定請求超時時間
        })
        if (response.data && response.data.success) {
          logs.value = response.data.data || []
        } else {
          console.error('獲取最近操作記錄失敗:', response.data?.message || '未知錯誤')
          logs.value = []
        }
      } catch (error) {
        console.error('獲取最近操作記錄失敗:', error)
        logs.value = []
      }
    }

    // 獲取最新聊天連結
    const fetchRecentChatLinks = async () => {
      try {
        const response = await axios.get('/api/chat-links/recent', { 
          params: { limit: 5 },
          timeout: 5000 // 設定請求超時時間
        })
        if (response.data && response.data.success) {
          chatLinks.value = response.data.data || []
        } else {
          console.error('獲取最新聊天連結失敗:', response.data?.message || '未知錯誤')
          chatLinks.value = []
        }
      } catch (error) {
        console.error('獲取最新聊天連結失敗:', error)
        chatLinks.value = []
      }
    }

    // 頁面載入時獲取數據
    onMounted(() => {
      loading.value = true
      Promise.all([
        fetchStats(),
        fetchRecentLogs(),
        fetchRecentChatLinks()
      ]).finally(() => {
        loading.value = false
      })
    })

    return {
      loading,
      stats,
      logs,
      chatLinks,
      formatDate
    }
  }
}
</script> 