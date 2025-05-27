<template>
  <div class="user-chat">
    <ChatInterface />
  </div>
</template>

<script>
import ChatInterface from '@/components/ChatInterface.vue'

export default {
  name: 'UserChat',
  components: {
    ChatInterface
  },
  setup() {
    return {}
  }
}
</script>

<style scoped>
.user-chat {
  height: 100%;
}
</style> 