<template>
  <UserLayout>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">個人設定</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8" lg="6">
        <v-card>
          <v-card-title class="bg-primary text-white">
            個人資料
          </v-card-title>
          <v-card-text class="pt-4">
            <v-form ref="profileForm" @submit.prevent="updateProfile">
              <v-text-field
                v-model="profile.username"
                label="使用者名稱"
                variant="outlined"
                readonly
                class="mb-3"
              ></v-text-field>

              <v-text-field
                v-model="profile.full_name"
                label="姓名"
                variant="outlined"
                readonly
                class="mb-3"
              ></v-text-field>

              <v-text-field
                v-model="profile.email"
                label="電子郵件"
                variant="outlined"
                readonly
                class="mb-3"
              ></v-text-field>

              <v-text-field
                v-model="profile.phone"
                label="電話"
                variant="outlined"
                :readonly="profile.is_ad_user"
                class="mb-3"
              ></v-text-field>

              <v-text-field
                v-model="profile.department"
                label="部門"
                variant="outlined"
                readonly
                class="mb-3"
              ></v-text-field>

              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  v-if="!profile.is_ad_user"
                  color="primary"
                  type="submit"
                  :loading="loading.profile"
                >
                  更新資料
                </v-btn>
              </v-card-actions>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="8" lg="6" v-if="!profile.is_ad_user">
        <v-card>
          <v-card-title class="bg-primary text-white">
            變更密碼
          </v-card-title>
          <v-card-text class="pt-4">
            <v-form ref="passwordForm" @submit.prevent="updatePassword">
              <v-text-field
                v-model="passwords.current"
                label="目前密碼"
                type="password"
                variant="outlined"
                :rules="[v => !!v || '請輸入目前密碼']"
                class="mb-3"
              ></v-text-field>

              <v-text-field
                v-model="passwords.new"
                label="新密碼"
                type="password"
                variant="outlined"
                :rules="[v => !!v || '請輸入新密碼']"
                class="mb-3"
              ></v-text-field>

              <v-text-field
                v-model="passwords.confirm"
                label="確認新密碼"
                type="password"
                variant="outlined"
                :rules="[
                  v => !!v || '請確認新密碼',
                  v => v === passwords.new || '密碼不一致'
                ]"
                class="mb-3"
              ></v-text-field>

              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  type="submit"
                  :loading="loading.password"
                >
                  變更密碼
                </v-btn>
              </v-card-actions>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 操作結果提示 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">
          關閉
        </v-btn>
      </template>
    </v-snackbar>
  </UserLayout>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import UserLayout from '@/components/UserLayout.vue'
import axios from 'axios'

export default {
  name: 'UserProfile',
  components: {
    UserLayout
  },
  setup() {
    const profile = ref({
      username: '',
      full_name: '',
      email: '',
      phone: '',
      department: '',
      is_ad_user: false
    })

    const passwords = reactive({
      current: '',
      new: '',
      confirm: ''
    })

    const loading = reactive({
      profile: false,
      password: false
    })

    const snackbar = reactive({
      show: false,
      text: '',
      color: 'success'
    })

    const profileForm = ref(null)
    const passwordForm = ref(null)

    // 獲取個人資料
    const fetchProfile = async () => {
      try {
        const response = await axios.get('/api/auth/me')
        if (response.data.user) {
          const user = response.data.user
          profile.value = {
            username: user.username,
            full_name: user.full_name,
            email: user.email || '',
            phone: user.phone || '',
            department: user.department || '',
            is_ad_user: user.is_ad_user
          }
        }
      } catch (error) {
        console.error('獲取個人資料失敗:', error)
        showSnackbar('獲取個人資料失敗', 'error')
      }
    }

    // 更新個人資料
    const updateProfile = async () => {
      if (profile.value.is_ad_user) {
        showSnackbar('AD帳號無法修改個人資料', 'warning')
        return
      }

      loading.profile = true
      try {
        const response = await axios.put('/api/users/profile', {
          phone: profile.value.phone
        })

        if (response.data.success) {
          showSnackbar('個人資料更新成功')
        }
      } catch (error) {
        console.error('更新個人資料失敗:', error)
        showSnackbar(error.response?.data?.detail || '更新個人資料失敗', 'error')
      } finally {
        loading.profile = false
      }
    }

    // 更新密碼
    const updatePassword = async () => {
      const { valid } = await passwordForm.value.validate()
      
      if (!valid) return

      loading.password = true
      try {
        const response = await axios.put('/api/users/password', {
          current_password: passwords.current,
          new_password: passwords.new
        })

        if (response.data.success) {
          showSnackbar('密碼更新成功')
          passwords.current = ''
          passwords.new = ''
          passwords.confirm = ''
        }
      } catch (error) {
        console.error('更新密碼失敗:', error)
        showSnackbar(error.response?.data?.detail || '更新密碼失敗', 'error')
      } finally {
        loading.password = false
      }
    }

    // 顯示提示訊息
    const showSnackbar = (text, color = 'success') => {
      snackbar.text = text
      snackbar.color = color
      snackbar.show = true
    }

    onMounted(() => {
      fetchProfile()
    })

    return {
      profile,
      passwords,
      loading,
      snackbar,
      profileForm,
      passwordForm,
      updateProfile,
      updatePassword
    }
  }
}
</script> 