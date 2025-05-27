<template>
  <v-container fluid class="chat-container pa-0">
    <v-row no-gutters class="fill-height">
      <!-- 左側會話列表 -->
      <v-col cols="3" class="session-sidebar">
        <v-card flat class="fill-height">
          <v-card-title class="d-flex align-center justify-space-between">
            <span>對話記錄</span>
            <v-btn
              icon
              size="small"
              @click="showNewSessionDialog = true"
              :disabled="!selectedChatLink"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </v-card-title>
          
          <!-- 聊天連結選擇 -->
          <v-card-text>
            <v-select
              v-model="selectedChatLink"
              :items="chatLinks"
              item-title="name"
              item-value="id"
              label="選擇聊天機器人"
              variant="outlined"
              density="compact"
              @update:model-value="onChatLinkChange"
            >
              <template v-slot:item="{ props, item }">
                <v-list-item v-bind="props">
                  <v-list-item-title>{{ item.raw.name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ item.raw.description }}</v-list-item-subtitle>
                </v-list-item>
              </template>
            </v-select>
          </v-card-text>
          
          <v-divider></v-divider>
          
          <!-- 會話列表 -->
          <v-list class="session-list">
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
        </v-card>
      </v-col>
      
      <!-- 右側聊天區域 -->
      <v-col cols="9" class="chat-area">
        <v-card flat class="fill-height d-flex flex-column">
          <!-- 聊天標題列 -->
          <v-card-title v-if="currentSession" class="chat-header">
            <div>
              <div class="text-h6">{{ currentSession.title || '新對話' }}</div>
              <div class="text-caption text-medium-emphasis">
                {{ currentSession.chat_link_name }}
              </div>
            </div>
          </v-card-title>
          
          <!-- 訊息區域 -->
          <v-card-text class="flex-grow-1 messages-container" ref="messagesContainer">
            <div v-if="!currentSession" class="empty-state">
              <v-icon size="64" color="grey-lighten-2">mdi-chat-outline</v-icon>
              <p class="text-h6 text-grey-lighten-1 mt-4">選擇或建立一個對話開始聊天</p>
            </div>
            
            <div v-else class="messages-list">
              <div
                v-for="message in currentSession.messages"
                :key="message.id"
                class="message-wrapper"
                :class="message.message_type"
              >
                <div class="message-bubble">
                  <div class="message-content">
                    {{ message.content }}
                  </div>
                  <div class="message-time">
                    {{ formatTime(message.timestamp) }}
                    <span v-if="message.processing_time" class="processing-time">
                      ({{ message.processing_time }}ms)
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- 載入中指示器 -->
              <div v-if="isLoading" class="message-wrapper assistant">
                <div class="message-bubble">
                  <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          </v-card-text>
          
          <!-- 輸入區域 -->
          <v-card-actions class="input-area" v-if="currentSession">
            <v-textarea
              v-model="messageInput"
              placeholder="輸入訊息..."
              variant="outlined"
              rows="1"
              auto-grow
              max-rows="4"
              hide-details
              class="flex-grow-1"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.enter.shift.exact="messageInput += '\n'"
              :disabled="isLoading"
            ></v-textarea>
            <v-btn
              icon
              color="primary"
              @click="sendMessage"
              :disabled="!messageInput.trim() || isLoading"
              class="ml-2"
            >
              <v-icon>mdi-send</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- 新建會話對話框 -->
    <v-dialog v-model="showNewSessionDialog" max-width="400">
      <v-card>
        <v-card-title>建立新對話</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newSessionTitle"
            label="對話標題 (可選)"
            variant="outlined"
            placeholder="留空將自動生成標題"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showNewSessionDialog = false">取消</v-btn>
          <v-btn color="primary" @click="createNewSession">建立</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- 編輯會話標題對話框 -->
    <v-dialog v-model="showEditTitleDialog" max-width="400">
      <v-card>
        <v-card-title>重新命名對話</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="editingTitle"
            label="對話標題"
            variant="outlined"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showEditTitleDialog = false">取消</v-btn>
          <v-btn color="primary" @click="updateSessionTitle">儲存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'ChatInterface',
  setup() {
    const router = useRouter()
    
    // 響應式資料
    const chatLinks = ref([])
    const selectedChatLink = ref(null)
    const sessions = ref([])
    const currentSessionId = ref(null)
    const currentSession = ref(null)
    const messageInput = ref('')
    const isLoading = ref(false)
    
    // 對話框狀態
    const showNewSessionDialog = ref(false)
    const newSessionTitle = ref('')
    const showEditTitleDialog = ref(false)
    const editingTitle = ref('')
    const editingSessionId = ref(null)
    
    // DOM 引用
    const messagesContainer = ref(null)
    
    // 載入可用的聊天連結
    const loadChatLinks = async () => {
      try {
        const response = await axios.get('/api/chat/webhook-links')
        chatLinks.value = response.data
        
        // 如果有可用的聊天連結，預設選擇第一個
        if (chatLinks.value.length > 0) {
          selectedChatLink.value = chatLinks.value[0].id
          await loadSessions()
        }
      } catch (error) {
        console.error('載入聊天連結失敗:', error)
      }
    }
    
    // 載入會話列表
    const loadSessions = async () => {
      try {
        const response = await axios.get('/api/chat/sessions')
        sessions.value = response.data.sessions
      } catch (error) {
        console.error('載入會話列表失敗:', error)
      }
    }
    
    // 選擇會話
    const selectSession = async (sessionId) => {
      try {
        currentSessionId.value = sessionId
        const response = await axios.get(`/api/chat/sessions/${sessionId}`)
        currentSession.value = response.data
        
        // 滾動到底部
        await nextTick()
        scrollToBottom()
      } catch (error) {
        console.error('載入會話詳情失敗:', error)
      }
    }
    
    // 建立新會話
    const createNewSession = async () => {
      if (!selectedChatLink.value) {
        alert('請先選擇聊天機器人')
        return
      }
      
      try {
        const response = await axios.post('/api/chat/sessions', {
          chat_link_id: selectedChatLink.value,
          title: newSessionTitle.value || null
        })
        
        // 重新載入會話列表
        await loadSessions()
        
        // 選擇新建立的會話
        await selectSession(response.data.session_id)
        
        // 重置對話框
        showNewSessionDialog.value = false
        newSessionTitle.value = ''
      } catch (error) {
        console.error('建立會話失敗:', error)
        alert('建立會話失敗: ' + (error.response?.data?.detail || error.message))
      }
    }
    
    // 發送訊息
    const sendMessage = async () => {
      if (!messageInput.value.trim() || !currentSessionId.value || isLoading.value) {
        return
      }
      
      const content = messageInput.value.trim()
      messageInput.value = ''
      isLoading.value = true
      
      try {
        // 使用環境變數中的逾時設定，預設為 5 分鐘
        const chatTimeout = import.meta.env.VITE_CHAT_TIMEOUT || 300000
        const response = await axios.post(`/api/chat/sessions/${currentSessionId.value}/messages`, {
          session_id: currentSessionId.value,
          content: content
        }, {
          timeout: parseInt(chatTimeout)
        })
        
        // 更新當前會話的訊息列表
        if (response.data.success) {
          currentSession.value.messages.push(response.data.user_message)
          currentSession.value.messages.push(response.data.ai_message)
        } else {
          // 處理錯誤情況
          currentSession.value.messages.push(response.data.user_message)
          if (response.data.ai_message) {
            currentSession.value.messages.push(response.data.ai_message)
          }
        }
        
        // 滾動到底部
        await nextTick()
        scrollToBottom()
        
        // 重新載入會話列表以更新時間
        await loadSessions()
      } catch (error) {
        console.error('發送訊息失敗:', error)
        alert('發送訊息失敗: ' + (error.response?.data?.detail || error.message))
      } finally {
        isLoading.value = false
      }
    }
    
    // 編輯會話標題
    const editSessionTitle = (session) => {
      editingSessionId.value = session.session_id
      editingTitle.value = session.title
      showEditTitleDialog.value = true
    }
    
    // 更新會話標題
    const updateSessionTitle = async () => {
      try {
        await axios.put(`/api/chat/sessions/${editingSessionId.value}`, {
          title: editingTitle.value
        })
        
        // 重新載入會話列表
        await loadSessions()
        
        // 如果是當前會話，更新標題
        if (currentSession.value && currentSession.value.session_id === editingSessionId.value) {
          currentSession.value.title = editingTitle.value
        }
        
        showEditTitleDialog.value = false
      } catch (error) {
        console.error('更新會話標題失敗:', error)
        alert('更新會話標題失敗: ' + (error.response?.data?.detail || error.message))
      }
    }
    
    // 刪除會話
    const deleteSession = async (sessionId) => {
      if (!confirm('確定要刪除這個對話嗎？此操作無法復原。')) {
        return
      }
      
      try {
        await axios.delete(`/api/chat/sessions/${sessionId}`)
        
        // 重新載入會話列表
        await loadSessions()
        
        // 如果刪除的是當前會話，清空當前會話
        if (currentSessionId.value === sessionId) {
          currentSessionId.value = null
          currentSession.value = null
        }
      } catch (error) {
        console.error('刪除會話失敗:', error)
        alert('刪除會話失敗: ' + (error.response?.data?.detail || error.message))
      }
    }
    
    // 聊天連結變更
    const onChatLinkChange = async () => {
      currentSessionId.value = null
      currentSession.value = null
      await loadSessions()
    }
    
    // 滾動到底部
    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
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
    
    // 格式化時間
    const formatTime = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleTimeString('zh-TW', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }
    
    // 組件掛載時載入資料
    onMounted(() => {
      loadChatLinks()
    })
    
    return {
      // 資料
      chatLinks,
      selectedChatLink,
      sessions,
      currentSessionId,
      currentSession,
      messageInput,
      isLoading,
      
      // 對話框狀態
      showNewSessionDialog,
      newSessionTitle,
      showEditTitleDialog,
      editingTitle,
      
      // DOM 引用
      messagesContainer,
      
      // 方法
      loadChatLinks,
      loadSessions,
      selectSession,
      createNewSession,
      sendMessage,
      editSessionTitle,
      updateSessionTitle,
      deleteSession,
      onChatLinkChange,
      formatDate,
      formatTime
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 64px); /* 減去導航列高度 */
}

.session-sidebar {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
  background-color: #fafafa;
}

.session-list {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.session-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.chat-area {
  background-color: white;
}

.chat-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  background-color: #f5f5f5;
}

.messages-container {
  overflow-y: auto;
  padding: 16px;
  background: linear-gradient(to bottom, #f8f9fa, #ffffff);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-wrapper {
  display: flex;
  margin-bottom: 8px;
}

.message-wrapper.user {
  justify-content: flex-end;
}

.message-wrapper.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.user .message-bubble {
  background-color: #1976d2;
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant .message-bubble {
  background-color: #f1f3f4;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-content {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
}

.processing-time {
  font-style: italic;
}

.input-area {
  padding: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  background-color: white;
}

/* 打字指示器動畫 */
.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
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
  background: #f1f1f1;
}

.session-list::-webkit-scrollbar-thumb,
.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.session-list::-webkit-scrollbar-thumb:hover,
.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 