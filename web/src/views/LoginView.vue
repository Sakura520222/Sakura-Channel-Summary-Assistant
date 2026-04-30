<template>
  <div class="login-container">
    <section class="login-hero" aria-label="Sakura-Bot">
      <div class="brand-mark" aria-hidden="true">🌸</div>
      <h1>Sakura-Bot</h1>
      <p>频道、AI、转发与定时任务的统一控制台</p>
      <div class="hero-metrics">
        <span>WebUI</span>
        <span>Naive UI</span>
        <span>AGPL-3.0</span>
      </div>
    </section>

    <n-card class="login-card" :bordered="false">
      <div class="login-card-header">
        <n-text class="login-title">登录控制台</n-text>
        <n-text depth="3" class="login-subtitle">使用启动日志中的管理 Token</n-text>
      </div>

      <n-form ref="formRef" :model="formData" class="login-form">
        <n-form-item label="管理 Token" path="token">
          <n-input
            v-model:value="formData.token"
            type="password"
            show-password-on="click"
            placeholder="请输入管理 Token"
            size="large"
            @keyup.enter="handleLogin"
          />
        </n-form-item>
        <n-button type="primary" block size="large" :loading="loading" @click="handleLogin">
          登录
        </n-button>
      </n-form>

      <n-divider v-if="devModeAvailable">或者</n-divider>
      <n-button v-if="devModeAvailable" block secondary :loading="devLoading" @click="handleDevLogin">
        开发模式
      </n-button>

      <n-text depth="3" class="login-hint">
        管理 Token 为 Bot Token 的 SHA256 前 16 位
      </n-text>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import { loginWithToken, checkAuthStatus } from "@/api/modules";

const router = useRouter();
const message = useMessage();
const loading = ref(false);
const devLoading = ref(false);
const devModeAvailable = ref(false);

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
    // 仅开发模式允许 fallback
    if (devModeAvailable.value) {
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

onMounted(async () => {
  try {
    const res = await checkAuthStatus();
    devModeAvailable.value = !!res.dev_mode;
  } catch {
    // 后端不可用时，开发环境仍显示按钮
    devModeAvailable.value = !!import.meta.env.DEV;
  }
});
</script>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 56px;
  min-height: 100vh;
  padding: 40px;
  overflow: hidden;
  background:
    linear-gradient(115deg, rgba(232, 74, 122, 0.2) 0%, transparent 28%, rgba(43, 142, 240, 0.17) 52%, transparent 74%, rgba(32, 167, 121, 0.15) 100%),
    linear-gradient(62deg, rgba(255, 255, 255, 0.52) 0%, rgba(235, 248, 255, 0.28) 30%, rgba(255, 244, 248, 0.42) 62%, rgba(244, 255, 250, 0.32) 100%),
    #f8fbff;
  background-size: 260% 260%, 180% 180%, auto;
  animation: login-flow 16s ease-in-out infinite;
}

.login-container::before {
  position: absolute;
  inset: 0;
  pointer-events: none;
  content: "";
  background-image:
    linear-gradient(rgba(40, 52, 76, 0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(40, 52, 76, 0.055) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.8), transparent 80%);
}

.login-container::after {
  position: absolute;
  inset: -35%;
  pointer-events: none;
  content: "";
  background:
    repeating-linear-gradient(
      116deg,
      transparent 0 15%,
      rgba(255, 255, 255, 0.18) 18%,
      rgba(255, 255, 255, 0.44) 20%,
      rgba(255, 255, 255, 0.12) 23%,
      transparent 27% 48%
    ),
    linear-gradient(104deg, transparent 15%, rgba(255, 255, 255, 0.3) 44%, transparent 68%);
  opacity: 0.74;
  mix-blend-mode: screen;
  transform: translate3d(-8%, -6%, 0);
  animation: light-sweep 12s linear infinite;
}

.login-hero,
.login-card {
  position: relative;
  z-index: 1;
}

.login-hero {
  width: min(460px, 42vw);
  color: #1e2b3f;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  margin-bottom: 22px;
  border-radius: 8px;
  color: #fff;
  font-size: 28px;
  font-weight: 850;
  background: linear-gradient(135deg, #e84a7a 0%, #2b8ef0 100%);
  box-shadow: 0 18px 40px rgba(232, 74, 122, 0.22);
}

.login-hero h1 {
  margin: 0;
  font-size: 48px;
  line-height: 1.04;
  font-weight: 850;
  letter-spacing: 0;
}

.login-hero p {
  max-width: 400px;
  margin: 18px 0 0;
  color: #526078;
  font-size: 16px;
  line-height: 1.75;
}

.hero-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}

.hero-metrics span {
  padding: 6px 10px;
  border: 1px solid rgba(82, 96, 120, 0.14);
  border-radius: 999px;
  color: #526078;
  background: rgba(255, 255, 255, 0.58);
  font-size: 12px;
  font-weight: 650;
}

.login-card {
  width: 420px;
  max-width: 92vw;
  padding: 8px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 28px 70px rgba(31, 43, 67, 0.16);
  backdrop-filter: blur(22px);
}

.login-card-header {
  margin-bottom: 22px;
}

.login-title {
  display: block;
  font-size: 24px;
  line-height: 1.25;
  font-weight: 760;
}

.login-subtitle {
  display: block;
  margin-top: 6px;
  font-size: 13px;
}

.login-form {
  margin-top: 4px;
}

.login-hint {
  display: block;
  margin-top: 18px;
  font-size: 12px;
  line-height: 1.6;
}

@keyframes login-flow {
  0% {
    background-position: 0% 44%, 100% 50%, center;
  }

  45% {
    background-position: 100% 56%, 24% 70%, center;
  }

  100% {
    background-position: 0% 44%, 100% 50%, center;
  }
}

@keyframes light-sweep {
  0% {
    transform: translate3d(-18%, -8%, 0) rotate(0.001deg);
  }

  100% {
    transform: translate3d(18%, 8%, 0) rotate(0.001deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-container,
  .login-container::after {
    animation: none;
  }
}

@media (max-width: 860px) {
  .login-container {
    flex-direction: column;
    align-items: stretch;
    justify-content: center;
    gap: 24px;
    padding: 24px;
  }

  .login-hero {
    width: 100%;
  }

  .login-hero h1 {
    font-size: 36px;
  }

  .login-card {
    width: 100%;
    max-width: none;
  }
}
</style>
