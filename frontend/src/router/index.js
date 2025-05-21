import { createRouter, createWebHistory } from 'vue-router'

// 導入視圖
import Login from '../views/Login.vue'

// 創建路由配置
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/admin/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/admin/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/groups',
    name: 'Groups',
    component: () => import('../views/admin/Groups.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/chat-links',
    name: 'ChatLinks',
    component: () => import('../views/admin/ChatLinks.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/ad-config',
    name: 'ADConfig',
    component: () => import('../views/admin/ADConfig.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('../views/admin/Logs.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/admin/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user-dashboard',
    name: 'UserDashboard',
    component: () => import('../views/user/UserDashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user-profile',
    name: 'UserProfile',
    component: () => import('../views/user/UserProfile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user-history',
    name: 'UserHistory',
    component: () => import('../views/user/UserHistory.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守衛
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  
  if (to.meta.requiresAuth && !token) {
    // 需要認證但未登入，轉向登入頁
    next('/login')
  } else if (to.meta.requiresAdmin && !isAdmin(user)) {
    // 需要管理員權限但非管理員，轉向用戶儀表板
    next('/user-dashboard')
  } else {
    // 通過驗證
    next()
  }
})

// 檢查是否為管理員
function isAdmin(user) {
  if (!user || !user.groups) return false
  
  return user.groups.some(group => 
    group.name === 'admins' || group.can_manage_platform === true
  )
}

export default router 