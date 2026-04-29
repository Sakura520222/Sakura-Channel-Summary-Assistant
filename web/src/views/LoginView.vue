<template>
  <div class="login-container">
    <n-card class="login-card" title="🌸 Sakura-Bot 登录" hoverable>
      <n-form ref="formRef" :model="formData">
        <n-form-item label="管理 Token" path="token">
          <n-input
            v-model:value="formData.token"
            type="password"
            show-password-on="click"
            placeholder="请输入管理 Token（从启动日志获取）"
            @keyup.enter="handleLogin"
          />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="handleLogin">
          登 录
        </n-button>
      </n-form>
      <n-divider>或者</n-divider>
      <n-button block quaternary :loading="devLoading" @click="handleDevLogin">
        开发模式（跳过认证）
      </n-button>
      <template #footer>
        <n-text depth="3" style="font-size: 12px">
          管理 Token 为 Bot Token 的 SHA256 前16位，可在 Bot 启动日志中查看
        </n-text>
      </template>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import { loginWithToken } from "@/api/modules";

const router = useRouter();
const message = useMessage();
const loading = ref(false);
const devLoading = ref(false);

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
    const res = await loginWithToken(formData.token);
    if (res.success && res.access_token) {
      localStorage.setItem("sakura_bot_token", res.access_token);
      message.success("登录成功");
      router.push("/");
    } else {
      message.error(res.message || "认证失败");
    }
  } catch {
    message.error("登录失败，请检查 Token 是否正确");
  } finally {
    loading.value = false;
  }
}

async function handleDevLogin() {
  devLoading.value = true;
  try {
    const res = await loginWithToken("dev");
    if (res.success && res.access_token) {
      localStorage.setItem("sakura_bot_token", res.access_token);
      message.info("已进入开发模式");
      router.push("/");
    } else {
      message.error(res.message || "开发模式认证失败");
    }
  } catch {
    // 仅开发环境允许 fallback
    if (import.meta.env.DEV) {
      localStorage.setItem("sakura_bot_token", "dev");
      message.info("已进入开发模式（后端不可用）");
      router.push("/");
    } else {
      message.error("无法连接到服务器，请检查网络或稍后重试");
    }
  } finally {
    devLoading.value = false;
  }
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
