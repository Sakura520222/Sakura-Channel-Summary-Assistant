<template>
  <div>
    <n-card title="定时任务管理">
      <template #header-extra>
        <n-button type="primary" @click="showAddModal = true">添加定时任务</n-button>
      </template>

      <n-data-table :columns="columns" :data="scheduleList" :bordered="false" />

      <!-- 未配置定时任务的频道 -->
      <n-divider v-if="unscheduled.length" />
      <n-alert v-if="unscheduled.length" type="info" title="未配置定时任务的频道">
        <n-space>
          <n-tag v-for="ch in unscheduled" :key="ch" size="small" style="cursor: pointer"
            @click="setupScheduleFor(ch)">
            {{ getChannelName(ch) }}
          </n-tag>
        </n-space>
      </n-alert>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from "vue";
import { NButton, NTag, useMessage } from "naive-ui";
import type { DataTableColumns } from "naive-ui";
import { getSchedules, updateSchedule, deleteSchedule } from "../api/modules";
import { getChannels } from "../api/modules";

const message = useMessage();
const scheduleList = ref<Array<Record<string, unknown>>>([]);
const unscheduled = ref<string[]>([]);
const allChannels = ref<string[]>([]);
const showAddModal = ref(false);
const editingChannel = ref("");

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

function getChannelName(url: string) {
  return url.replace("https://t.me/", "@");
}

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
  try {
    const res = await deleteSchedule(channel);
    message[res.success ? "success" : "error"](res.message);
    if (res.success) await loadData();
  } catch {
    message.error("删除失败");
  }
}

async function loadData() {
  try {
    const [schedRes, chRes] = await Promise.all([getSchedules(), getChannels()]);
    if (schedRes.success) {
      scheduleList.value = schedRes.data.schedules || [];
      unscheduled.value = schedRes.data.unscheduled_channels || [];
    }
    if (chRes.success) {
      allChannels.value = (chRes.data.channels || []).map((c: Record<string, unknown>) => c.url as string);
    }
  } catch {
    message.error("加载数据失败");
  }
}

onMounted(loadData);
</script>
