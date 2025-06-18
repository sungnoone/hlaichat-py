<template>
  <AdminLayout>
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between mb-6">
          <h1 class="text-h4">群組管理</h1>
          <v-btn color="primary" prepend-icon="mdi-account-group-outline" @click="openCreateDialog">
            新增群組
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- 搜尋欄位 -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-text>
            <v-text-field
              v-model="search"
              label="搜尋群組名稱"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              @input="fetchGroups"
              @click:clear="fetchGroups"
            ></v-text-field>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 群組列表 -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-data-table
            :headers="headers"
            :items="groups"
            :loading="loading"
            :items-per-page="10"
            class="elevation-1"
          >
            <!-- 權限欄 -->
            <template v-slot:item.permissions="{ item }">
              <v-chip
                v-if="item.can_login"
                size="small"
                color="success"
                class="mr-1 mb-1"
              >
                可登入
              </v-chip>
              <v-chip
                v-if="item.can_manage_platform"
                size="small"
                color="error"
                class="mr-1 mb-1"
              >
                可管理
              </v-chip>
              <v-chip
                v-if="item.can_use_chat_links"
                size="small"
                color="info"
                class="mr-1 mb-1"
              >
                可使用聊天
              </v-chip>
            </template>

            <!-- 成員欄 -->
            <template v-slot:item.users="{ item }">
              <span v-if="item.users && item.users.length > 0">
                {{ item.users.length }} 名成員
              </span>
              <span v-else class="text-grey">
                無成員
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
                  <v-list-item @click="openUsersDialog(item)">
                    <v-list-item-title>
                      <v-icon start>mdi-account-multiple</v-icon>
                      管理成員
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
              @update:model-value="fetchGroups"
            ></v-pagination>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 新增/編輯群組對話框 -->
    <v-dialog v-model="groupDialog.show" max-width="600px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          {{ groupDialog.isEdit ? '編輯群組' : '新增群組' }}
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="groupDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-form ref="groupForm" @submit.prevent="saveGroup">
            <v-text-field
              v-model="groupDialog.data.name"
              label="群組名稱"
              :rules="[v => !!v || '請輸入群組名稱']"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-textarea
              v-model="groupDialog.data.description"
              label="群組描述"
              variant="outlined"
              auto-grow
              class="mb-3"
            ></v-textarea>

            <v-divider class="mb-3"></v-divider>
            <div class="text-subtitle-1 mb-2">群組權限</div>

            <v-switch
              v-model="groupDialog.data.can_login"
              label="允許登入平台"
              color="success"
              hide-details
              class="mb-3"
            ></v-switch>

            <v-switch
              v-model="groupDialog.data.can_manage_platform"
              label="允許管理平台 (管理員權限)"
              color="error"
              hide-details
              class="mb-3"
            ></v-switch>

            <v-switch
              v-model="groupDialog.data.can_use_chat_links"
              label="允許使用聊天連結"
              color="info"
              hide-details
              class="mb-4"
            ></v-switch>
          </v-form>
        </v-card-text>
        <v-card-actions class="pb-4 px-4">
          <v-spacer></v-spacer>
          <v-btn color="error" variant="text" @click="groupDialog.show = false">
            取消
          </v-btn>
          <v-btn color="primary" @click="saveGroup" :loading="groupDialog.loading">
            儲存
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 管理成員對話框 -->
    <v-dialog v-model="usersDialog.show" max-width="800px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          管理群組成員
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" color="white" @click="usersDialog.show = false"></v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <p class="mb-4">「{{ usersDialog.groupName }}」群組的成員：</p>

          <!-- 搜尋欄位和統計信息 -->
          <div class="d-flex align-center mb-3">
            <v-text-field
              v-model="usersDialog.search"
              label="搜尋使用者"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              class="mr-3"
              hide-details
              clearable
              style="max-width: 300px"
            ></v-text-field>
            
            <v-chip
              color="primary"
              size="small"
              variant="outlined"
            >
              成員數量：{{ usersDialog.memberIds.length }}
            </v-chip>
          </div>

          <div class="d-flex mb-4 align-center">
            <v-btn-toggle
              v-model="usersDialog.filter"
              density="comfortable"
              color="primary"
            >
              <v-btn value="all">全部</v-btn>
              <v-btn value="members">成員</v-btn>
              <v-btn value="nonmembers">非成員</v-btn>
            </v-btn-toggle>
            
            <v-spacer></v-spacer>
            
            <v-btn
              v-if="usersDialog.filter === 'nonmembers' && getFilteredNonMemberCount() > 0"
              color="success"
              size="small"
              class="ml-2"
              prepend-icon="mdi-account-multiple-plus"
              @click="addAllFilteredUsers"
              :loading="usersDialog.batchLoading"
            >
              加入所有篩選使用者
            </v-btn>
            
            <v-btn
              v-if="usersDialog.filter === 'members' && getFilteredMemberCount() > 0"
              color="error"
              size="small"
              class="ml-2"
              prepend-icon="mdi-account-multiple-remove"
              @click="removeAllFilteredUsers"
              :loading="usersDialog.batchLoading"
            >
              移除所有篩選使用者
            </v-btn>
          </div>

          <!-- 成員列表 -->
          <v-data-table
            :headers="userHeaders"
            :items="displayedUsers"
            :loading="usersDialog.loading"
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

            <!-- 成員狀態欄 -->
            <template v-slot:item.is_member="{ item }">
              <div class="text-center">
                <v-btn
                  :color="item.is_member ? 'error' : 'success'"
                  :icon="item.is_member ? 'mdi-account-remove' : 'mdi-account-plus'"
                  size="small"
                  variant="text"
                  :disabled="usersDialog.loading"
                  @click="toggleUserMembership(item)"
                  :loading="item.isUpdating"
                ></v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions class="pb-4 px-4">
          <v-btn color="secondary" variant="outlined" @click="fetchGroupUsers">
            <v-icon start>mdi-refresh</v-icon>
            重新整理
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="usersDialog.show = false">
            完成
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 刪除確認對話框 -->
    <v-dialog v-model="deleteDialog.show" max-width="500">
      <v-card>
        <v-card-title class="bg-error text-white">
          刪除群組
        </v-card-title>
        <v-card-text class="pt-4">
          <p>確定要刪除群組「{{ deleteDialog.name }}」嗎？</p>
          <p class="text-caption text-grey">此操作會解除所有使用者與此群組的關聯，並且無法復原。</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="deleteDialog.show = false">
            取消
          </v-btn>
          <v-btn color="error" variant="flat" @click="deleteGroup" :loading="deleteDialog.loading">
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
import { ref, reactive, computed, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from 'axios'

export default {
  name: 'Groups',
  components: {
    AdminLayout
  },
  setup() {
    const groups = ref([])
    const allUsers = ref([])
    const loading = ref(false)
    const search = ref('')
    const pagination = reactive({
      page: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 10
    })
    
    // 表格欄位定義
    const headers = ref([
      { title: '群組名稱', key: 'name' },
      { title: '描述', key: 'description' },
      { title: '權限', key: 'permissions' },
      { title: '成員', key: 'users' },
      { title: '建立日期', key: 'created_at' },
      { title: '操作', key: 'actions', sortable: false, align: 'end' }
    ])
    
    const userHeaders = ref([
      { title: '使用者名稱', key: 'username' },
      { title: '姓名', key: 'full_name' },
      { title: '狀態', key: 'is_active' },
      { title: '類型', key: 'is_ad_user' },
      { title: '群組成員', key: 'is_member', align: 'center' }
    ])
    
    // 新增/編輯群組對話框
    const groupDialog = reactive({
      show: false,
      isEdit: false,
      loading: false,
      data: {
        id: null,
        name: '',
        description: '',
        can_login: true,
        can_manage_platform: false,
        can_use_chat_links: true
      }
    })
    
    // 管理成員對話框
    const usersDialog = reactive({
      show: false,
      loading: false,
      batchLoading: false,
      groupId: null,
      groupName: '',
      search: '',
      memberIds: [],
      filter: 'all'
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
    const groupForm = ref(null)
    
    // 計算顯示的使用者列表
    const displayedUsers = computed(() => {
      let users = [...allUsers.value];
      
      // 搜尋過濾
      if (usersDialog.search) {
        const search = usersDialog.search.toLowerCase();
        users = users.filter(user => 
          user.username.toLowerCase().includes(search) || 
          user.full_name.toLowerCase().includes(search)
        );
      }
      
      // 成員狀態過濾
      if (usersDialog.filter === 'members') {
        users = users.filter(user => user.is_member);
      } else if (usersDialog.filter === 'nonmembers') {
        users = users.filter(user => !user.is_member);
      }
      
      return users;
    });
    
    // 獲取過濾後的非成員數量
    const getFilteredNonMemberCount = () => {
      return displayedUsers.value.filter(user => !user.is_member).length;
    };
    
    // 獲取過濾後的成員數量
    const getFilteredMemberCount = () => {
      return displayedUsers.value.filter(user => user.is_member).length;
    };
    
    // 加入所有過濾的使用者
    const addAllFilteredUsers = async () => {
      usersDialog.batchLoading = true;
      
      try {
        const nonMembers = displayedUsers.value.filter(user => !user.is_member);
        
        // 標記所有用戶為成員
        for (const user of nonMembers) {
          user.isUpdating = true;
          user.is_member = true;
        }
        
        // 更新所有使用者
        const userIds = nonMembers.map(user => user.id);
        
        // 批量更新使用者群組
        for (const userId of userIds) {
          const user = allUsers.value.find(u => u.id === userId);
          const currentGroups = user.groups.map(g => g.id);
          
          await axios.put(`/api/users/${userId}`, {
            group_ids: [...currentGroups, usersDialog.groupId]
          });
        }
        
        // 移除標記
        for (const user of nonMembers) {
          user.isUpdating = false;
        }
        
        // 更新成員 ID 列表
        usersDialog.memberIds = [...usersDialog.memberIds, ...userIds];
        
        // 重新獲取群組列表
        fetchGroups();
        
        showSnackbar('批量加入成員成功');
      } catch (error) {
        console.error('批量加入成員失敗:', error);
        showSnackbar('批量加入成員失敗', 'error');
        
        // 恢復顯示狀態
        displayedUsers.value.forEach(user => {
          user.isUpdating = false;
          user.is_member = usersDialog.memberIds.includes(user.id);
        });
      } finally {
        usersDialog.batchLoading = false;
      }
    };
    
    // 移除所有過濾的使用者
    const removeAllFilteredUsers = async () => {
      usersDialog.batchLoading = true;
      
      try {
        const members = displayedUsers.value.filter(user => user.is_member);
        
        // 標記所有用戶為非成員
        for (const user of members) {
          user.isUpdating = true;
          user.is_member = false;
        }
        
        // 更新所有使用者
        const userIds = members.map(user => user.id);
        
        // 批量更新使用者群組
        for (const userId of userIds) {
          const user = allUsers.value.find(u => u.id === userId);
          const updatedGroups = user.groups
            .filter(g => g.id !== usersDialog.groupId)
            .map(g => g.id);
          
          await axios.put(`/api/users/${userId}`, {
            group_ids: updatedGroups
          });
        }
        
        // 移除標記
        for (const user of members) {
          user.isUpdating = false;
        }
        
        // 更新成員 ID 列表
        usersDialog.memberIds = usersDialog.memberIds.filter(id => !userIds.includes(id));
        
        // 重新獲取群組列表
        fetchGroups();
        
        showSnackbar('批量移除成員成功');
      } catch (error) {
        console.error('批量移除成員失敗:', error);
        showSnackbar('批量移除成員失敗', 'error');
        
        // 恢復顯示狀態
        displayedUsers.value.forEach(user => {
          user.isUpdating = false;
          user.is_member = usersDialog.memberIds.includes(user.id);
        });
      } finally {
        usersDialog.batchLoading = false;
      }
    };
    
    // 獲取群組的使用者列表
    const fetchGroupUsers = async () => {
      if (!usersDialog.groupId) return;
      
      usersDialog.loading = true;
      usersDialog.memberIds = []; // 重置成員ID列表
      
      try {
        // 先獲取所有使用者
        if (allUsers.value.length === 0) {
          await fetchAllUsers();
        } else {
          await fetchAllUsers();
        }
        
        // 獲取群組成員的 ID 列表
        const group = groups.value.find(g => g.id === usersDialog.groupId);
        
        if (!group) {
          console.error('無法在前端找到群組:', usersDialog.groupId);
          showSnackbar('無法找到群組資料', 'error');
          usersDialog.loading = false;
          return;
        }
        
        const members = group?.users || [];
        usersDialog.memberIds = members.map(user => user.id);
        
        // 標記每個使用者是否是群組成員
        allUsers.value = allUsers.value.map(user => ({
          ...user,
          is_member: usersDialog.memberIds.includes(user.id),
          isUpdating: false
        }));
        
        // 檢查標記後的使用者列表
        const markedMembers = allUsers.value.filter(user => user.is_member);
        
        if (members.length > 0 && markedMembers.length === 0) {
          console.warn('警告: 群組有成員但標記後沒有成員，可能是資料不一致');
          try {
            const response = await axios.get(`/api/groups/${usersDialog.groupId}`);
            if (response.data.success) {
              const groupData = response.data.data;
              if (groupData.users && groupData.users.length > 0) {
                usersDialog.memberIds = groupData.users.map(user => user.id);
                allUsers.value = allUsers.value.map(user => ({
                  ...user,
                  is_member: usersDialog.memberIds.includes(user.id),
                  isUpdating: false
                }));
              }
            }
          } catch (error) {
            console.error('獲取群組詳情失敗:', error);
          }
        }
      } catch (error) {
        console.error('獲取群組成員失敗:', error);
        showSnackbar('獲取群組成員失敗', 'error');
      } finally {
        usersDialog.loading = false;
      }
    };
    
    // 格式化日期
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-TW')
    }
    
    // 獲取群組列表
    const fetchGroups = async () => {
      loading.value = true;
      try {
        const response = await axios.get('/api/groups', {
          params: {
            page: pagination.page,
            page_size: pagination.itemsPerPage,
            name: search.value
          }
        });
        
        if (response.data.success) {
          groups.value = response.data.items;
          pagination.totalPages = response.data.total_pages;
          pagination.totalItems = response.data.total;
        }
      } catch (error) {
        console.error('獲取群組失敗:', error);
        showSnackbar('獲取群組失敗', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    // 獲取所有使用者
    const fetchAllUsers = async () => {
      try {
        const response = await axios.get('/api/users', {
          params: {
            page: 1,
            page_size: 1000
          }
        });
        
        if (response.data.success) {
          allUsers.value = response.data.items;
          
          // 如果使用者數量超過每頁限制，獲取所有頁面
          if (response.data.total > response.data.page_size) {
            const totalPages = response.data.total_pages;
            
            for (let page = 2; page <= totalPages; page++) {
              try {
                const pageResponse = await axios.get('/api/users', {
                  params: {
                    page: page,
                    page_size: 1000
                  }
                });
                
                if (pageResponse.data.success) {
                  allUsers.value = [...allUsers.value, ...pageResponse.data.items];
                }
              } catch (error) {
                console.error(`獲取第 ${page} 頁使用者失敗:`, error);
              }
            }
          }
        } else {
          console.error('獲取使用者列表失敗:', response.data);
        }
      } catch (error) {
        console.error('獲取使用者失敗:', error);
        if (error.response) {
          console.error('錯誤回應:', error.response.data);
          console.error('錯誤詳情:', error.response.data);
          console.error('錯誤狀態:', error.response.status);
          console.error('錯誤標頭:', error.response.headers);
        } else if (error.request) {
          console.error('請求未收到回應:', error.request);
        } else {
          console.error('錯誤訊息:', error.message);
        }
      }
    }
    
    // 開啟新增群組對話框
    const openCreateDialog = () => {
      groupDialog.isEdit = false
      groupDialog.data = {
        id: null,
        name: '',
        description: '',
        can_login: true,
        can_manage_platform: false,
        can_use_chat_links: true
      }
      groupDialog.show = true
    }
    
    // 開啟編輯群組對話框
    const openEditDialog = (group) => {
      groupDialog.isEdit = true
      groupDialog.data = {
        id: group.id,
        name: group.name,
        description: group.description || '',
        can_login: group.can_login,
        can_manage_platform: group.can_manage_platform,
        can_use_chat_links: group.can_use_chat_links
      }
      groupDialog.show = true
    }
    
    // 開啟管理成員對話框
    const openUsersDialog = async (group) => {
      usersDialog.groupId = group.id;
      usersDialog.groupName = group.name;
      usersDialog.search = '';
      usersDialog.filter = 'all';
      usersDialog.loading = true;
      usersDialog.show = true;
      
      try {
        await fetchGroupUsers();
      } catch (error) {
        console.error('開啟管理成員對話框失敗:', error);
      }
    };
    
    // 確認刪除對話框
    const confirmDelete = (group) => {
      deleteDialog.id = group.id
      deleteDialog.name = group.name
      deleteDialog.show = true
    }
    
    // 儲存群組
    const saveGroup = async () => {
      const { valid } = await groupForm.value.validate()
      
      if (!valid) return
      
      groupDialog.loading = true
      
      try {
        let response
        
        if (groupDialog.isEdit) {
          // 編輯群組
          response = await axios.put(`/api/groups/${groupDialog.data.id}`, {
            name: groupDialog.data.name,
            description: groupDialog.data.description,
            can_login: groupDialog.data.can_login,
            can_manage_platform: groupDialog.data.can_manage_platform,
            can_use_chat_links: groupDialog.data.can_use_chat_links
          })
        } else {
          // 新增群組
          response = await axios.post('/api/groups', {
            name: groupDialog.data.name,
            description: groupDialog.data.description,
            can_login: groupDialog.data.can_login,
            can_manage_platform: groupDialog.data.can_manage_platform,
            can_use_chat_links: groupDialog.data.can_use_chat_links
          })
        }
        
        if (response.data.success) {
          groupDialog.show = false
          fetchGroups()
          showSnackbar(groupDialog.isEdit ? '群組更新成功' : '群組建立成功')
        }
      } catch (error) {
        console.error('儲存群組失敗:', error)
        showSnackbar(error.response?.data?.detail || '儲存群組失敗', 'error')
      } finally {
        groupDialog.loading = false
      }
    }
    
    // 切換使用者群組成員身份
    const toggleUserMembership = async (user) => {
      user.isUpdating = true;
      
      try {
        const updatedMembership = !user.is_member;
        
        console.log('切換使用者群組成員身份前:', {
          userId: user.id,
          username: user.username,
          currentMembership: user.is_member,
          updatedMembership: updatedMembership,
          currentGroups: user.groups.map(g => ({ id: g.id, name: g.name }))
        });
        
        if (updatedMembership) {
          // 將使用者加入群組
          await axios.put(`/api/users/${user.id}`, {
            group_ids: [...user.groups.map(g => g.id), usersDialog.groupId]
          });
          
          // 更新成員 ID 列表
          if (!usersDialog.memberIds.includes(user.id)) {
            usersDialog.memberIds.push(user.id);
          }
        } else {
          // 將使用者移出群組
          await axios.put(`/api/users/${user.id}`, {
            group_ids: user.groups.filter(g => g.id !== usersDialog.groupId).map(g => g.id)
          });
          
          // 更新成員 ID 列表
          usersDialog.memberIds = usersDialog.memberIds.filter(id => id !== user.id);
        }
        
        // 更新使用者狀態
        user.is_member = updatedMembership;
        
        console.log('切換使用者群組成員身份後:', {
          userId: user.id,
          username: user.username,
          newMembership: user.is_member,
          memberIds: usersDialog.memberIds
        });
        
        // 更新成功，重新獲取群組列表
        fetchGroups();
      } catch (error) {
        console.error('更新使用者群組失敗:', error);
        showSnackbar('更新使用者群組失敗', 'error');
        // 復原前端變更
        user.is_member = usersDialog.memberIds.includes(user.id);
      } finally {
        user.isUpdating = false;
      }
    };
    
    // 刪除群組
    const deleteGroup = async () => {
      deleteDialog.loading = true
      
      try {
        const response = await axios.delete(`/api/groups/${deleteDialog.id}`)
        
        if (response.data.success) {
          deleteDialog.show = false
          fetchGroups()
          showSnackbar('群組已刪除')
        }
      } catch (error) {
        console.error('刪除群組失敗:', error)
        showSnackbar(error.response?.data?.detail || '刪除群組失敗', 'error')
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
      fetchGroups()
    })
    
    return {
      groups,
      loading,
      search,
      pagination,
      headers,
      userHeaders,
      groupDialog,
      usersDialog,
      deleteDialog,
      snackbar,
      groupForm,
      displayedUsers,
      getFilteredNonMemberCount,
      getFilteredMemberCount,
      addAllFilteredUsers,
      removeAllFilteredUsers,
      fetchGroupUsers,
      formatDate,
      fetchGroups,
      openCreateDialog,
      openEditDialog,
      openUsersDialog,
      confirmDelete,
      saveGroup,
      toggleUserMembership,
      deleteGroup
    }
  }
}
</script>