<template>
  <n-spin :show="loading" description="加载中...">
  <div class="dashboard-page">
    <section class="dashboard-hero">
      <div>
        <n-text depth="3" class="hero-kicker">Overview</n-text>
        <h2>今日控制台</h2>
      </div>
      <div class="hero-status" :class="botStatusClass">
        <span class="hero-status-dot"></span>
        <span>{{ statusLabel }}</span>
      </div>
    </section>

    <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
      <n-gi span="0:4 640:2 1024:1">
        <n-card class="metric-card channel-card">
          <n-statistic label="监控频道" :value="dashboard.channel_count ?? 0">
            <template #prefix><span class="metric-icon">频</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="0:4 640:2 1024:1">
        <n-card class="metric-card summary-card">
          <n-statistic label="总结总数" :value="dashboard.total_summaries ?? 0">
            <template #prefix><span class="metric-icon">总</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="0:4 640:2 1024:1">
        <n-card class="metric-card forwarding-card">
          <n-statistic label="转发规则" :value="dashboard.forwarding_rule_count ?? 0">
            <template #prefix><span class="metric-icon">转</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="0:4 640:2 1024:1">
        <n-card class="metric-card status-card">
          <n-statistic label="Bot 状态" :value="statusLabel">
            <template #prefix><span class="metric-icon">态</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
    </n-grid>

    <n-grid :cols="2" :x-gap="16" :y-gap="16" class="mt-md" responsive="screen" item-responsive>
      <n-gi span="0:2 1024:1">
        <n-card title="系统信息" class="panel-card">
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
        <n-card title="定时任务概览" class="panel-card">
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

const botStatusClass = computed(() => ({
  running: dashboard.value.bot_status === "running",
  paused: dashboard.value.bot_status === "paused",
}));

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

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dashboard-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 22px;
  border: 1px solid rgba(133, 145, 171, 0.16);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(232, 74, 122, 0.09), rgba(43, 142, 240, 0.08)),
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

.dashboard-hero h2 {
  margin: 0;
  color: var(--n-text-color);
  font-size: 24px;
  line-height: 1.25;
  font-weight: 780;
  letter-spacing: 0;
}

.hero-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 34px;
  padding: 0 13px;
  border: 1px solid rgba(122, 132, 154, 0.22);
  border-radius: 999px;
  color: var(--n-text-color-2);
  background: rgba(122, 132, 154, 0.08);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.hero-status.running {
  color: #168864;
  border-color: rgba(32, 167, 121, 0.26);
  background: rgba(32, 167, 121, 0.1);
}

.hero-status.paused {
  color: #b8791e;
  border-color: rgba(242, 161, 58, 0.3);
  background: rgba(242, 161, 58, 0.12);
}

.hero-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.metric-card {
  position: relative;
  overflow: hidden;
  min-height: 124px;
}

.metric-card :deep(.n-statistic__label) {
  font-size: 13px;
}

.metric-card :deep(.n-statistic-value) {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

.metric-card :deep(.n-statistic-value__content) {
  font-size: 28px;
  font-weight: 800;
}

.metric-icon {
  display: inline-grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  color: #fff;
  font-size: 15px;
  font-weight: 780;
}

.channel-card .metric-icon {
  background: #e84a7a;
}

.summary-card .metric-icon {
  background: #2b8ef0;
}

.forwarding-card .metric-icon {
  background: #20a779;
}

.status-card .metric-icon {
  background: #f2a13a;
}

.panel-card {
  min-height: 292px;
}

:global(html.dark) .dashboard-hero {
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.22);
}

:global(html.dark) .hero-status.running {
  color: #55d0a6;
}

@media (max-width: 640px) {
  .dashboard-hero {
    align-items: flex-start;
    flex-direction: column;
    padding: 18px;
  }

  .dashboard-hero h2 {
    font-size: 21px;
  }
}
</style>
