<template>
  <div class="webhook-chat-container">
    <!-- 頂部標題欄 -->
    <v-app-bar color="primary" density="compact" class="chat-header" app>
      <v-btn icon @click="goBack" class="mr-2">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-app-bar-title>
        {{ chatLink?.name || '聊天機器人' }}
      </v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="clearCurrentSession" :disabled="!currentSession || messages.length === 0">
        <v-icon>mdi-delete-sweep</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- 主要內容區域 -->
    <div class="main-content">
      <div class="resizable-layout">
        <!-- 左側聊天歷史列表 -->
        <div class="chat-history-sidebar" :style="{ width: sidebarWidth + 'px' }">
          <div class="sidebar-header">
            <span class="sidebar-title">對話記錄</span>
            <v-btn
              icon
              size="small"
              @click="createNewSession"
              color="primary"
              class="new-chat-btn"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </div>
          
          <v-divider></v-divider>
          
          <!-- 會話列表 -->
          <div class="session-list-container">
            <v-list class="session-list pa-0">
              <v-list-item
                v-for="session in sessions"
                :key="session.session_id"
                :active="currentSessionId === session.session_id"
                @click="selectSession(session.session_id)"
                class="session-item"
              >
                <v-list-item-title class="text-truncate">
                  {{ session.title || '新對話' }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ formatDate(session.updated_at) }}
                </v-list-item-subtitle>
                
                <template v-slot:append>
                  <v-menu>
                    <template v-slot:activator="{ props }">
                      <v-btn
                        icon
                        size="x-small"
                        variant="text"
                        v-bind="props"
                        @click.stop
                      >
                        <v-icon>mdi-dots-vertical</v-icon>
                      </v-btn>
                    </template>
                    <v-list>
                      <v-list-item @click="editSessionTitle(session)">
                        <v-list-item-title>重新命名</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="deleteSession(session.session_id)">
                        <v-list-item-title class="text-error">刪除</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </template>
              </v-list-item>
            </v-list>
          </div>
        </div>

        <!-- 可拖拽的分隔器 -->
        <div 
          class="resizer" 
          @mousedown="startResize"
          :class="{ 'resizing': isResizing }"
        >
          <div class="resizer-line"></div>
        </div>

        <!-- 右側聊天區域 -->
        <div class="chat-area" :style="{ width: 'calc(100% - ' + (sidebarWidth + 4) + 'px)' }">
          <!-- 訊息列表區域 -->
          <div class="messages-container" ref="messagesContainer">
            <div class="messages-content">
              <!-- 歡迎訊息 -->
              <div v-if="!currentSession" class="welcome-message text-center py-8">
                <v-icon size="64" color="primary" class="mb-4">mdi-robot</v-icon>
                <h3 class="text-h5 mb-2">{{ chatLink?.name || '聊天機器人' }}</h3>
                <p class="text-body-1 text-grey">{{ chatLink?.description || '選擇或建立一個對話開始聊天' }}</p>
              </div>

              <!-- 訊息列表 -->
              <div v-else class="messages-list">
                <div v-for="message in messages" :key="message.id" class="message-item mb-4">
                  <!-- 使用者訊息 -->
                  <div v-if="message.message_type === 'user'" class="user-message d-flex justify-end">
                    <div class="message-bubble user-bubble">
                      <div class="message-content">{{ message.content }}</div>
                      <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                    </div>
                  </div>

                  <!-- AI 回應 -->
                  <div v-else class="ai-message d-flex justify-start">
                    <v-avatar size="32" color="primary" class="mr-3 mt-1">
                      <v-icon color="white">mdi-robot</v-icon>
                    </v-avatar>
                    <div class="message-bubble ai-bubble">
                      <div class="message-content">{{ message.content }}</div>
                      <div class="message-time">
                        {{ formatTime(message.timestamp) }}
                        <span v-if="message.processing_time" class="processing-time">
                          ({{ message.processing_time }}ms)
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 載入中指示器 -->
                <div v-if="isLoading" class="ai-message d-flex justify-start">
                  <v-avatar size="32" color="primary" class="mr-3 mt-1">
                    <v-icon color="white">mdi-robot</v-icon>
                  </v-avatar>
                  <div class="message-bubble ai-bubble">
                    <div class="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 固定在底部的輸入區域 -->
          <div class="input-area-fixed" v-if="currentSession" :style="{ width: 'calc(100% - ' + (sidebarWidth + 4) + 'px)' }">
            <div class="input-container">
              <v-row no-gutters align="center">
                <v-col>
                  <v-textarea
                    v-model="newMessage"
                    placeholder="輸入您的訊息..."
                    variant="outlined"
                    density="compact"
                    rows="1"
                    auto-grow
                    max-rows="4"
                    hide-details
                    @keydown.enter.exact.prevent="sendMessage"
                    @keydown.enter.shift.exact="newMessage += '\n'"
                    :disabled="isLoading"
                    class="message-input"
                  ></v-textarea>
                </v-col>
                <v-col cols="auto" class="ml-2">
                  <v-btn
                    icon
                    color="primary"
                    :disabled="!newMessage.trim() || isLoading"
                    @click="sendMessage"
                    size="large"
                  >
                    <v-icon>mdi-send</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 編輯會話標題對話框 -->
    <v-dialog v-model="editTitleDialog.show" max-width="400">
      <v-card>
        <v-card-title>重新命名對話</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="editTitleDialog.title"
            label="對話標題"
            variant="outlined"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="editTitleDialog.show = false">取消</v-btn>
          <v-btn color="primary" @click="updateSessionTitle">儲存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 確認清除對話框 -->
    <v-dialog v-model="clearDialog" max-width="400">
      <v-card>
        <v-card-title>清除對話</v-card-title>
        <v-card-text>
          確定要清除當前對話的所有訊息嗎？此操作無法復原。
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="clearDialog = false">
            取消
          </v-btn>
          <v-btn color="error" variant="text" @click="confirmClearSession">
            確定清除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

