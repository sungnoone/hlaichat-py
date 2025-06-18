import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // 從上一級目錄載入環境變數
  const envDir = path.resolve(__dirname, '..')
  const env = loadEnv(mode, envDir)
  
  return {
    plugins: [vue()],
    envDir: envDir, // 設定環境變數檔案目錄
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      host: '0.0.0.0', // 允許所有 IP 連入
      port: 3000, // 指定埠號
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true
        }
      }
    }
  }
}) 