<template>
  <AdminLayout>
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between mb-6">
          <h1 class="text-h4">憑證管理</h1>
          <v-btn color="primary" prepend-icon="mdi-key-variant" @click="openCreateDialog">
            新增憑證
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- 搜尋 -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-text-field
          v-model="search"
          label="搜尋憑證"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          clearable
          @input="debouncedSearch"
        ></v-text-field>
      </v-col>
      <v-col cols="12" md="6">
        <v-btn
          color="secondary"
          variant="outlined"
          @click="resetSearch"
        >
          重置搜尋
        </v-btn>
      </v-col>
    </v-row>

    <!-- 憑證列表 -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-data-table
            :headers="headers"
            :items="credentials"
            :loading="loading"
            :items-per-page="pagination.pageSize"
            hide-default-footer
            class="elevation-1"
          >
            <!-- API Key 欄 -->
            <template v-slot:item.api_key="{ item }">
              <div class="d-flex align-center">
                <span v-if="!item.showKey" class="text-grey">
                  ••••••••••••••••
                </span>
                <span v-else class="font-monospace">
                  {{ item.api_key }}
                </span>
                <v-btn
                  :icon="item.showKey ? 'mdi-eye-off' : 'mdi-eye'"
                  variant="text"
                  size="small"
                  @click="toggleKeyVisibility(item)"
                  class="ml-2"
                ></v-btn>
                <v-btn
                  icon="mdi-content-copy"
                  variant="text"
                  size="small"
                  @click="copyToClipboard(item.api_key)"
                  class="ml-1"
                ></v-btn>
              </div>
            </template>

            <!-- 描述欄 -->
            <template v-slot:item.description="{ item }">
              <span v-if="item.description" class="text-truncate" style="max-width: 200px;">
                {{ item.description }}
              </span>
              <span v-else class="text-grey">
                無描述
              </span>
            </template>

            <!-- 創建日期欄 -->
            <template v-slot:item.created_at="{ item }">
              {{ formatDate(item.created_at) }}
            </template>

            <!-- 更新日期欄 -->
            <template v-slot:item.updated_at="{ item }">
              {{ formatDate(item.updated_at) }}
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
              @update:model-value="fetchCredentials"
            ></v-pagination>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 新增/編輯憑證對話框 -->
    <v-dialog v-model="credentialDialog.show" max-width="600px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          {{ credentialDialog.isEdit ? '編輯憑證' : '新增憑證' }}
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="credentialDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-form ref="credentialForm" @submit.prevent="saveCredential">
            <v-text-field
              v-model="credentialDialog.data.name"
              label="憑證名稱"
              :rules="[v => !!v || '請輸入憑證名稱']"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-text-field
              v-model="credentialDialog.data.api_key"
              label="API Key"
              :type="credentialDialog.showApiKey ? 'text' : 'password'"
              :rules="[v => !!v || '請輸入 API Key']"
              variant="outlined"
              class="mb-3"
            >
              <template v-slot:append-inner>
                <v-btn
                  :icon="credentialDialog.showApiKey ? 'mdi-eye-off' : 'mdi-eye'"
                  variant="text"
                  size="small"
                  @click="credentialDialog.showApiKey = !credentialDialog.showApiKey"
                ></v-btn>
              </template>
            </v-text-field>

            <v-textarea
              v-model="credentialDialog.data.description"
              label="描述"
              variant="outlined"
              auto-grow
              class="mb-3"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions class="pb-4 px-4">
          <v-spacer></v-spacer>
          <v-btn color="error" variant="text" @click="credentialDialog.show = false">
            取消
          </v-btn>
          <v-btn color="primary" @click="saveCredential" :loading="credentialDialog.loading">
            儲存
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 刪除確認對話框 -->
    <v-dialog v-model="deleteDialog.show" max-width="400px">
      <v-card>
        <v-card-title class="bg-error text-white">
          確認刪除
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="deleteDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <p>確定要刪除憑證「{{ deleteDialog.credentialName }}」嗎？</p>
          <p class="text-error">此操作無法復原。</p>
        </v-card-text>
        <v-card-actions class="pb-4 px-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="deleteDialog.show = false">
            取消
          </v-btn>
          <v-btn color="error" @click="deleteCredential" :loading="deleteDialog.loading">
            刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 通知 -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top"
    >
      {{ snackbar.message }}
    </v-snackbar>
  </AdminLayout>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { debounce } from 'lodash-es'
import AdminLayout from '@/components/AdminLayout.vue'
import { credentialApi } from '@/services/api'

