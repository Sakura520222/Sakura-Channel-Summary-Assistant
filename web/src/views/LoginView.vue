<template>
  <div class="login-container">
    <n-card class="login-card" title="🌸 Sakura-Bot 登录" hoverable>
      <n-form ref="formRef" :model="formData">
        <n-form-item label="管理 Token" path="token">
          <n-input
            v-model:value="formData.token"
            type="password"
            show-password-on="click"
            placeholder="请输入管理 Token"
            @keyup.enter="handleLogin"
          />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="handleLogin">
          登 录
        </n-button>
      </n-form>
      <n-divider>或者</n-divider>
      <n-button block quaternary @click="handleDevLogin">
        开发模式（跳过认证）
      </n-button>
      <template #footer>
        <n-text depth="3" style="font-size: 12px">
          Token 可从 Bot 启动日志中获取，或使用 .env 中的 BOT_TOKEN 计算
        </n-text>
      </template>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import apiClient from "../api/client";

const router = useRouter();
const message = useMessage();
const loading = ref(false);

const formData = reactive({
  token: "",
});

async function handleLogin() {
  if (!formData.token) {
    message.warning("请输入 Token");
    return;
  }
  loading.value = true;
  try {
    localStorage.setItem("sakura_bot_token", formData.token);
    const res = await apiClient.get("/health");
    if (res.data?.status === "ok") {
      message.success("登录成功");
      router.push("/");
    } else {
      throw new Error("认证失败");
    }
  } catch {
    localStorage.removeItem("sakura_bot_token");
    message.error("Token 无效或服务器不可达");
  } finally {
    loading.value = false;
  }
}

function handleDevLogin() {
  localStorage.setItem("sakura_bot_token", "dev");
  message.info("已进入开发模式");
  router.push("/");
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  max-width: 90vw;
}
</style>
