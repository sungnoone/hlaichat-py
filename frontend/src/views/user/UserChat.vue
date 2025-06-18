<template>
  <div>
    <!-- Embedded 類型：嵌入 n8n 對話元件 -->
    <EmbeddedChatInterface v-if="chatType === 'embedded'" />
    
    <!-- Webhook 類型：自訂 ChatGPT 風格聊天介面 -->
    <WebhookChatInterface v-else-if="chatType === 'webhook'" />
    
    <!-- 未知類型或載入中 -->
    <div v-else class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <p class="mt-4 text-h6">載入中...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import EmbeddedChatInterface from '@/components/EmbeddedChatInterface.vue'
import WebhookChatInterface from '@/components/WebhookChatInterface.vue'

export default {
  name: 'UserChat',
  components: {
    EmbeddedChatInterface,
    WebhookChatInterface
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const chatType = ref(null)

    onMounted(() => {
      // 從查詢參數中獲取聊天類型
      const type = route.query.type
      const linkId = route.query.linkId

      if (!type || !linkId) {
        console.error('缺少必要的查詢參數')
        router.push('/user-dashboard')
        return
      }

      if (type === 'embedded' || type === 'webhook') {
        chatType.value = type
      } else {
        console.error('未知的聊天類型:', type)
        router.push('/user-dashboard')
      }
    })

    return {
      chatType
    }
  }
}
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  color: #666;
}
</style> 