export default {
  name: 'Credentials',
  components: {
    AdminLayout
  },
  setup() {
    // 響應式資料
    const loading = ref(false)
    const credentials = ref([])
    const search = ref('')

    // 分頁資料
    const pagination = reactive({
      page: 1,
      pageSize: 10,
      total: 0,
      totalPages: 0
    })

    // 對話框狀態
    const credentialDialog = reactive({
      show: false,
      isEdit: false,
      loading: false,
      showApiKey: false,
      data: {
        name: '',
        api_key: '',
        description: ''
      }
    })

    const deleteDialog = reactive({
      show: false,
      loading: false,
      credentialId: null,
      credentialName: ''
    })

    // 通知
    const snackbar = reactive({
      show: false,
      message: '',
      color: 'success'
    })

    // 表格標題
    const headers = [
      { title: '憑證名稱', key: 'name', sortable: true },
      { title: 'API Key', key: 'api_key', sortable: false },
      { title: '描述', key: 'description', sortable: false },
      { title: '創建時間', key: 'created_at', sortable: true },
      { title: '更新時間', key: 'updated_at', sortable: true },
      { title: '操作', key: 'actions', sortable: false }
    ]

    // 計算屬性
    const debouncedSearch = debounce(() => {
      pagination.page = 1
      fetchCredentials()
    }, 500)

    // 方法
    const fetchCredentials = async () => {
      loading.value = true
      try {
        const params = {
          skip: (pagination.page - 1) * pagination.pageSize,
          limit: pagination.pageSize
        }

        if (search.value) {
          params.search = search.value
        }

        const response = await credentialApi.getCredentials(params)
        
        credentials.value = response.credentials.map(credential => ({
          ...credential,
          showKey: false
        }))
        
        pagination.total = response.total
        pagination.totalPages = Math.ceil(response.total / pagination.pageSize)
      } catch (error) {
        showSnackbar('取得憑證列表失敗', 'error')
        console.error('取得憑證列表失敗:', error)
      } finally {
        loading.value = false
      }
    }

    const openCreateDialog = () => {
      credentialDialog.isEdit = false
      credentialDialog.data = {
        name: '',
        api_key: '',
        description: ''
      }
      credentialDialog.showApiKey = false
      credentialDialog.show = true
    }

    const openEditDialog = (credential) => {
      credentialDialog.isEdit = true
      credentialDialog.data = { ...credential }
      credentialDialog.showApiKey = false
      credentialDialog.show = true
    }

    const saveCredential = async () => {
      credentialDialog.loading = true
      try {
        if (credentialDialog.isEdit) {
          await credentialApi.updateCredential(credentialDialog.data.id, credentialDialog.data)
          showSnackbar('憑證更新成功')
        } else {
          await credentialApi.createCredential(credentialDialog.data)
          showSnackbar('憑證建立成功')
        }
        
        credentialDialog.show = false
        await fetchCredentials()
      } catch (error) {
        showSnackbar(
          credentialDialog.isEdit ? '憑證更新失敗' : '憑證建立失敗',
          'error'
        )
        console.error('儲存憑證失敗:', error)
      } finally {
        credentialDialog.loading = false
      }
    }

    const confirmDelete = (credential) => {
      deleteDialog.credentialId = credential.id
      deleteDialog.credentialName = credential.name
      deleteDialog.show = true
    }

    const deleteCredential = async () => {
      deleteDialog.loading = true
      try {
        await credentialApi.deleteCredential(deleteDialog.credentialId)
        showSnackbar('憑證刪除成功')
        deleteDialog.show = false
        await fetchCredentials()
      } catch (error) {
        showSnackbar('憑證刪除失敗', 'error')
        console.error('刪除憑證失敗:', error)
      } finally {
        deleteDialog.loading = false
      }
    }

    const toggleKeyVisibility = (credential) => {
      credential.showKey = !credential.showKey
    }

    const copyToClipboard = async (text) => {
      try {
        await navigator.clipboard.writeText(text)
        showSnackbar('API Key 已複製到剪貼簿')
      } catch (error) {
        showSnackbar('複製失敗', 'error')
      }
    }

    const resetSearch = () => {
      search.value = ''
      pagination.page = 1
      fetchCredentials()
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const showSnackbar = (message, color = 'success') => {
      snackbar.message = message
      snackbar.color = color
      snackbar.show = true
    }

    // 生命週期
    onMounted(() => {
      fetchCredentials()
    })

    return {
      loading,
      credentials,
      search,
      pagination,
      credentialDialog,
      deleteDialog,
      snackbar,
      headers,
      debouncedSearch,
      fetchCredentials,
      openCreateDialog,
      openEditDialog,
      saveCredential,
      confirmDelete,
      deleteCredential,
      toggleKeyVisibility,
      copyToClipboard,
      resetSearch,
      formatDate
    }
  }
}
</script>

<style scoped>
.font-monospace {
  font-family: 'Courier New', monospace;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
}
</style> 