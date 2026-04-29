<template>
  <n-layout has-sider style="height: 100vh">
    <!-- 侧边栏 -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      show-trigger
      :native-scrollbar="false"
      style="background-color: #fff"
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
      <n-layout-header bordered style="height: 56px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; background: #fff">
        <div style="font-size: 16px; font-weight: 500">
          {{ pageTitle }}
        </div>
        <n-space>
          <n-tag :type="botOnline ? 'success' : 'error'" size="small" round>
            {{ botOnline ? '运行中' : '已停止' }}
          </n-tag>
        </n-space>
      </n-layout-header>

      <!-- 内容 -->
      <n-layout-content content-style="padding: 24px; min-height: calc(100vh - 56px - 48px)">
        <router-view />
      </n-layout-content>

      <!-- 页脚 -->
      <n-layout-footer
        bordered
        style="height: 48px; padding: 0 24px; display: flex; align-items: center; justify-content: center; background: #fff"
      >
        <n-text depth="3" style="font-size: 12px">
          Sakura-Bot WebUI v1.0.0 · 基于 AGPL-3.0 许可
        </n-text>
      </n-layout-footer>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, ref, h } from "vue";
import { useRouter, useRoute } from "vue-router";
import { NIcon } from "naive-ui";
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
const botOnline = ref(true);

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

function renderIcon(icon: string) {
  return () => h(NIcon, null, { default: () => h("span", { innerHTML: icon }) });
}

const menuOptions: MenuOption[] = [
  { label: "仪表板", key: "/", icon: renderIcon(DashboardOutlined) },
  { label: "频道管理", key: "/channels", icon: renderIcon(ChannelOutlined) },
  { label: "AI 配置", key: "/ai-config", icon: renderIcon(RobotOutlined) },
  { label: "定时任务", key: "/schedules", icon: renderIcon(ScheduleOutlined) },
  { label: "转发规则", key: "/forwarding", icon: renderIcon(SwapOutlined) },
  { label: "互动设置", key: "/interaction", icon: renderIcon(LikeOutlined) },
  { label: "统计数据", key: "/stats", icon: renderIcon(BarChartOutlined) },
  { label: "系统运维", key: "/system", icon: renderIcon(SettingOutlined) },
  { label: "UserBot", key: "/userbot", icon: renderIcon(UserOutlined) },
];

function handleMenuSelect(key: string) {
  router.push(key);
}
</script>

<style scoped>
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
</style>
