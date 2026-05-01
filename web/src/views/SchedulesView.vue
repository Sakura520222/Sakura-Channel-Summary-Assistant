<template>
  <div>
    <n-card title="定时任务管理">
      <template #header-extra>
        <n-button type="primary" @click="showAddModal = true">添加定时任务</n-button>
      </template>

      <n-spin :show="loading" description="加载中...">
        <n-data-table :columns="columns" :data="scheduleList" :bordered="false" />
      </n-spin>

      <!-- 未配置定时任务的频道 -->
      <n-divider v-if="unscheduled.length" />
      <n-alert v-if="unscheduled.length" type="info" title="未配置定时任务的频道">
        <n-space>
          <n-tag v-for="ch in unscheduled" :key="ch" size="small" class="cursor-pointer"
            @click="setupScheduleFor(ch)">
            {{ getChannelName(ch) }}
          </n-tag>
        </n-space>
      </n-alert>
    </n-card>

    <n-card title="总结状态维护" class="maintenance-card">
      <template #header-extra>
        <n-space>
          <n-button type="primary" secondary @click="addSummaryTime">添加记录</n-button>
          <n-button secondary :loading="summaryTimesLoading" @click="loadSummaryTimes">刷新</n-button>
          <n-button type="error" secondary @click="confirmDeleteAllSummaryTimes">清空总结时间</n-button>
          <n-button type="error" ghost @click="confirmDeletePollRegenerations">删除投票重生成文件</n-button>
        </n-space>
      </template>
      <n-alert type="info" :bordered="false" class="maintenance-tip">
        这里维护 data/.last_summary_time.json，适合放在“定时任务”页面，因为它决定下一次自动/手动总结从哪个时间点开始抓取消息。
        data/.poll_regenerations.json 是投票重生成运行时缓存，可在异常或数据污染时删除。
      </n-alert>
      <n-spin :show="summaryTimesLoading" description="加载中...">
        <n-data-table :columns="summaryTimeColumns" :data="summaryTimes" :bordered="false" />
      </n-spin>
    </n-card>

    <!-- 添加/编辑定时任务弹窗 -->
    <n-modal v-model:show="showAddModal" preset="dialog" :title="editingChannel ? '编辑定时任务' : '添加定时任务'"
      positive-text="保存" negative-text="取消" @positive-click="handleSave">
      <n-form label-placement="left" label-width="80">
        <n-form-item label="频道">
          <n-select v-model:value="form.channel" :options="channelOptions" :disabled="!!editingChannel"
            placeholder="选择频道" />
        </n-form-item>
        <n-form-item label="频率">
          <n-radio-group v-model:value="form.frequency">
            <n-radio value="daily">每天</n-radio>
            <n-radio value="weekly">每周</n-radio>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="时间">
          <n-time-picker v-model:formatted-value="form.time" format="HH:mm" value-format="HH:mm" />
        </n-form-item>
        <n-form-item v-if="form.frequency === 'weekly'" label="星期">
          <n-checkbox-group v-model:value="form.days">
            <n-space>
              <n-checkbox v-for="d in weekDays" :key="d.value" :value="d.value" :label="d.label" />
            </n-space>
          </n-checkbox-group>
        </n-form-item>
      </n-form>
    </n-modal>

    <!-- 编辑上次总结时间 -->
    <n-modal v-model:show="showSummaryTimeModal" preset="dialog" :title="summaryTimeEditing ? '编辑上次总结时间' : '添加上次总结时间'"
      positive-text="保存" negative-text="取消" @positive-click="handleSaveSummaryTime">
      <n-form label-placement="left" label-width="120">
        <n-form-item label="频道">
          <n-auto-complete
            v-model:value="summaryTimeForm.channel"
            :options="summaryTimeChannelOptions"
            :disabled="summaryTimeEditing"
            placeholder="输入频道 URL、@username 或频道 ID"
          />
        </n-form-item>
        <n-form-item label="时间">
          <n-date-picker v-model:value="summaryTimeForm.timestamp" type="datetime" clearable />
        </n-form-item>
        <n-form-item label="总结消息 ID">
          <n-dynamic-tags v-model:value="summaryTimeForm.summary_message_ids" />
        </n-form-item>
        <n-form-item label="投票消息 ID">
          <n-dynamic-tags v-model:value="summaryTimeForm.poll_message_ids" />
        </n-form-item>
        <n-form-item label="按钮消息 ID">
          <n-dynamic-tags v-model:value="summaryTimeForm.button_message_ids" />
        </n-form-item>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from "vue";
import { NButton, NTag, useMessage, useDialog } from "naive-ui";
import type { DataTableColumns } from "naive-ui";
import {
  deleteAllLastSummaryTimes,
  deleteLastSummaryTime,
  deletePollRegenerationsFile,
  deleteSchedule,
  getChannels,
  getLastSummaryTimes,
  getSchedules,
  updateLastSummaryTime,
  updateSchedule,
  type LastSummaryTimeItem,
} from "@/api/modules";
import { getChannelName } from "@/utils/formatters";

