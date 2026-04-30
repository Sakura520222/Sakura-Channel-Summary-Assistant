<template>
  <n-spin :show="loading" description="加载中...">
  <div class="userbot-page">
    <section class="userbot-hero">
      <div>
        <n-text depth="3" class="hero-kicker">UserBot</n-text>
        <h2>账号连接状态</h2>
      </div>
      <n-tag :type="userbot.connected ? 'success' : 'error'" round>
        {{ userbot.connected ? '已连接' : '未连接' }}
      </n-tag>
    </section>

    <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
      <n-gi span="0:4 640:2 1024:1">
        <n-card class="status-card">
          <n-text depth="3" class="status-label">状态</n-text>
          <div class="status-value">
            <span class="status-mark" :class="{ active: userbot.enabled }"></span>
            {{ userbot.enabled ? '已启用' : '未启用' }}
          </div>
        </n-card>
      </n-gi>
      <n-gi span="0:4 640:2 1024:1">
        <n-card class="status-card">
          <n-text depth="3" class="status-label">连接</n-text>
          <div class="status-value">
            <span class="status-mark" :class="{ active: userbot.connected }"></span>
            {{ userbot.connected ? '在线' : '离线' }}
          </div>
        </n-card>
      </n-gi>
      <n-gi span="0:4 640:2 1024:1">
        <n-card class="status-card">
          <n-text depth="3" class="status-label">手机号</n-text>
          <div class="status-value text-value">{{ userbot.phone_preview || '未配置' }}</div>
        </n-card>
      </n-gi>
      <n-gi span="0:4 640:2 1024:1">
        <n-card class="status-card">
          <n-text depth="3" class="status-label">回退到 Bot</n-text>
          <div class="status-value">
            <span class="status-mark info" :class="{ active: userbot.fallback_to_bot }"></span>
            {{ userbot.fallback_to_bot ? '已启用' : '未启用' }}
          </div>
        </n-card>
      </n-gi>
    </n-grid>

    <n-card title="频道操作" class="action-card">
      <n-input-group class="channel-actions">
        <n-input v-model:value="channelUrl" placeholder="channel_name 或 @channel_name" />
        <n-button type="primary" @click="handleJoin" :loading="actionLoading">加入频道</n-button>
        <n-button type="error" secondary @click="handleLeave" :loading="actionLoading">离开频道</n-button>
      </n-input-group>
      <n-text depth="3" class="action-hint">支持频道名、@channel_name 或完整 t.me 链接</n-text>
    </n-card>
  </div>
  </n-spin>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useMessage, useDialog } from "naive-ui";
import { getUserBotStatus, userBotJoinChannel, userBotLeaveChannel } from "@/api/modules";

const message = useMessage();
const dialog = useDialog();
const loading = ref(true);
const actionLoading = ref(false);
const channelUrl = ref("");

const userbot = reactive({
  enabled: false,
  connected: false,
  phone_preview: "",
  fallback_to_bot: false,
});

async function loadStatus() {
  loading.value = true;
  try {
    const res = await getUserBotStatus();
    if (res.success) Object.assign(userbot, res.data);
  } catch {
    message.error("获取 UserBot 状态失败");
  } finally {
    loading.value = false;
  }
}

async function handleJoin() {
  if (!channelUrl.value.trim()) {
    message.warning("请输入频道名或链接");
    return;
  }
  dialog.info({
    title: "确认加入频道",
    content: `确定要让 UserBot 加入 ${channelUrl.value} 吗？`,
    positiveText: "确认加入",
    negativeText: "取消",
    onPositiveClick: async () => {
      actionLoading.value = true;
      try {
        const res = await userBotJoinChannel(channelUrl.value.trim());
        message[res.success ? "success" : "error"](res.message);
      } catch {
        message.error("操作失败");
      } finally {
        actionLoading.value = false;
      }
    },
  });
}

async function handleLeave() {
  if (!channelUrl.value.trim()) {
    message.warning("请输入频道名或链接");
    return;
  }
  dialog.warning({
    title: "确认离开频道",
    content: `确定要让 UserBot 离开 ${channelUrl.value} 吗？`,
    positiveText: "确认离开",
    negativeText: "取消",
    onPositiveClick: async () => {
      actionLoading.value = true;
      try {
        const res = await userBotLeaveChannel(channelUrl.value.trim());
        message[res.success ? "success" : "error"](res.message);
      } catch {
        message.error("操作失败");
      } finally {
        actionLoading.value = false;
      }
    },
  });
}

onMounted(loadStatus);
</script>

<style scoped>
.userbot-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.userbot-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 22px;
  border: 1px solid rgba(133, 145, 171, 0.16);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(32, 167, 121, 0.11), rgba(43, 142, 240, 0.08)),
    color-mix(in srgb, var(--n-color) 88%, transparent);
  box-shadow: 0 14px 34px rgba(31, 43, 67, 0.06);
}

.hero-kicker {
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.userbot-hero h2 {
  margin: 0;
  color: var(--n-text-color);
  font-size: 24px;
  line-height: 1.25;
  font-weight: 780;
  letter-spacing: 0;
}

.status-card {
  min-height: 112px;
}

.status-label {
  display: block;
  font-size: 13px;
}

.status-value {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 14px;
  color: var(--n-text-color);
  font-size: 22px;
  line-height: 1.2;
  font-weight: 780;
}

.text-value {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-mark {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #d25a5a;
  box-shadow: 0 0 0 5px rgba(210, 90, 90, 0.12);
}

.status-mark.active {
  background: #20a779;
  box-shadow: 0 0 0 5px rgba(32, 167, 121, 0.13);
}

.status-mark.info.active {
  background: #2b8ef0;
  box-shadow: 0 0 0 5px rgba(43, 142, 240, 0.13);
}

.action-card {
  max-width: 860px;
}

.channel-actions {
  max-width: 720px;
}

.action-hint {
  display: block;
  margin-top: 10px;
  font-size: 12px;
}

:global(html.dark) .userbot-hero {
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.22);
}

@media (max-width: 720px) {
  .userbot-hero {
    align-items: flex-start;
    flex-direction: column;
    padding: 18px;
  }

  .channel-actions {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .channel-actions :deep(.n-input),
  .channel-actions :deep(.n-button) {
    width: 100%;
  }
}
</style>
