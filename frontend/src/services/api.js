import axios from 'axios'

// 憑證 API
export const credentialApi = {
  // 取得憑證列表
  async getCredentials(params = {}) {
    const response = await axios.get('/api/credentials', { params })
    return response.data
  },

  // 取得所有憑證列表（用於下拉選單）
  async getAllCredentials() {
    const response = await axios.get('/api/credentials/simple')
    return response.data
  },

  // 取得單一憑證
  async getCredential(id) {
    const response = await axios.get(`/api/credentials/${id}`)
    return response.data
  },

  // 建立憑證
  async createCredential(data) {
    const response = await axios.post('/api/credentials', data)
    return response.data
  },

  // 更新憑證
  async updateCredential(id, data) {
    const response = await axios.put(`/api/credentials/${id}`, data)
    return response.data
  },

  // 刪除憑證
  async deleteCredential(id) {
    const response = await axios.delete(`/api/credentials/${id}`)
    return response.data
  }
} 