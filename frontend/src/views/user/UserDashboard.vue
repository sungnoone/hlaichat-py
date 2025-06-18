<template>
  <UserLayout>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">我的聊天機器人</h1>
      </v-col>
    </v-row>

    <!-- 沒有可用的聊天連結時顯示 -->
    <v-row v-if="chatLinks.length === 0">
      <v-col cols="12">
        <v-card class="text-center py-10">
          <v-card-text>
            <v-icon size="64" color="grey-lighten-1">mdi-robot-off</v-icon>
            <h3 class="text-h5 mt-4">尚無可用的聊天機器人</h3>
            <p class="text-body-1 mt-2 text-grey">管理員尚未為您配置任何可用的聊天機器人，請稍後再試或聯絡管理員。</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 可用的聊天連結列表 -->
    <v-row>
      <v-col
        v-for="link in chatLinks"
        :key="link.id"
        cols="12"
        md="6"
        lg="4"
      >
        <v-card class="mx-auto h-100 d-flex flex-column" hover>
          <v-card-item>
            <v-card-title>{{ link.name }}</v-card-title>
            <v-card-subtitle v-if="link.description">
              {{ link.description }}
            </v-card-subtitle>
          </v-card-item>

          <v-card-text class="flex-grow-1">
            <div>
              <v-chip 
                size="small" 
                :color="getLinkTypeColor(link.link_type)"
                class="mb-4"
              >
                {{ getLinkTypeText(link.link_type) }}
              </v-chip>
            </div>

            <p class="mb-3 text-caption text-grey">
              <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
              建立日期: {{ formatDate(link.created_at) }}
            </p>
          </v-card-text>

          <v-card-actions class="mt-auto">
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              @click="openChatLink(link)"
              :prepend-icon="getLinkTypeIcon(link.link_type)"
            >
              {{ getLinkTypeButtonText(link.link_type) }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>


  </UserLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import UserLayout from '@/components/UserLayout.vue'
import axios from 'axios'

export default {
  name: 'UserDashboard',
  components: {
    UserLayout
  },
  setup() {
    const router = useRouter()
    const chatLinks = ref([])
    const loading = ref(false)

    // 格式化日期
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-TW')
    }

    // 獲取連結類型顏色
    const getLinkTypeColor = (linkType) => {
      switch (linkType) {
        case 'n8n_host_chat':
          return 'primary'
        case 'n8n_embedded_chat':
          return 'secondary'
        case 'n8n_webhook':
          return 'success'
        default:
          return 'grey'
      }
    }

    // 獲取連結類型文字
    const getLinkTypeText = (linkType) => {
      switch (linkType) {
        case 'n8n_host_chat':
          return 'Hosted 聊天'
        case 'n8n_embedded_chat':
          return 'Embedded 聊天'
        case 'n8n_webhook':
          return 'Webhook 聊天'
        default:
          return '未知類型'
      }
    }

    // 獲取連結類型圖標
    const getLinkTypeIcon = (linkType) => {
      switch (linkType) {
        case 'n8n_host_chat':
          return 'mdi-open-in-new'
        case 'n8n_embedded_chat':
          return 'mdi-chat'
        case 'n8n_webhook':
          return 'mdi-chat'
        default:
          return 'mdi-help'
      }
    }

    // 獲取連結類型按鈕文字
    const getLinkTypeButtonText = (linkType) => {
      switch (linkType) {
        case 'n8n_host_chat':
          return '開啟聊天'
        case 'n8n_embedded_chat':
          return '開始對話'
        case 'n8n_webhook':
          return '開始對話'
        default:
          return '開啟'
      }
    }

    // 開啟聊天連結
    const openChatLink = (link) => {
      switch (link.link_type) {
        case 'n8n_host_chat':
          // Hosted 類型：另開新分頁導向聊天網址
          window.open(link.url, '_blank')
          break
        case 'n8n_embedded_chat':
          // Embedded 類型：進入嵌入 n8n 對話元件的頁面
          router.push({
            name: 'UserChat',
            query: {
              linkId: link.id,
              type: 'embedded'
            }
          })
          break
        case 'n8n_webhook':
          // Webhook 類型：進入專屬自訂的 ChatGPT 風格對話介面
          router.push({
            name: 'UserChat',
            query: {
              linkId: link.id,
              type: 'webhook'
            }
          })
          break
        default:
          console.error('未知的連結類型:', link.link_type)
      }
    }



    // 獲取可用的聊天連結
    const fetchChatLinks = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/chat-links')
        if (response.data.success) {
          chatLinks.value = response.data.items || []
        }
      } catch (error) {
        console.error('獲取聊天連結失敗:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchChatLinks()
    })

    return {
      chatLinks,
      loading,
      formatDate,
      getLinkTypeColor,
      getLinkTypeText,
      getLinkTypeIcon,
      getLinkTypeButtonText,
      openChatLink
    }
  }
}
</script>