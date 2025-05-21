<template>
  <AdminLayout>
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between mb-6">
          <h1 class="text-h4">使用者管理</h1>
          <v-btn color="primary" prepend-icon="mdi-account-plus" @click="openCreateDialog">
            新增使用者
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- 搜尋與過濾 -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="搜尋使用者"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              class="mb-3 mb-md-0"
              @keyup.enter="fetchUsers"
            ></v-text-field>
          </v-col>
          <v-col cols="6" md="3">
            <v-select
              v-model="filters.status"
              label="狀態"
              :items="[
                { value: '', title: '所有狀態' },
                { value: true, title: '啟用' },
                { value: false, title: '停用' }
              ]"
              item-title="title"
              item-value="value"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="fetchUsers"
            ></v-select>
          </v-col>
          <v-col cols="6" md="3">
            <v-select
              v-model="filters.type"
              label="類型"
              :items="[
                { value: '', title: '所有類型' },
                { value: 'platform', title: '平台帳號' },
                { value: 'ad', title: 'AD 帳號' }
              ]"
              item-title="title"
              item-value="value"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="fetchUsers"
            ></v-select>
          </v-col>
          <v-col cols="12" md="2">
            <v-btn color="primary" variant="tonal" block @click="fetchUsers">
              搜尋
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 使用者列表 -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="users"
        :loading="loading"
        :items-per-page="10"
        class="elevation-1"
      >
        <!-- 狀態欄 -->
        <template v-slot:item.is_active="{ item }">
          <v-chip
            :color="item.is_active ? 'success' : 'error'"
            size="small"
          >
            {{ item.is_active ? '啟用' : '停用' }}
          </v-chip>
        </template>

        <!-- 類型欄 -->
        <template v-slot:item.is_ad_user="{ item }">
          <v-chip
            :color="item.is_ad_user ? 'info' : 'secondary'"
            size="small"
          >
            {{ item.is_ad_user ? 'AD 帳號' : '平台帳號' }}
          </v-chip>
        </template>

        <!-- 群組欄 -->
        <template v-slot:item.groups="{ item }">
          <v-chip
            v-for="group in item.groups"
            :key="group.id"
            color="primary"
            size="small"
            class="mr-1 mb-1"
            variant="outlined"
          >
            {{ group.name }}
          </v-chip>
        </template>

        <!-- 註冊日期欄 -->
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
              <v-list-item @click="openPasswordDialog(item)">
                <v-list-item-title>
                  <v-icon start>mdi-key</v-icon>
                  修改密碼
                </v-list-item-title>
              </v-list-item>
              <v-list-item @click="openGroupDialog(item)">
                <v-list-item-title>
                  <v-icon start>mdi-account-group</v-icon>
                  管理群組
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
          @update:model-value="fetchUsers"
        ></v-pagination>
      </div>
    </v-card>

    <!-- 新增/編輯使用者對話框 -->
    <v-dialog v-model="userDialog.show" max-width="600px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          {{ userDialog.isEdit ? '編輯使用者' : '新增使用者' }}
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="userDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-form ref="userForm" @submit.prevent="saveUser">
            <v-text-field
              v-model="userDialog.data.username"
              label="使用者名稱"
              :readonly="userDialog.isEdit"
              :rules="[v => !!v || '請輸入使用者名稱']"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-text-field
              v-if="!userDialog.isEdit"
              v-model="userDialog.data.password"
              label="密碼"
              type="password"
              :rules="[v => !!v || '請輸入密碼']"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-text-field
              v-model="userDialog.data.full_name"
              label="姓名"
              :rules="[v => !!v || '請輸入姓名']"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-text-field
              v-model="userDialog.data.email"
              label="電子郵件"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-text-field
              v-model="userDialog.data.phone"
              label="電話"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-text-field
              v-model="userDialog.data.department"
              label="部門"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-switch
              v-model="userDialog.data.is_active"
              label="啟用使用者"
              color="success"
              hide-details
              class="mb-3"
            ></v-switch>

            <v-textarea
              v-model="userDialog.data.notes"
              label="備註"
              variant="outlined"
              auto-grow
              class="mb-3"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions class="pb-4 px-4">
          <v-spacer></v-spacer>
          <v-btn color="error" variant="text" @click="userDialog.show = false">
            取消
          </v-btn>
          <v-btn color="primary" @click="saveUser" :loading="userDialog.loading">
            儲存
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 修改密碼對話框 -->
    <v-dialog v-model="passwordDialog.show" max-width="500px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          修改密碼
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="passwordDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-form ref="passwordForm" @submit.prevent="updatePassword">
            <v-text-field
              v-model="passwordDialog.password"
              label="新密碼"
              type="password"
              :rules="[v => !!v || '請輸入新密碼']"
              variant="outlined"
              class="mb-3"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions class="pb-4 px-4">
          <v-spacer></v-spacer>
          <v-btn color="error" variant="text" @click="passwordDialog.show = false">
            取消
          </v-btn>
          <v-btn color="primary" @click="updatePassword" :loading="passwordDialog.loading">
            更新密碼
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 管理群組對話框 -->
    <v-dialog v-model="groupDialog.show" max-width="600px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          管理使用者群組
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="groupDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <p class="mb-4">為使用者 <strong>{{ groupDialog.username }}</strong> 選擇群組：</p>
          
          <!-- 群組搜尋 -->
          <v-text-field
            v-model="groupDialog.search"
            label="搜尋群組"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="compact"
            class="mb-3"
            hide-details
            clearable
          ></v-text-field>
          
          <!-- 群組列表 -->
          <v-sheet max-height="300px" class="overflow-y-auto">
            <v-list>
              <v-list-item
                v-for="group in filteredGroups"
                :key="group.id"
                :value="group.id"
                density="compact"
                class="px-0"
              >
                <template v-slot:prepend>
                  <v-checkbox
                    v-model="groupDialog.selectedGroups"
                    :value="group.id"
                    hide-details
                    density="compact"
                  ></v-checkbox>
                </template>
                <v-list-item-title class="text-subtitle-2">{{ group.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip
                    v-if="group.can_login"
                    size="x-small"
                    color="success"
                    class="mr-1"
                  >
                    可登入
                  </v-chip>
                  <v-chip
                    v-if="group.can_manage_platform"
                    size="x-small"
                    color="error"
                    class="mr-1"
                  >
                    可管理
                  </v-chip>
                  <v-chip
                    v-if="group.can_use_chat_links"
                    size="x-small"
                    color="info"
                    class="mr-1"
                  >
                    可使用聊天
                  </v-chip>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-sheet>
          
          <!-- 已選擇的群組摘要 -->
          <v-sheet class="mt-4 pa-3 bg-grey-lighten-4 rounded">
            <div class="d-flex align-center mb-2">
              <div class="text-subtitle-2">已選擇的群組 ({{ groupDialog.selectedGroups.length }})</div>
              <v-spacer></v-spacer>
              <v-btn
                v-if="groupDialog.selectedGroups.length > 0"
                size="small"
                variant="text"
                color="error"
                @click="groupDialog.selectedGroups = []"
              >
                清除全部
              </v-btn>
            </div>
            <div v-if="groupDialog.selectedGroups.length === 0" class="text-body-2 text-grey">
              尚未選擇任何群組
            </div>
            <v-chip-group>
              <v-chip
                v-for="groupId in groupDialog.selectedGroups"
                :key="groupId"
                closable
                color="primary"
                size="small"
                @click:close="removeGroupFromSelection(groupId)"
              >
                {{ getGroupNameById(groupId) }}
              </v-chip>
            </v-chip-group>
          </v-sheet>
        </v-card-text>
        <v-card-actions class="pb-4 px-4">
          <v-spacer></v-spacer>
          <v-btn color="error" variant="text" @click="groupDialog.show = false">
            取消
          </v-btn>
          <v-btn color="primary" @click="updateUserGroups" :loading="groupDialog.loading">
            儲存群組設定
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 刪除確認對話框 -->
    <v-dialog v-model="deleteDialog.show" max-width="500">
      <v-card>
        <v-card-title class="bg-error text-white">
          刪除使用者
        </v-card-title>
        <v-card-text class="pt-4">
          <p>確定要刪除使用者 <strong>{{ deleteDialog.username }}</strong> 嗎？</p>
          <p class="text-caption text-grey">此操作無法復原。</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="deleteDialog.show = false">
            取消
          </v-btn>
          <v-btn color="error" variant="flat" @click="deleteUser" :loading="deleteDialog.loading">
            刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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
import { ref, onMounted, reactive, computed } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from 'axios'

export default {
  name: 'Users',
  components: {
    AdminLayout
  },
  setup() {
    const users = ref([])
    const loading = ref(false)
    const search = ref('')
    const filters = reactive({
      status: '',
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
      { title: '使用者名稱', key: 'username' },
      { title: '姓名', key: 'full_name' },
      { title: '狀態', key: 'is_active' },
      { title: '類型', key: 'is_ad_user' },
      { title: '群組', key: 'groups' },
      { title: '建立日期', key: 'created_at' },
      { title: '操作', key: 'actions', sortable: false, align: 'end' }
    ])
    
    // 新增/編輯使用者對話框
    const userDialog = reactive({
      show: false,
      isEdit: false,
      loading: false,
      data: {
        id: null,
        username: '',
        password: '',
        full_name: '',
        email: '',
        phone: '',
        department: '',
        is_active: true,
        notes: '',
        group_ids: []
      }
    })
    
    // 修改密碼對話框
    const passwordDialog = reactive({
      show: false,
      userId: null,
      username: '',
      password: '',
      loading: false
    })
    
    // 管理群組對話框
    const groupDialog = reactive({
      show: false,
      userId: null,
      username: '',
      selectedGroups: [],
      search: '',
      loading: false
    })
    
    // 刪除確認對話框
    const deleteDialog = reactive({
      show: false,
      userId: null,
      username: '',
      loading: false
    })
    
    // 提示訊息
    const snackbar = reactive({
      show: false,
      text: '',
      color: 'success'
    })
    
    // 所有群組列表
    const allGroups = ref([])
    
    // 表單引用
    const userForm = ref(null)
    const passwordForm = ref(null)
    
    // 格式化日期
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-TW')
    }
    
    // 獲取使用者列表
    const fetchUsers = async (page = pagination.page) => {
      loading.value = true
      pagination.page = page
      
      try {
        const params = {
          page: pagination.page,
          page_size: pagination.itemsPerPage,
          search: search.value || undefined
        }
        
        if (filters.status !== '') {
          params.is_active = filters.status
        }
        
        if (filters.type === 'platform') {
          params.is_ad_user = false
        } else if (filters.type === 'ad') {
          params.is_ad_user = true
        }
        
        const response = await axios.get('/api/users', { params })
        
        if (response.data.success) {
          users.value = response.data.items
          pagination.totalPages = response.data.total_pages
          pagination.totalItems = response.data.total
        }
      } catch (error) {
        console.error('獲取使用者失敗:', error)
        showSnackbar('獲取使用者失敗', 'error')
      } finally {
        loading.value = false
      }
    }
    
    // 獲取所有群組
    const fetchGroups = async () => {
      try {
        const response = await axios.get('/api/groups')
        if (response.data.success) {
          allGroups.value = response.data.items
        }
      } catch (error) {
        console.error('獲取群組失敗:', error)
      }
    }
    
    // 開啟新增使用者對話框
    const openCreateDialog = () => {
      userDialog.isEdit = false
      userDialog.data = {
        id: null,
        username: '',
        password: '',
        full_name: '',
        email: '',
        phone: '',
        department: '',
        is_active: true,
        notes: '',
        group_ids: []
      }
      userDialog.show = true
    }
    
    // 開啟編輯使用者對話框
    const openEditDialog = (user) => {
      userDialog.isEdit = true
      userDialog.data = {
        id: user.id,
        username: user.username,
        full_name: user.full_name,
        email: user.email || '',
        phone: user.phone || '',
        department: user.department || '',
        is_active: user.is_active,
        notes: user.notes || '',
        group_ids: user.groups.map(g => g.id)
      }
      userDialog.show = true
    }
    
    // 開啟修改密碼對話框
    const openPasswordDialog = (user) => {
      passwordDialog.userId = user.id
      passwordDialog.username = user.username
      passwordDialog.password = ''
      passwordDialog.show = true
    }
    
    // 開啟管理群組對話框
    const openGroupDialog = (user) => {
      groupDialog.userId = user.id;
      groupDialog.username = user.username;
      groupDialog.selectedGroups = user.groups.map(g => g.id);
      groupDialog.search = '';
      groupDialog.show = true;
    }
    
    // 確認刪除對話框
    const confirmDelete = (user) => {
      deleteDialog.userId = user.id
      deleteDialog.username = user.username
      deleteDialog.show = true
    }
    
    // 儲存使用者
    const saveUser = async () => {
      const { valid } = await userForm.value.validate()
      
      if (!valid) return
      
      userDialog.loading = true
      
      try {
        let response
        
        if (userDialog.isEdit) {
          // 編輯使用者
          response = await axios.put(`/api/users/${userDialog.data.id}`, {
            full_name: userDialog.data.full_name,
            email: userDialog.data.email,
            phone: userDialog.data.phone,
            department: userDialog.data.department,
            is_active: userDialog.data.is_active,
            notes: userDialog.data.notes
          })
        } else {
          // 新增使用者
          response = await axios.post('/api/users', {
            username: userDialog.data.username,
            password: userDialog.data.password,
            full_name: userDialog.data.full_name,
            email: userDialog.data.email,
            phone: userDialog.data.phone,
            department: userDialog.data.department,
            is_active: userDialog.data.is_active,
            notes: userDialog.data.notes
          })
        }
        
        if (response.data.success) {
          userDialog.show = false
          fetchUsers()
          showSnackbar(userDialog.isEdit ? '使用者更新成功' : '使用者建立成功')
        }
      } catch (error) {
        console.error('儲存使用者失敗:', error)
        showSnackbar(error.response?.data?.detail || '儲存使用者失敗', 'error')
      } finally {
        userDialog.loading = false
      }
    }
    
    // 更新密碼
    const updatePassword = async () => {
      const { valid } = await passwordForm.value.validate()
      
      if (!valid) return
      
      passwordDialog.loading = true
      
      try {
        const response = await axios.put(`/api/users/${passwordDialog.userId}/password`, {
          password: passwordDialog.password
        })
        
        if (response.data.success) {
          passwordDialog.show = false
          showSnackbar('密碼更新成功')
        }
      } catch (error) {
        console.error('更新密碼失敗:', error)
        showSnackbar(error.response?.data?.detail || '更新密碼失敗', 'error')
      } finally {
        passwordDialog.loading = false
      }
    }
    
    // 過濾群組列表
    const filteredGroups = computed(() => {
      if (!groupDialog.search) {
        return allGroups.value;
      }
      
      const search = groupDialog.search.toLowerCase();
      return allGroups.value.filter(group => 
        group.name.toLowerCase().includes(search)
      );
    });
    
    // 根據 ID 獲取群組名稱
    const getGroupNameById = (groupId) => {
      const group = allGroups.value.find(g => g.id === groupId);
      return group ? group.name : '未知群組';
    };
    
    // 從選擇中移除群組
    const removeGroupFromSelection = (groupId) => {
      groupDialog.selectedGroups = groupDialog.selectedGroups.filter(id => id !== groupId);
    };
    
    // 更新使用者群組
    const updateUserGroups = async () => {
      groupDialog.loading = true
      
      try {
        const response = await axios.put(`/api/users/${groupDialog.userId}`, {
          group_ids: groupDialog.selectedGroups
        })
        
        if (response.data.success) {
          groupDialog.show = false
          fetchUsers()
          showSnackbar('使用者群組更新成功')
        }
      } catch (error) {
        console.error('更新使用者群組失敗:', error)
        showSnackbar(error.response?.data?.detail || '更新使用者群組失敗', 'error')
      } finally {
        groupDialog.loading = false
      }
    }
    
    // 刪除使用者
    const deleteUser = async () => {
      deleteDialog.loading = true
      
      try {
        const response = await axios.delete(`/api/users/${deleteDialog.userId}`)
        
        if (response.data.success) {
          deleteDialog.show = false
          fetchUsers()
          showSnackbar('使用者已刪除')
        }
      } catch (error) {
        console.error('刪除使用者失敗:', error)
        showSnackbar(error.response?.data?.detail || '刪除使用者失敗', 'error')
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
      fetchUsers()
      fetchGroups()
    })
    
    return {
      users,
      loading,
      search,
      filters,
      pagination,
      headers,
      userDialog,
      passwordDialog,
      groupDialog,
      deleteDialog,
      snackbar,
      allGroups,
      userForm,
      passwordForm,
      formatDate,
      fetchUsers,
      openCreateDialog,
      openEditDialog,
      openPasswordDialog,
      openGroupDialog,
      confirmDelete,
      saveUser,
      updatePassword,
      updateUserGroups,
      deleteUser,
      filteredGroups,
      getGroupNameById,
      removeGroupFromSelection
    }
  }
}
</script>