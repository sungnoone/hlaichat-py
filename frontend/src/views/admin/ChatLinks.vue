<template>
  <AdminLayout>
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between mb-6">
          <h1 class="text-h4">聊天連結管理</h1>
          <v-btn color="primary" prepend-icon="mdi-link-plus" @click="openCreateDialog">
            新增連結
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- 搜尋與過濾 -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="search"
              label="搜尋聊天連結"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              class="mb-3 mb-md-0"
              @keyup.enter="fetchChatLinks"
            ></v-text-field>
          </v-col>
          <v-col cols="6" md="4">
            <v-select
              v-model="filter.type"
              label="類型"
              :items="[
                { value: '', title: '所有類型' },
                { value: 'n8n_host_chat', title: 'n8n Host Chat' },
                { value: 'n8n_embedded_chat', title: 'n8n Embedded Chat' },
                { value: 'n8n_webhook', title: 'n8n Webhook' }
              ]"
              item-title="title"
              item-value="value"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="fetchChatLinks"
            ></v-select>
          </v-col>
          <v-col cols="6" md="2">
            <v-btn color="primary" variant="tonal" block @click="fetchChatLinks">
              搜尋
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 聊天連結列表 -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="chatLinks"
        :loading="loading"
        :items-per-page="10"
        class="elevation-1"
      >
        <!-- 類型欄 -->
        <template v-slot:item.link_type="{ item }">
          <v-chip
            :color="getLinkTypeColor(item.link_type)"
            size="small"
          >
            {{ getLinkTypeLabel(item.link_type) }}
          </v-chip>
        </template>

        <!-- 可使用群組欄 -->
        <template v-slot:item.groups="{ item }">
          <v-chip
            v-for="group in item.groups"
            :key="group.id"
            color="info"
            size="small"
            class="mr-1 mb-1"
            variant="outlined"
          >
            {{ group.name }}
          </v-chip>
          <span v-if="!item.groups || item.groups.length === 0" class="text-grey">
            無群組
          </span>
        </template>

        <!-- 創建日期欄 -->
        <template v-slot:item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <!-- 操作欄 -->
        <template v-slot:item.actions="{ item }">
          <v-menu>
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-dots-vertical"
                variant="text"
                size="small"
              ></v-btn>
            </template>
            <v-list>
              <v-list-item @click="openEditDialog(item)">
                <v-list-item-title>
                  <v-icon start>mdi-pencil</v-icon>
                  編輯
                </v-list-item-title>
              </v-list-item>
              <v-list-item @click="openGroupsDialog(item)">
                <v-list-item-title>
                  <v-icon start>mdi-account-group</v-icon>
                  管理群組
                </v-list-item-title>
              </v-list-item>
              <v-list-item v-if="item.link_type === 'n8n_host_chat'" @click="openLink(item.url)">
                <v-list-item-title>
                  <v-icon start>mdi-open-in-new</v-icon>
                  開啟連結
                </v-list-item-title>
              </v-list-item>
              <v-list-item v-if="item.link_type === 'n8n_embedded_chat'" @click="viewEmbedCode(item)">
                <v-list-item-title>
                  <v-icon start>mdi-code-tags</v-icon>
                  查看嵌入代碼
                </v-list-item-title>
              </v-list-item>
              <v-list-item v-if="item.link_type === 'n8n_webhook'" @click="openChatInterface(item)">
                <v-list-item-title>
                  <v-icon start>mdi-chat</v-icon>
                  開啟聊天介面
                </v-list-item-title>
              </v-list-item>
              <v-divider></v-divider>
              <v-list-item @click="confirmDelete(item)" class="text-error">
                <v-list-item-title>
                  <v-icon start>mdi-delete</v-icon>
                  刪除
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-data-table>

      <!-- 分頁 -->
      <div class="d-flex justify-center pt-4 pb-3">
        <v-pagination
          v-model="pagination.page"
          :length="pagination.totalPages"
          :total-visible="7"
          @update:model-value="fetchChatLinks"
        ></v-pagination>
      </div>
    </v-card>

    <!-- 新增/編輯聊天連結對話框 -->
    <v-dialog v-model="linkDialog.show" max-width="700px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          {{ linkDialog.isEdit ? '編輯聊天連結' : '新增聊天連結' }}
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="linkDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-form ref="linkForm" @submit.prevent="saveChatLink">
            <v-text-field
              v-model="linkDialog.data.name"
              label="連結名稱"
              :rules="[v => !!v || '請輸入連結名稱']"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-textarea
              v-model="linkDialog.data.description"
              label="連結描述"
              variant="outlined"
              auto-grow
              class="mb-3"
            ></v-textarea>

            <v-radio-group
              v-model="linkDialog.data.link_type"
              label="連結類型"
              class="mb-3"
            >
              <v-radio value="n8n_host_chat" label="n8n Host Chat (完整網址)"></v-radio>
              <v-radio value="n8n_embedded_chat" label="n8n Embedded Chat (嵌入代碼)"></v-radio>
              <v-radio value="n8n_webhook" label="n8n Webhook (API 端點)"></v-radio>
            </v-radio-group>

            <v-text-field
              v-if="linkDialog.data.link_type === 'n8n_host_chat'"
              v-model="linkDialog.data.url"
              label="n8n Host Chat URL"
              :rules="[v => !!v || '請輸入 n8n Host Chat URL']"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-textarea
              v-if="linkDialog.data.link_type === 'n8n_embedded_chat'"
              v-model="linkDialog.data.embed_code"
              label="n8n Embedded Chat 嵌入代碼"
              :rules="[v => !!v || '請輸入嵌入代碼']"
              variant="outlined"
              auto-grow
              rows="8"
              class="mb-3"
            ></v-textarea>

            <div v-if="linkDialog.data.link_type === 'n8n_webhook'">
              <v-text-field
                v-model="linkDialog.data.webhook_url"
                label="n8n Webhook URL"
                :rules="[v => !!v || '請輸入 n8n Webhook URL']"
                variant="outlined"
                class="mb-3"
              ></v-text-field>

              <v-select
                v-model="linkDialog.data.credential_id"
                label="選擇 API Key 憑證"
                :items="credentials"
                item-title="name"
                item-value="id"
                variant="outlined"
                class="mb-3"
                clearable
              >
                <template v-slot:no-data>
                  <v-list-item>
                    <v-list-item-title>
                      尚無可用的憑證，請先到憑證管理新增
                    </v-list-item-title>
                  </v-list-item>
                </template>
              </v-select>
            </div>

            <v-divider class="mb-3"></v-divider>
            <div class="text-subtitle-1 mb-2">可使用群組</div>

            <v-select
              v-model="linkDialog.data.group_ids"
              label="選擇可使用的群組"
              :items="groups"
              item-title="name"
              item-value="id"
              multiple
              chips
              closable-chips
              variant="outlined"
              class="mb-3"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions class="pb-4 px-4">
          <v-spacer></v-spacer>
          <v-btn color="error" variant="text" @click="linkDialog.show = false">
            取消
          </v-btn>
          <v-btn color="primary" @click="saveChatLink" :loading="linkDialog.loading">
            儲存
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 管理群組對話框 -->
    <v-dialog v-model="groupsDialog.show" max-width="600px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          管理可使用群組
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="groupsDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <p class="mb-4">為「{{ groupsDialog.linkName }}」選擇可使用的群組：</p>

          <v-sheet max-height="300px" class="overflow-y-auto">
            <v-checkbox
              v-for="group in groups"
              :key="group.id"
              v-model="groupsDialog.selectedGroups"
              :label="group.name"
              :value="group.id"
              hide-details
              class="mb-2"
            ></v-checkbox>
          </v-sheet>
        </v-card-text>
        <v-card-actions class="pb-4 px-4">
          <v-spacer></v-spacer>
          <v-btn color="error" variant="text" @click="groupsDialog.show = false">
            取消
          </v-btn>
          <v-btn color="primary" @click="updateChatLinkGroups" :loading="groupsDialog.loading">
            儲存群組設定
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 查看嵌入代碼對話框 -->
    <v-dialog v-model="embedDialog.show" max-width="700px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          查看嵌入代碼
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="embedDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-alert type="info" density="compact" class="mb-3">
            您可以複製以下代碼並嵌入到您的網頁中。
          </v-alert>
          <v-textarea
            v-model="embedDialog.code"
            readonly
            auto-grow
            variant="outlined"
            rows="8"
            label="嵌入代碼"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="copyEmbedCode">
            <v-icon start>mdi-content-copy</v-icon>
            複製代碼
          </v-btn>
          <v-btn color="grey" variant="text" @click="embedDialog.show = false">
            關閉
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 刪除確認對話框 -->
    <v-dialog v-model="deleteDialog.show" max-width="500">
      <v-card>
        <v-card-title class="bg-error text-white">
          刪除聊天連結
        </v-card-title>
        <v-card-text class="pt-4">
          <p>確定要刪除聊天連結「{{ deleteDialog.name }}」嗎？</p>
          <p class="text-caption text-grey">此操作無法復原。</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="deleteDialog.show = false">
            取消
          </v-btn>
          <v-btn color="error" variant="flat" @click="deleteChatLink" :loading="deleteDialog.loading">
            刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 複製成功提示 -->
    <v-snackbar v-model="copySuccess" :timeout="2000" color="success">
      已複製到剪貼簿
    </v-snackbar>

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
import { ref, reactive, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from 'axios'
import { credentialApi } from '@/services/api'

export default {
  name: 'ChatLinks',
  components: {
    AdminLayout
  },
  setup() {
    const chatLinks = ref([])
    const groups = ref([])
    const credentials = ref([])
    const loading = ref(false)
    const copySuccess = ref(false)
    const search = ref('')
    const filter = reactive({
      type: ''
    })
    const pagination = reactive({
      page: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 10
    })
    
    // 表格欄位定義
    const headers = ref([
      { title: '連結名稱', key: 'name' },
      { title: '描述', key: 'description' },
      { title: '類型', key: 'link_type' },
      { title: '可使用群組', key: 'groups' },
      { title: '建立日期', key: 'created_at' },
      { title: '操作', key: 'actions', sortable: false, align: 'end' }
    ])
    
    // 新增/編輯聊天連結對話框
    const linkDialog = reactive({
      show: false,
      isEdit: false,
      loading: false,
      data: {
        id: null,
        name: '',
        description: '',
        link_type: 'n8n_host_chat',
        url: '',
        embed_code: '',
        webhook_url: '',
        credential_id: null,
        group_ids: []
      }
    })
    
    // 管理群組對話框
    const groupsDialog = reactive({
      show: false,
      linkId: null,
      linkName: '',
      selectedGroups: [],
      loading: false
    })
    
    // 查看嵌入代碼對話框
    const embedDialog = reactive({
      show: false,
      code: ''
    })
    
    // 刪除確認對話框
    const deleteDialog = reactive({
      show: false,
      id: null,
      name: '',
      loading: false
    })
    
    // 提示訊息
    const snackbar = reactive({
      show: false,
      text: '',
      color: 'success'
    })
    
    // 表單引用
    const linkForm = ref(null)
    
    // 格式化日期
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-TW')
    }
    
    // 取得連結類型顏色
    const getLinkTypeColor = (linkType) => {
      switch (linkType) {
        case 'n8n_host_chat':
          return 'primary'
        case 'n8n_embedded_chat':
          return 'secondary'
        case 'n8n_webhook':
          return 'success'
        case 'flowise_chat':
          return 'info'
        default:
          return 'grey'
      }
    }
    
    // 取得連結類型標籤
    const getLinkTypeLabel = (linkType) => {
      switch (linkType) {
        case 'n8n_host_chat':
          return 'n8n Host Chat'
        case 'n8n_embedded_chat':
          return 'n8n Embedded Chat'
        case 'n8n_webhook':
          return 'n8n Webhook'
        case 'flowise_chat':
          return 'Flowise Chat'
        default:
          return linkType
      }
    }
    
    // 獲取聊天連結列表
    const fetchChatLinks = async (page = pagination.page) => {
      loading.value = true
      pagination.page = page
      
      try {
        const params = {
          page: pagination.page,
          page_size: pagination.itemsPerPage,
          name: search.value || undefined
        }
        
        if (filter.type) {
          params.link_type = filter.type
        }
        
        const response = await axios.get('/api/chat-links/admin', { params })
        
        if (response.data.success) {
          chatLinks.value = response.data.items
          pagination.totalPages = response.data.total_pages
          pagination.totalItems = response.data.total
        }
      } catch (error) {
        console.error('獲取聊天連結失敗:', error)
        showSnackbar('獲取聊天連結失敗', 'error')
      } finally {
        loading.value = false
      }
    }
    
    // 獲取群組列表
    const fetchGroups = async () => {
      try {
        const response = await axios.get('/api/groups')
        if (response.data.success) {
          groups.value = response.data.items
        }
      } catch (error) {
        console.error('獲取群組失敗:', error)
      }
    }
    
    // 獲取憑證列表
    const fetchCredentials = async () => {
      try {
        const response = await credentialApi.getAllCredentials()
        credentials.value = response
      } catch (error) {
        console.error('獲取憑證失敗:', error)
      }
    }
    
    // 開啟聊天連結
    const openLink = (url) => {
      window.open(url, '_blank')
    }
    
    // 查看嵌入代碼
    const viewEmbedCode = (item) => {
      embedDialog.code = item.embed_code
      embedDialog.show = true
    }
    
    // 複製嵌入代碼
    const copyEmbedCode = () => {
      navigator.clipboard.writeText(embedDialog.code)
        .then(() => {
          copySuccess.value = true
        })
        .catch(error => {
          console.error('複製失敗:', error)
        })
    }
    
    // 開啟聊天介面 (針對 webhook 類型)
    const openChatInterface = (item) => {
      // 導向到聊天介面，並傳遞聊天連結 ID
      window.open(`/chat?link_id=${item.id}`, '_blank')
    }
    
    // 開啟新增聊天連結對話框
    const openCreateDialog = () => {
      linkDialog.isEdit = false
      linkDialog.data = {
        id: null,
        name: '',
        description: '',
        link_type: 'n8n_host_chat',
        url: '',
        embed_code: '',
        webhook_url: '',
        credential_id: null,
        group_ids: []
      }
      linkDialog.show = true
    }
    
    // 開啟編輯聊天連結對話框
    const openEditDialog = (item) => {
      linkDialog.isEdit = true
      linkDialog.data = {
        id: item.id,
        name: item.name,
        description: item.description || '',
        link_type: item.link_type,
        url: item.url || '',
        embed_code: item.embed_code || '',
        webhook_url: item.webhook_url || '',
        credential_id: item.credential_id || null,
        group_ids: item.groups ? item.groups.map(g => g.id) : []
      }
      linkDialog.show = true
    }
    
    // 開啟管理群組對話框
    const openGroupsDialog = (item) => {
      groupsDialog.linkId = item.id
      groupsDialog.linkName = item.name
      groupsDialog.selectedGroups = item.groups ? item.groups.map(g => g.id) : []
      groupsDialog.show = true
    }
    
    // 確認刪除對話框
    const confirmDelete = (item) => {
      deleteDialog.id = item.id
      deleteDialog.name = item.name
      deleteDialog.show = true
    }
    
    // 儲存聊天連結
    const saveChatLink = async () => {
      const { valid } = await linkForm.value.validate()
      
      if (!valid) return
      
      linkDialog.loading = true
      
      try {
        let response
        const data = {
          name: linkDialog.data.name,
          description: linkDialog.data.description,
          link_type: linkDialog.data.link_type,
          group_ids: linkDialog.data.group_ids
        }
        
        // 根據類型加入對應的字段
        if (linkDialog.data.link_type === 'n8n_host_chat') {
          data.url = linkDialog.data.url
        } else if (linkDialog.data.link_type === 'n8n_embedded_chat') {
          data.embed_code = linkDialog.data.embed_code
        } else if (linkDialog.data.link_type === 'n8n_webhook') {
          data.webhook_url = linkDialog.data.webhook_url
          data.credential_id = linkDialog.data.credential_id
        }
        
        if (linkDialog.isEdit) {
          // 編輯聊天連結
          response = await axios.put(`/api/chat-links/${linkDialog.data.id}`, data)
        } else {
          // 新增聊天連結
          response = await axios.post('/api/chat-links', data)
        }
        
        if (response.data.success) {
          linkDialog.show = false
          fetchChatLinks()
          showSnackbar(linkDialog.isEdit ? '聊天連結更新成功' : '聊天連結建立成功')
        }
      } catch (error) {
        console.error('儲存聊天連結失敗:', error)
        showSnackbar(error.response?.data?.detail || '儲存聊天連結失敗', 'error')
      } finally {
        linkDialog.loading = false
      }
    }
    
    // 更新聊天連結可使用群組
    const updateChatLinkGroups = async () => {
      groupsDialog.loading = true
      
      try {
        const response = await axios.put(`/api/chat-links/${groupsDialog.linkId}`, {
          group_ids: groupsDialog.selectedGroups
        })
        
        if (response.data.success) {
          groupsDialog.show = false
          fetchChatLinks()
          showSnackbar('可使用群組更新成功')
        }
      } catch (error) {
        console.error('更新可使用群組失敗:', error)
        showSnackbar(error.response?.data?.detail || '更新可使用群組失敗', 'error')
      } finally {
        groupsDialog.loading = false
      }
    }
    
    // 刪除聊天連結
    const deleteChatLink = async () => {
      deleteDialog.loading = true
      
      try {
        const response = await axios.delete(`/api/chat-links/${deleteDialog.id}`)
        
        if (response.data.success) {
          deleteDialog.show = false
          fetchChatLinks()
          showSnackbar('聊天連結已刪除')
        }
      } catch (error) {
        console.error('刪除聊天連結失敗:', error)
        showSnackbar(error.response?.data?.detail || '刪除聊天連結失敗', 'error')
      } finally {
        deleteDialog.loading = false
      }
    }
    
    // 顯示提示訊息
    const showSnackbar = (text, color = 'success') => {
      snackbar.text = text
      snackbar.color = color
      snackbar.show = true
    }
    
    onMounted(() => {
      fetchChatLinks()
      fetchGroups()
      fetchCredentials()
    })
    
    return {
      chatLinks,
      groups,
      credentials,
      loading,
      copySuccess,
      search,
      filter,
      pagination,
      headers,
      linkDialog,
      groupsDialog,
      embedDialog,
      deleteDialog,
      snackbar,
      linkForm,
      formatDate,
      getLinkTypeColor,
      getLinkTypeLabel,
      fetchChatLinks,
      openLink,
      viewEmbedCode,
      copyEmbedCode,
      openChatInterface,
      openCreateDialog,
      openEditDialog,
      openGroupsDialog,
      confirmDelete,
      saveChatLink,
      updateChatLinkGroups,
      deleteChatLink
    }
  }
}
</script> 