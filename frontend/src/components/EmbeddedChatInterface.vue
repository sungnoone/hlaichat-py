<template>
  <v-container fluid class="embedded-chat-container pa-0 fill-height">
    <!-- 標題欄 -->
    <v-app-bar color="primary" density="compact" class="chat-header">
      <v-btn icon @click="goBack" class="mr-2">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-app-bar-title>
        {{ chatLink?.name || '聊天機器人' }}
      </v-app-bar-title>
    </v-app-bar>

    <!-- 嵌入的 n8n 對話元件 -->
    <v-main class="embedded-main">
      <div v-if="chatLink && chatLink.embed_code" class="embed-container">
        <div v-html="chatLink.embed_code" class="embed-content"></div>
      </div>
      <div v-else-if="chatLink && !chatLink.embed_code" class="error-container">
        <v-icon size="64" color="error" class="mb-4">mdi-alert-circle</v-icon>
        <h3 class="text-h5 mb-2">嵌入代碼未設定</h3>
        <p class="text-body-1 text-grey">此聊天連結尚未設定嵌入代碼，請聯絡管理員。</p>
      </div>
      <div v-else class="loading-container">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4 text-h6">載入中...</p>
      </div>
    </v-main>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

export default {
  name: 'EmbeddedChatInterface',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const chatLink = ref(null)

    // 返回上一頁
    const goBack = () => {
      router.push('/user-dashboard')
    }

    // 獲取聊天連結資訊
    const fetchChatLink = async () => {
      const linkId = route.query.linkId
      if (!linkId) {
        router.push('/user-dashboard')
        return
      }

      try {
        const response = await axios.get(`/api/chat-links/${linkId}`)
        if (response.data.success) {
          chatLink.value = response.data.data
          
          // 確認是 embedded 類型
          if (chatLink.value.link_type !== 'n8n_embedded_chat') {
            console.error('此連結不是 embedded 類型')
            router.push('/user-dashboard')
            return
          }
        } else {
          throw new Error('無法獲取聊天連結資訊')
        }
      } catch (error) {
        console.error('獲取聊天連結失敗:', error)
        router.push('/user-dashboard')
      }
    }

    onMounted(() => {
      fetchChatLink()
    })

    return {
      chatLink,
      goBack
    }
  }
}
</script>

<style scoped>
.embedded-chat-container {
  height: 100vh;
  background-color: #f5f5f5;
}

.chat-header {
  border-bottom: 1px solid #e0e0e0;
}

.embedded-main {
  height: calc(100vh - 64px);
}

.embed-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.embed-content {
  width: 100%;
  height: 100%;
}

/* 確保嵌入的內容填滿整個容器 */
.embed-content :deep(iframe) {
  width: 100% !important;
  height: 100% !important;
  border: none !important;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}
</style> 