export default {
  name: 'WebhookChatInterface',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const chatLink = ref(null)
    const sessions = ref([])
    const currentSession = ref(null)
    const currentSessionId = ref(null)
    const messages = ref([])
    const newMessage = ref('')
    const isLoading = ref(false)
    const clearDialog = ref(false)
    const messagesContainer = ref(null)

    // 分隔器拖拽相關狀態
    const sidebarWidth = ref(300) // 預設左側寬度 300px
    const isResizing = ref(false)
    const minSidebarWidth = 200 // 最小寬度
    const maxSidebarWidth = 600 // 最大寬度

    // 從 localStorage 載入使用者偏好的側邊欄寬度
    const loadSidebarWidth = () => {
      const savedWidth = localStorage.getItem('webhook-chat-sidebar-width')
      if (savedWidth) {
        const width = parseInt(savedWidth)
        if (width >= minSidebarWidth && width <= maxSidebarWidth) {
          sidebarWidth.value = width
        }
      }
    }

    // 儲存側邊欄寬度到 localStorage
    const saveSidebarWidth = () => {
      localStorage.setItem('webhook-chat-sidebar-width', sidebarWidth.value.toString())
    }

    const editTitleDialog = reactive({
      show: false,
      sessionId: null,
      title: ''
    })

    // 格式化時間
    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('zh-TW', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }

    // 格式化日期
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 1) {
        return '今天'
      } else if (diffDays === 2) {
        return '昨天'
      } else if (diffDays <= 7) {
        return `${diffDays} 天前`
      } else {
        return date.toLocaleDateString('zh-TW')
      }
    }

    // 滾動到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }

    // 開始拖拽調整分隔器
    const startResize = (e) => {
      isResizing.value = true
      document.addEventListener('mousemove', handleResize)
      document.addEventListener('mouseup', stopResize)
      e.preventDefault()
    }

    // 處理拖拽調整
    const handleResize = (e) => {
      if (!isResizing.value) return
      
      const newWidth = e.clientX
      
      // 限制寬度範圍
      if (newWidth >= minSidebarWidth && newWidth <= maxSidebarWidth) {
        sidebarWidth.value = newWidth
      }
    }

    // 停止拖拽調整
    const stopResize = () => {
      isResizing.value = false
      document.removeEventListener('mousemove', handleResize)
      document.removeEventListener('mouseup', stopResize)
      saveSidebarWidth() // 儲存使用者偏好設定
    }

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
          
          // 確認是 webhook 類型
          if (chatLink.value.link_type !== 'n8n_webhook') {
            console.error('此連結不是 webhook 類型')
            router.push('/user-dashboard')
            return
          }

          // 載入會話列表
          await loadSessions()
        } else {
          throw new Error('無法獲取聊天連結資訊')
        }
      } catch (error) {
        console.error('獲取聊天連結失敗:', error)
        router.push('/user-dashboard')
      }
    }

    // 載入會話列表
    const loadSessions = async () => {
      try {
        const response = await axios.get('/api/chat/sessions')
        if (response.data.sessions) {
          // 只顯示當前聊天連結的會話
          sessions.value = response.data.sessions.filter(
            session => session.chat_link_id === chatLink.value.id
          )
        }
      } catch (error) {
        console.error('載入會話列表失敗:', error)
      }
    }

    // 建立新會話
    const createNewSession = async () => {
      if (!chatLink.value) return

      try {
        const response = await axios.post('/api/chat/sessions', {
          chat_link_id: chatLink.value.id,
          title: null
        })
        
        if (response.data) {
          await loadSessions()
          await selectSession(response.data.session_id)
        }
      } catch (error) {
        console.error('建立會話失敗:', error)
      }
    }

    // 選擇會話
    const selectSession = async (sessionId) => {
      try {
        currentSessionId.value = sessionId
        const response = await axios.get(`/api/chat/sessions/${sessionId}`)
        
        if (response.data) {
          currentSession.value = response.data
          messages.value = response.data.messages || []
          await nextTick()
          scrollToBottom()
        }
      } catch (error) {
        console.error('載入會話詳情失敗:', error)
      }
    }

    // 發送訊息
    const sendMessage = async () => {
      if (!newMessage.value.trim() || !currentSessionId.value || isLoading.value) {
        return
      }

      const content = newMessage.value.trim()
      newMessage.value = ''
      isLoading.value = true

      try {
        const response = await axios.post(`/api/chat/sessions/${currentSessionId.value}/messages`, {
          session_id: currentSessionId.value,
          content: content
        })
        
        if (response.data.success) {
          messages.value.push(response.data.user_message)
          messages.value.push(response.data.ai_message)
        } else {
          messages.value.push(response.data.user_message)
          if (response.data.ai_message) {
            messages.value.push(response.data.ai_message)
          }
        }
        
        await nextTick()
        scrollToBottom()
        
        // 重新載入會話列表以更新時間
        await loadSessions()
      } catch (error) {
        console.error('發送訊息失敗:', error)
      } finally {
        isLoading.value = false
      }
    }

    // 編輯會話標題
    const editSessionTitle = (session) => {
      editTitleDialog.sessionId = session.session_id
      editTitleDialog.title = session.title
      editTitleDialog.show = true
    }

    // 更新會話標題
    const updateSessionTitle = async () => {
      try {
        await axios.put(`/api/chat/sessions/${editTitleDialog.sessionId}`, {
          title: editTitleDialog.title
        })
        
        await loadSessions()
        
        if (currentSession.value && currentSession.value.session_id === editTitleDialog.sessionId) {
          currentSession.value.title = editTitleDialog.title
        }
        
        editTitleDialog.show = false
      } catch (error) {
        console.error('更新會話標題失敗:', error)
      }
    }

    // 刪除會話
    const deleteSession = async (sessionId) => {
      if (!confirm('確定要刪除這個對話嗎？此操作無法復原。')) {
        return
      }

      try {
        await axios.delete(`/api/chat/sessions/${sessionId}`)
        
        await loadSessions()
        
        if (currentSessionId.value === sessionId) {
          currentSessionId.value = null
          currentSession.value = null
          messages.value = []
        }
      } catch (error) {
        console.error('刪除會話失敗:', error)
      }
    }

    // 清除當前會話
    const clearCurrentSession = () => {
      clearDialog.value = true
    }

    // 確認清除會話
    const confirmClearSession = async () => {
      if (currentSessionId.value) {
        await deleteSession(currentSessionId.value)
      }
      clearDialog.value = false
    }

    onMounted(() => {
      loadSidebarWidth() // 載入使用者偏好的側邊欄寬度
      fetchChatLink()
    })

    return {
      chatLink,
      sessions,
      currentSession,
      currentSessionId,
      messages,
      newMessage,
      isLoading,
      clearDialog,
      messagesContainer,
      editTitleDialog,
      sidebarWidth,
      isResizing,
      formatTime,
      formatDate,
      startResize,
      goBack,
      createNewSession,
      selectSession,
      sendMessage,
      editSessionTitle,
      updateSessionTitle,
      deleteSession,
      clearCurrentSession,
      confirmClearSession
    }
  }
}
</script>