const message = useMessage();
const dialog = useDialog();
const loading = ref(true);
const scheduleList = ref<Array<Record<string, unknown>>>([]);
const unscheduled = ref<string[]>([]);
const allChannels = ref<string[]>([]);
const showAddModal = ref(false);
const editingChannel = ref("");
const summaryTimesLoading = ref(false);
const summaryTimes = ref<LastSummaryTimeItem[]>([]);
const showSummaryTimeModal = ref(false);
const summaryTimeEditing = ref(false);

const summaryTimeForm = ref({
  channel: "",
  timestamp: Date.now() as number | null,
  summary_message_ids: [] as string[],
  poll_message_ids: [] as string[],
  button_message_ids: [] as string[],
});

const form = ref({
  channel: "",
  frequency: "daily",
  time: "09:00",
  days: ["mon"],
});

const weekDays = [
  { value: "mon", label: "周一" },
  { value: "tue", label: "周二" },
  { value: "wed", label: "周三" },
  { value: "thu", label: "周四" },
  { value: "fri", label: "周五" },
  { value: "sat", label: "周六" },
  { value: "sun", label: "周日" },
];

const channelOptions = computed(() =>
  allChannels.value.map((ch) => ({ label: getChannelName(ch), value: ch }))
);

const summaryTimeChannelOptions = computed(() =>
  allChannels.value.map((ch) => ({ label: ch, value: ch }))
);

const columns: DataTableColumns = [
  { title: "频道", key: "channel", render: (row) => getChannelName(row.channel as string) },
  {
    title: "频率", key: "frequency", width: 100,
    render: (row) => row.frequency === "daily" ? "每天" : "每周",
  },
  {
    title: "时间", key: "time", width: 100,
    render: (row) => `${String(row.hour).padStart(2, "0")}:${String(row.minute).padStart(2, "0")}`,
  },
  {
    title: "星期", key: "days", width: 200,
    render: (row) => {
      const days = row.days as string[];
      if (!days?.length) return "-";
      return days.join(", ");
    },
  },
  {
    title: "操作", key: "actions", width: 150,
    render: (row) => {
      const ch = row.channel as string;
      return [
        h(NButton, { size: "small", quaternary: true, onClick: () => editSchedule(row) }, () => "编辑"),
        h(NButton, { size: "small", type: "error", quaternary: true, onClick: () => removeSchedule(ch) }, () => "删除"),
      ];
    },
  },
];

const summaryTimeColumns: DataTableColumns<LastSummaryTimeItem> = [
  { title: "频道", key: "channel", render: (row) => getChannelName(row.channel) },
  {
    title: "上次总结时间",
    key: "time",
    render: (row) => formatDateTime(row.time),
  },
  {
    title: "总结消息",
    key: "summary_message_ids",
    width: 100,
    render: (row) => row.summary_message_ids?.length || 0,
  },
  {
    title: "投票消息",
    key: "poll_message_ids",
    width: 100,
    render: (row) => row.poll_message_ids?.length || 0,
  },
  {
    title: "操作",
    key: "actions",
    width: 170,
    render: (row) => [
      h(NButton, { size: "small", quaternary: true, onClick: () => editSummaryTime(row) }, () => "编辑"),
      h(NButton, { size: "small", type: "error", quaternary: true, onClick: () => removeSummaryTime(row.channel) }, () => "删除"),
    ],
  },
];

function editSchedule(row: Record<string, unknown>) {
  editingChannel.value = row.channel as string;
  form.value = {
    channel: row.channel as string,
    frequency: row.frequency as string,
    time: `${String(row.hour).padStart(2, "0")}:${String(row.minute).padStart(2, "0")}`,
    days: (row.days as string[]) || ["mon"],
  };
  showAddModal.value = true;
}

function setupScheduleFor(channel: string) {
  editingChannel.value = "";
  form.value = { channel, frequency: "daily", time: "09:00", days: ["mon"] };
  showAddModal.value = true;
}

async function handleSave() {
  const { channel, frequency, time, days } = form.value;
  const [hour, minute] = time.split(":").map(Number);
  try {
    const res = await updateSchedule(channel, { frequency, hour, minute, days });
    message[res.success ? "success" : "error"](res.message);
    if (res.success) {
      showAddModal.value = false;
      await loadData();
    }
  } catch {
    message.error("保存失败");
  }
  return true;
}

