<template>
  <n-spin :show="loading" description="加载中...">
  <div>
    <n-grid :cols="2" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
      <!-- Bot 状态 -->
      <n-gi span="0:2 1024:1">
        <n-card title="Bot 状态">
          <n-descriptions bordered :column="1" label-placement="left">
            <n-descriptions-item label="运行状态">
              <n-tag :type="statusMap[botStatus.status] || 'default'" size="small">
                {{ statusLabels[botStatus.status] || botStatus.status }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="版本">{{ botStatus.version }}</n-descriptions-item>
            <n-descriptions-item label="监控频道数">{{ botStatus.channel_count }}</n-descriptions-item>
            <n-descriptions-item label="转发功能">
              <n-tag :type="botStatus.forwarding_enabled ? 'success' : 'default'" size="small">
                {{ botStatus.forwarding_enabled ? '已启用' : '已禁用' }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="QA Bot">
              <n-tag :type="botStatus.qa_bot_running ? 'success' : 'default'" size="small">
                {{ botStatus.qa_bot_running ? '运行中' : '未运行' }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="UserBot">
              <n-tag :type="botStatus.userbot_connected ? 'success' : 'default'" size="small">
                {{ botStatus.userbot_connected ? '已连接' : '未连接' }}
              </n-tag>
            </n-descriptions-item>
          </n-descriptions>
        </n-card>
      </n-gi>

      <!-- 控制面板 -->
      <n-gi span="0:2 1024:1">
        <n-card title="控制面板">
          <n-space vertical>
            <!-- 暂停/恢复 -->
            <n-space>
              <n-button type="warning" :disabled="botStatus.status === 'paused'" @click="handlePause">
                暂停 Bot
              </n-button>
              <n-button type="success" :disabled="botStatus.status === 'running'" @click="handleResume">
                恢复 Bot
              </n-button>
            </n-space>

            <n-divider />

            <!-- 日志级别 -->
            <n-form-item label="日志级别" label-placement="left" label-width="80">
              <n-select v-model:value="logLevel" :options="logLevelOptions" style="width: 150px" />
              <n-button type="primary" style="margin-left: 12px" @click="handleLogLevelChange">
                应用
              </n-button>
            </n-form-item>

            <n-divider />

            <!-- 重启 -->
            <n-button type="error" @click="handleRestart">请求重启</n-button>
            <n-text depth="3" style="font-size: 12px">重启请求将设置标记，Bot 在下次检查时执行重启</n-text>
          </n-space>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
  </n-spin>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useMessage, useDialog } from "naive-ui";
import { getSystemStatus, pauseBot, resumeBot, updateLogLevel, restartBot } from "@/api/modules";

const message = useMessage();
const dialog = useDialog();
const loading = ref(true);
const logLevel = ref("INFO");

const botStatus = reactive({
  status: "unknown",
  version: "-",
  log_level: "INFO",
  channel_count: 0,
  forwarding_enabled: false,
  qa_bot_running: false,
  userbot_connected: false,
});

const statusMap: Record<string, string> = {
  running: "success",
  paused: "warning",
  shutting_down: "error",
};

const statusLabels: Record<string, string> = {
  running: "运行中",
  paused: "已暂停",
  shutting_down: "关闭中",
};

const logLevelOptions = [
  { label: "DEBUG", value: "DEBUG" },
  { label: "INFO", value: "INFO" },
  { label: "WARNING", value: "WARNING" },
  { label: "ERROR", value: "ERROR" },
  { label: "CRITICAL", value: "CRITICAL" },
];

async function loadStatus() {
  loading.value = true;
  try {
    const res = await getSystemStatus();
    if (res.success) {
      Object.assign(botStatus, res.data);
      logLevel.value = res.data.log_level || "INFO";
    }
  } catch {
    message.error("获取状态失败");
  } finally {
    loading.value = false;
  }
}

async function handlePause() {
  dialog.warning({
    title: "确认暂停",
    content: "暂停后 Bot 将停止执行定时任务，确定继续吗？",
    positiveText: "确认暂停",
    negativeText: "取消",
    onPositiveClick: async () => {
      const res = await pauseBot();
      message[res.success ? "success" : "error"](res.message);
      if (res.success) await loadStatus();
    },
  });
}

async function handleResume() {
  const res = await resumeBot();
  message[res.success ? "success" : "error"](res.message);
  if (res.success) await loadStatus();
}

async function handleLogLevelChange() {
  const res = await updateLogLevel(logLevel.value);
  message[res.success ? "success" : "error"](res.message);
}

function handleRestart() {
  dialog.error({
    title: "确认重启",
    content: "确定要请求重启 Bot 吗？",
    positiveText: "确认重启",
    negativeText: "取消",
    onPositiveClick: async () => {
      const res = await restartBot();
      message[res.success ? "success" : "error"](res.message);
    },
  });
}

onMounted(loadStatus);
</script>
