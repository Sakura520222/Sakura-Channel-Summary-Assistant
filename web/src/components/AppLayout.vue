<template>
  <n-layout has-sider class="app-layout">
    <!-- 侧边栏 -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      show-trigger
      :native-scrollbar="false"
    >
      <div class="sider-header">
        <span class="logo">🌸</span>
        <span class="title" v-if="!collapsed">Sakura-Bot</span>
      </div>
      <n-menu
        :options="menuOptions"
        :value="currentRoute"
        @update:value="handleMenuSelect"
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :indent="24"
      />
    </n-layout-sider>

    <!-- 主内容区 -->
    <n-layout>
      <!-- 顶栏 -->
      <n-layout-header bordered class="app-header">
        <div class="header-title">{{ pageTitle }}</div>
        <n-space align="center">
          <n-tag :type="botOnline ? 'success' : 'error'" size="small" round>
            {{ botOnline ? '运行中' : '已停止' }}
          </n-tag>
          <n-button size="small" quaternary @click="toggleDarkMode">
            {{ isDark ? '🌙 深色' : '☀️ 浅色' }}
          </n-button>
          <n-button size="small" quaternary @click="handleLogout">退出登录</n-button>
        </n-space>
      </n-layout-header>

      <!-- 内容 -->
      <n-layout-content content-class="app-content">
        <router-view />
      </n-layout-content>

      <!-- 页脚 -->
      <n-layout-footer bordered class="app-footer">
        <n-text depth="3" class="footer-text">
          Sakura-Bot WebUI v1.0.0 · 基于 AGPL-3.0 许可
        </n-text>
      </n-layout-footer>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import type { MenuOption } from "naive-ui";
import {
  DashboardOutlined,
  ChannelOutlined,
  RobotOutlined,
  ScheduleOutlined,
  SwapOutlined,
  LikeOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
} from "./icons";

const router = useRouter();
const route = useRoute();
const collapsed = ref(false);
const botOnline = ref(false);
const isDark = ref(false);
let healthTimer: ReturnType<typeof setInterval> | null = null;

const currentRoute = computed(() => route.path || "/");

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    "/": "仪表板",
    "/channels": "频道管理",
    "/ai-config": "AI 配置",
    "/schedules": "定时任务",
    "/forwarding": "转发规则",
    "/interaction": "互动设置",
    "/stats": "统计数据",
    "/system": "系统运维",
    "/userbot": "UserBot 管理",
  };
  return map[route.path] || "Sakura-Bot";
});

// 图标已经是渲染函数，直接使用
const menuOptions: MenuOption[] = [
  { label: "仪表板", key: "/", icon: DashboardOutlined },
  { label: "频道管理", key: "/channels", icon: ChannelOutlined },
  { label: "AI 配置", key: "/ai-config", icon: RobotOutlined },
  { label: "定时任务", key: "/schedules", icon: ScheduleOutlined },
  { label: "转发规则", key: "/forwarding", icon: SwapOutlined },
  { label: "互动设置", key: "/interaction", icon: LikeOutlined },
  { label: "统计数据", key: "/stats", icon: BarChartOutlined },
  { label: "系统运维", key: "/system", icon: SettingOutlined },
  { label: "UserBot", key: "/userbot", icon: UserOutlined },
];

function handleMenuSelect(key: string) {
  router.push(key);
}

function handleLogout() {
  localStorage.removeItem("sakura_bot_token");
  router.push("/login");
}

function toggleDarkMode() {
  isDark.value = !isDark.value;
  document.documentElement.classList.toggle("dark", isDark.value);
  // 通知 Naive UI 的 darkTheme 由 App.vue 处理
  window.dispatchEvent(new CustomEvent("theme-change", { detail: isDark.value }));
}

async function checkBotStatus() {
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      const data = await res.json();
      botOnline.value = data.status === "ok";
    }
  } catch {
    botOnline.value = false;
  }
}

onMounted(() => {
  checkBotStatus();
  healthTimer = setInterval(checkBotStatus, 30000);
});

onUnmounted(() => {
  if (healthTimer) {
    clearInterval(healthTimer);
    healthTimer = null;
  }
});
</script>

<style scoped>
.app-layout {
  height: 100vh;
}
.sider-header {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  gap: 8px;
  height: 56px;
  border-bottom: 1px solid var(--n-border-color);
}
.logo {
  font-size: 24px;
}
.title {
  font-size: 16px;
  font-weight: 600;
  color: var(--n-text-color);
}
.app-header {
  height: 56px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-title {
  font-size: 16px;
  font-weight: 500;
}
.app-content {
  padding: 24px;
  min-height: calc(100vh - 56px - 48px);
}
.app-footer {
  height: 48px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.footer-text {
  font-size: 12px;
}
</style>