async function removeSchedule(channel: string) {
  dialog.warning({
    title: "确认删除",
    content: `确定要删除频道 ${getChannelName(channel)} 的定时任务吗？`,
    positiveText: "删除",
    negativeText: "取消",
    onPositiveClick: async () => {
      try {
        const res = await deleteSchedule(channel);
        message[res.success ? "success" : "error"](res.message);
        if (res.success) await loadData();
      } catch {
        message.error("删除失败");
      }
    },
  });
}

function formatDateTime(value: string) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function addSummaryTime() {
  summaryTimeEditing.value = false;
  summaryTimeForm.value = {
    channel: allChannels.value[0] || "",
    timestamp: Date.now(),
    summary_message_ids: [],
    poll_message_ids: [],
    button_message_ids: [],
  };
  showSummaryTimeModal.value = true;
}

function editSummaryTime(row: LastSummaryTimeItem) {
  const timestamp = row.time ? new Date(row.time).getTime() : Date.now();
  summaryTimeEditing.value = true;
  summaryTimeForm.value = {
    channel: row.channel,
    timestamp: Number.isNaN(timestamp) ? Date.now() : timestamp,
    summary_message_ids: (row.summary_message_ids || []).map(String),
    poll_message_ids: (row.poll_message_ids || []).map(String),
    button_message_ids: (row.button_message_ids || []).map(String),
  };
  showSummaryTimeModal.value = true;
}

function parseIdTags(values: string[]) {
  return values
    .map((value) => Number(String(value).trim()))
    .filter((value) => Number.isInteger(value));
}

async function handleSaveSummaryTime() {
  const { channel, timestamp } = summaryTimeForm.value;
  if (!channel || !timestamp) {
    message.error("请选择有效的频道和时间");
    return false;
  }
  try {
    const res = await updateLastSummaryTime(channel, {
      time: new Date(timestamp).toISOString(),
      summary_message_ids: parseIdTags(summaryTimeForm.value.summary_message_ids),
      poll_message_ids: parseIdTags(summaryTimeForm.value.poll_message_ids),
      button_message_ids: parseIdTags(summaryTimeForm.value.button_message_ids),
    });
    message[res.success ? "success" : "error"](res.message);
    if (res.success) {
      showSummaryTimeModal.value = false;
      await loadSummaryTimes();
    }
  } catch {
    message.error("保存总结时间失败");
  }
  return true;
}

function removeSummaryTime(channel: string) {
  dialog.warning({
    title: "确认删除",
    content: `确定要删除频道 ${getChannelName(channel)} 的上次总结时间吗？删除后下次总结可能回溯更长时间。`,
    positiveText: "删除",
    negativeText: "取消",
    onPositiveClick: async () => {
      try {
        const res = await deleteLastSummaryTime(channel);
        message[res.success ? "success" : "error"](res.message);
        if (res.success) await loadSummaryTimes();
      } catch {
        message.error("删除总结时间失败");
      }
    },
  });
}

function confirmDeleteAllSummaryTimes() {
  dialog.error({
    title: "确认清空总结时间",
    content: "这会删除 data/.last_summary_time.json。所有频道下次总结可能从默认时间范围重新抓取。",
    positiveText: "确认清空",
    negativeText: "取消",
    onPositiveClick: async () => {
      try {
        const res = await deleteAllLastSummaryTimes();
        message[res.success ? "success" : "error"](res.message);
        if (res.success) await loadSummaryTimes();
      } catch {
        message.error("清空总结时间失败");
      }
    },
  });
}

function confirmDeletePollRegenerations() {
  dialog.error({
    title: "确认删除投票重生成文件",
    content: "这会删除 data/.poll_regenerations.json，现有投票重生成状态会丢失。",
    positiveText: "确认删除",
    negativeText: "取消",
    onPositiveClick: async () => {
      try {
        const res = await deletePollRegenerationsFile();
        message[res.success ? "success" : "error"](res.message);
      } catch {
        message.error("删除投票重生成文件失败");
      }
    },
  });
}

async function loadSummaryTimes() {
  summaryTimesLoading.value = true;
  try {
    const res = await getLastSummaryTimes();
    if (res.success) {
      summaryTimes.value = res.data.items || [];
    }
  } catch {
    message.error("加载总结时间失败");
  } finally {
    summaryTimesLoading.value = false;
  }
}

async function loadData() {
  loading.value = true;
  try {
    const [schedRes, chRes] = await Promise.all([getSchedules(), getChannels(), loadSummaryTimes()]);
    if (schedRes.success) {
      scheduleList.value = schedRes.data.schedules || [];
      unscheduled.value = schedRes.data.unscheduled_channels || [];
    }
    if (chRes.success) {
      allChannels.value = (chRes.data.channels || []).map((c: Record<string, unknown>) => c.url as string);
    }
  } catch {
    message.error("加载数据失败");
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<style scoped>
.maintenance-card {
  margin-top: 16px;
}

.maintenance-tip {
  margin-bottom: 16px;
}
</style>