<style scoped>
.webhook-chat-container {
  height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.chat-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  border-bottom: 1px solid #e0e0e0;
}

.main-content {
  flex: 1;
  margin-top: 64px; /* 為頂部標題欄留出空間 */
  height: calc(100vh - 64px);
  overflow: hidden;
}

.resizable-layout {
  display: flex;
  height: 100%;
  width: 100%;
}

.chat-history-sidebar {
  background-color: #fafafa;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-width: 200px;
  max-width: 600px;
}

/* 可拖拽的分隔器 */
.resizer {
  width: 4px;
  background-color: #e0e0e0;
  cursor: col-resize;
  position: relative;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resizer:hover,
.resizer.resizing {
  background-color: #1976d2;
}

.resizer-line {
  width: 1px;
  height: 40px;
  background-color: #bbb;
  transition: background-color 0.2s ease;
}

.resizer:hover .resizer-line,
.resizer.resizing .resizer-line {
  background-color: white;
}

/* 防止拖拽時選中文字 */
.resizer.resizing {
  user-select: none;
}

.resizing * {
  user-select: none !important;
  pointer-events: none !important;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #e0e0e0;
}

.sidebar-title {
  font-weight: 500;
  font-size: 1.1rem;
}

.new-chat-btn {
  flex-shrink: 0;
}

.session-list-container {
  flex: 1;
  overflow-y: auto;
}

.session-list {
  height: 100%;
}

.session-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.chat-area {
  background-color: white;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  background: linear-gradient(to bottom, #f5f5f5, #fafafa);
  padding-bottom: 120px; /* 為底部輸入框留出空間 */
}

.messages-content {
  padding: 16px;
  min-height: 100%;
}

.messages-list {
  padding-bottom: 20px;
}

.message-item {
  max-width: 100%;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
}

.user-bubble {
  background-color: #1976d2;
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-bubble {
  background-color: white;
  color: #333;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.message-content {
  line-height: 1.4;
  white-space: pre-wrap;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
}

.processing-time {
  font-style: italic;
}

.input-area-fixed {
  position: fixed;
  bottom: 0;
  right: 0;
  background-color: white;
  border-top: 1px solid #e0e0e0;
  z-index: 999;
}

.input-container {
  padding: 16px;
}

.message-input {
  border-radius: 24px;
}

.welcome-message {
  color: #666;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
}

/* 載入動畫 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #999;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 滾動條樣式 */
.session-list::-webkit-scrollbar,
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.session-list::-webkit-scrollbar-track,
.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.session-list::-webkit-scrollbar-thumb,
.messages-container::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.session-list::-webkit-scrollbar-thumb:hover,
.messages-container::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style> 