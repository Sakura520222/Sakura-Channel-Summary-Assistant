<template>
  <n-spin :show="loading" description="加载中...">
  <div>
    <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
      <n-gi span="0:4 640:2 1024:1">
        <n-card>
          <n-statistic label="监控频道" :value="dashboard.channel_count ?? 0">
            <template #prefix><span style="font-size: 20px">📺</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="0:4 640:2 1024:1">
        <n-card>
          <n-statistic label="总结总数" :value="dashboard.total_summaries ?? 0">
            <template #prefix><span style="font-size: 20px">📊</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="0:4 640:2 1024:1">
        <n-card>
          <n-statistic label="转发规则" :value="dashboard.forwarding_rule_count ?? 0">
            <template #prefix><span style="font-size: 20px">📡</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="0:4 640:2 1024:1">
        <n-card>
          <n-statistic label="Bot 状态" :value="statusLabel">

          </n-statistic>
        </n-card>
      </n-gi>
    </n-grid>

    <n-grid :cols="2" :x-gap="16" :y-gap="16" style="margin-top: 16px" responsive="screen" item-responsive>
      <n-gi span="0:2 1024:1">
        <n-card title="系统信息">
          <n-descriptions bordered :column="1" label-placement="left" size="small">
            <n-descriptions-item label="版本">{{ dashboard.version ?? '-' }}</n-descriptions-item>
            <n-descriptions-item label="AI 模型">{{ dashboard.ai_model ?? '-' }}</n-descriptions-item>
            <n-descriptions-item label="日志级别">{{ dashboard.log_level ?? '-' }}</n-descriptions-item>
            <n-descriptions-item label="转发状态">
              <n-tag :type="dashboard.forwarding_enabled ? 'success' : 'default'" size="small">
                {{ dashboard.forwarding_enabled ? '已启用' : '已禁用' }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="运行时长">{{ formatUptimeLocal(dashboard.uptime_seconds as number) }}</n-descriptions-item>
          </n-descriptions>
        </n-card>
      </n-gi>
      <n-gi span="0:2 1024:1">
        <n-card title="定时任务概览">
          <n-empty v-if="scheduleCount === 0" description="暂无定时任务" />
          <n-list v-else>
            <n-list-item v-for="s in schedules" :key="String(s.channel)">
              <n-thing :title="getChannelName(String(s.channel))">
                <template #description>
                  <n-text depth="3">
                    {{ s.frequency === 'daily' ? '每日' : '每周' }} {{ String(s.hour).padStart(2, '0') }}:{{ String(s.minute).padStart(2, '0') }}
                    <span v-if="(s.days as string[])?.length"> ({{ (s.days as string[]).join(', ') }})</span>
                  </n-text>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
  </n-spin>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useMessage } from "naive-ui";
import { getDashboard, getSchedules } from "@/api/modules";
import { getChannelName, formatUptime } from "@/utils/formatters";

const message = useMessage();
const loading = ref(true);
const dashboard = ref<Record<string, unknown>>({});
const schedules = ref<Array<Record<string, unknown>>>([]);

const statusLabel = computed(() => {
  const s = dashboard.value.bot_status as string;
  if (s === "running") return "运行中";
  if (s === "paused") return "已暂停";
  return s || "未知";
});

const scheduleCount = computed(() => schedules.value.length);

function formatUptimeLocal(seconds: number | undefined) {
  return formatUptime(seconds);
}

async function loadData() {
  loading.value = true;
  try {
    const [dashRes, schedRes] = await Promise.allSettled([
      getDashboard(),
      getSchedules(),
    ]);
    if (dashRes.status === "fulfilled" && dashRes.value.success) {
      dashboard.value = dashRes.value.data;
    }
    if (schedRes.status === "fulfilled" && schedRes.value.success) {
      schedules.value = schedRes.value.data.schedules || [];
    }
  } catch {
    message.error("加载仪表板数据失败");
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>
