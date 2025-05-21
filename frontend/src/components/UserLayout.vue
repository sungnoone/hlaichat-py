<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      @mouseenter="rail = false"
      @mouseleave="rail = true"
      permanent
      color="primary"
      theme="dark"
    >
      <v-list-item
        prepend-avatar="/logo.png"
        :title="rail ? '' : 'AI Chat 使用平台'"
        nav
      >
        <template v-slot:append>
          <v-btn
            variant="text"
            icon="mdi-chevron-left"
            @click.stop="rail = !rail"
          ></v-btn>
        </template>
      </v-list-item>

      <v-divider></v-divider>

      <v-list density="compact" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :title="rail ? '' : item.title"
          :to="item.to"
          :value="item.title"
          :class="{ 'active-link': $route.path === item.to }"
        >
          <template v-slot:prepend>
            <v-icon 
              :icon="item.icon" 
              :color="$route.path === item.to ? 'white' : 'grey-lighten-1'"
              size="24"
            ></v-icon>
          </template>
        </v-list-item>
      </v-list>
      
      <template v-slot:append>
        <div class="pa-2">
          <v-btn block color="error" variant="tonal" @click="logout">
            <v-icon icon="mdi-logout"></v-icon>
            <span v-if="!rail">登出</span>
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar color="white" :elevation="1">
      <v-app-bar-title>{{ pageTitle }}</v-app-bar-title>
      
      <v-spacer></v-spacer>
      
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            variant="text"
          >
            <v-avatar size="32" color="primary" class="mr-2">
              <span class="text-h6 text-white">{{ userInitials }}</span>
            </v-avatar>
            <span>{{ user?.full_name }}</span>
            <v-icon right>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item to="/user-profile">
            <v-list-item-title>
              <v-icon class="mr-2">mdi-account</v-icon>
              個人設定
            </v-list-item-title>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="logout">
            <v-list-item-title>
              <v-icon class="mr-2">mdi-logout</v-icon>
              登出
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <slot></slot>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'UserLayout',
  setup() {
    const drawer = ref(true)
    const rail = ref(true)
    const router = useRouter()
    const user = ref(null)
    
    const menuItems = [
      { title: '我的聊天機器人', icon: 'mdi-robot-happy-outline', to: '/user-dashboard' },
      { title: '使用紀錄', icon: 'mdi-clipboard-text-clock-outline', to: '/user-history' }
    ]
    
    const pageTitle = computed(() => {
      const currentRoute = router.currentRoute.value
      const matchedItem = menuItems.find(item => item.to === currentRoute.path)
      return matchedItem ? matchedItem.title : '使用平台'
    })
    
    const userInitials = computed(() => {
      if (!user.value?.full_name) return '?'
      return user.value.full_name
        .split(' ')
        .map(name => name.charAt(0))
        .join('')
        .toUpperCase()
    })
    
    onMounted(() => {
      // 從 localStorage 獲取用戶信息
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser)
        } catch (e) {
          console.error('解析使用者數據時發生錯誤', e)
        }
      }
    })
    
    const logout = async () => {
      try {
        await axios.post('/api/auth/logout')
      } catch (error) {
        console.error('登出時發生錯誤:', error)
      } finally {
        // 清除本地存儲的認證信息
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        
        // 導向登入頁
        router.push('/login')
      }
    }
    
    return {
      drawer,
      rail,
      menuItems,
      pageTitle,
      user,
      userInitials,
      logout
    }
  }
}
</script>

<style scoped>
.active-link {
  background-color: rgba(255, 255, 255, 0.1);
}
</style>
