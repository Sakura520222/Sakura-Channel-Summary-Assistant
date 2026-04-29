<template>
  <div>
    <n-card title="UserBot 管理">
      <n-descriptions bordered :column="1" label-placement="left">
        <n-descriptions-item label="状态">
          <n-tag :type="userbot.enabled ? 'success' : 'default'" size="small">
            {{ userbot.enabled ? '已启用' : '未启用' }}
          </n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="连接">
          <n-tag :type="userbot.connected ? 'success' : 'error'" size="small">
            {{ userbot.connected ? '已连接' : '未连接' }}
          </n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="手机号">{{ userbot.phone_preview || '未配置' }}</n-descriptions-item>
        <n-descriptions-item label="回退到 Bot">
          <n-tag :type="userbot.fallback_to_bot ? 'info' : 'default'" size="small">
            {{ userbot.fallback_to_bot ? '已启用' : '未启用' }}
          </n-tag>
        </n-descriptions-item>
      </n-descriptions>

      <n-divider />

      <n-space vertical>
        <n-h5>频道操作</n-h5>
        <n-input-group>
          <n-input v-model:value="channelUrl" placeholder="https://t.me/channel_name" style="width: 300px" />
          <n-button type="primary" @click="handleJoin" :loading="loading">加入频道</n-button>
          <n-button type="error" @click="handleLeave" :loading="loading">离开频道</n-button>
        </n-input-group>
        <n-text depth="3" style="font-size: 12px">让 UserBot 加入或离开指定频道</n-text>
      </n-space>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useMessage } from "naive-ui";
import { getUserBotStatus, userBotJoinChannel, userBotLeaveChannel } from "../api/modules";

const message = useMessage();
const loading = ref(false);
const channelUrl = ref("");

const userbot = reactive({
  enabled: false,
  connected: false,
  phone_preview: "",
  fallback_to_bot: false,
});

async function loadStatus() {
  try {
    const res = await getUserBotStatus();
    if (res.success) Object.assign(userbot, res.data);
  } catch {
    message.error("获取 UserBot 状态失败");
  }
}

async function handleJoin() {
  if (!channelUrl.value.trim()) {
    message.warning("请输入频道 URL");
    return;
  }
  loading.value = true;
  try {
    const res = await userBotJoinChannel(channelUrl.value.trim());
    message[res.success ? "success" : "error"](res.message);
  } catch {
    message.error("操作失败");
  } finally {
    loading.value = false;
  }
}

async function handleLeave() {
  if (!channelUrl.value.trim()) {
    message.warning("请输入频道 URL");
    return;
  }
  loading.value = true;
  try {
    const res = await userBotLeaveChannel(channelUrl.value.trim());
    message[res.success ? "success" : "error"](res.message);
  } catch {
    message.error("操作失败");
  } finally {
    loading.value = false;
  }
}

onMounted(loadStatus);
</script>
