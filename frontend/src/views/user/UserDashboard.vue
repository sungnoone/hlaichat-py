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
        <v-card class="mx-auto h-100 d-flex flex-column">
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
                :color="link.link_type === 'hosted' ? 'primary' : 'secondary'"
                class="mb-4"
              >
                {{ link.link_type === 'hosted' ? '網址' : '嵌入代碼' }}
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
              v-if="link.link_type === 'hosted'"
              color="primary"
              :href="link.url"
              target="_blank"
              prepend-icon="mdi-open-in-new"
            >
              開啟聊天
            </v-btn>
            <v-btn
              v-else
              color="primary"
              @click="openEmbeddedChat(link)"
              prepend-icon="mdi-code-tags"
            >
              檢視嵌入代碼
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- 嵌入代碼對話框 -->
    <v-dialog v-model="embeddedDialog.show" max-width="700px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          <span>{{ embeddedDialog.title }}</span>
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="embeddedDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-alert type="info" density="compact" class="mb-3">
            您可以複製以下代碼並嵌入到您的網頁中。
          </v-alert>
          <v-textarea
            v-model="embeddedDialog.content"
            readonly
            auto-grow
            variant="outlined"
            rows="8"
            label="嵌入代碼"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="copyEmbeddedCode">
            <v-icon start>mdi-content-copy</v-icon>
            複製代碼
          </v-btn>
          <v-btn color="grey" variant="text" @click="embeddedDialog.show = false">
            關閉
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 複製成功提示 -->
    <v-snackbar v-model="copySuccess" :timeout="2000" color="success">
      已複製到剪貼簿
    </v-snackbar>
  </UserLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import UserLayout from '@/components/UserLayout.vue'
import axios from 'axios'

export default {
  name: 'UserDashboard',
  components: {
    UserLayout
  },
  setup() {
    const chatLinks = ref([])
    const embeddedDialog = ref({
      show: false,
      title: '',
      content: ''
    })
    const copySuccess = ref(false)
    const loading = ref(false)

    // 格式化日期
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-TW')
    }

    // 開啟嵌入代碼對話框
    const openEmbeddedChat = (link) => {
      embeddedDialog.value = {
        show: true,
        title: link.name,
        content: link.embed_code
      }
    }

    // 複製嵌入代碼
    const copyEmbeddedCode = () => {
      navigator.clipboard.writeText(embeddedDialog.value.content)
        .then(() => {
          copySuccess.value = true
        })
        .catch(error => {
          console.error('複製失敗:', error)
        })
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
      embeddedDialog,
      copySuccess,
      loading,
      formatDate,
      openEmbeddedChat,
      copyEmbeddedCode
    }
  }
}
</script>