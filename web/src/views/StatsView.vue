<template>
  <n-spin :show="loading" description="加载中...">
  <div>
    <n-card title="统计数据">
      <template #header-extra>
        <n-button @click="loadData">刷新</n-button>
      </template>

      <n-grid :cols="3" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
        <n-gi span="0:3 640:1">
          <n-statistic label="总结总数" :value="stats.total_count ?? 0" />
        </n-gi>
        <n-gi span="0:3 640:1">
          <n-statistic label="消息总数" :value="stats.total_messages ?? 0" />
        </n-gi>
        <n-gi span="0:3 640:1">
          <n-statistic label="本月总结" :value="stats.month_count ?? 0" />
        </n-gi>
      </n-grid>
    </n-card>

    <n-card title="历史总结" class="mt-md">
      <template #header-extra>
        <n-space>
          <n-select v-model:value="filterChannel" :options="channelOptions" placeholder="全部频道" clearable
            class="w-sm" @update:value="() => { pagination.page = 1; loadSummaries(); }" />
        </n-space>
      </template>

      <n-data-table :columns="summaryColumns" :data="summaries" :bordered="false" :loading="loadingSummaries"
        :remote="true" :pagination="pagination"
        @update:page="handlePageChange" />
    </n-card>

    <n-card title="频道排名" class="mt-md">
      <n-data-table :columns="rankingColumns" :data="ranking" :bordered="false" />
    </n-card>
  </div>
  </n-spin>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useMessage } from "naive-ui";
import type { DataTableColumns } from "naive-ui";
import { getStats, getSummaries, getChannelRanking, getChannels } from "@/api/modules";
import { getChannelName } from "@/utils/formatters";

const message = useMessage();
const loading = ref(true);
const stats = ref<Record<string, unknown>>({});
const summaries = ref<Array<Record<string, unknown>>>([]);
const ranking = ref<Array<Record<string, unknown>>>([]);
const channels = ref<string[]>([]);
const filterChannel = ref<string | null>(null);
const loadingSummaries = ref(false);
const totalSummaries = ref(0);
const pagination = ref({ page: 1, pageSize: 15, itemCount: 0 });

const channelOptions = computed(() =>
  channels.value.map((ch) => ({ label: getChannelName(ch), value: ch }))
);

const summaryColumns: DataTableColumns = [
  { title: "#", key: "id", width: 60 },
  { title: "频道", key: "channel_id", render: (row) => getChannelName(row.channel_id as string) },
  { title: "消息数", key: "message_count", width: 80 },
  {
    title: "创建时间", key: "created_at", width: 180,
    render: (row) => {
      const t = row.created_at as string;
      return t ? new Date(t).toLocaleString("zh-CN") : "-";
    },
  },
  {
    title: "内容", key: "summary_text",
    ellipsis: { tooltip: true },
    render: (row) => {
      const text = row.summary_text as string || "";
      return text.substring(0, 100) + (text.length > 100 ? "..." : "");
    },
  },
];

const rankingColumns: DataTableColumns = [
  { title: "#", key: "rank", width: 60, render: (_, i) => i + 1 },
  { title: "频道", key: "channel_id", render: (row) => getChannelName(row.channel_id as string) },
  { title: "总结数", key: "summary_count", width: 100 },
];

async function loadData() {
  loading.value = true;
  try {
    const [statsRes, chRes, rankRes] = await Promise.all([
      getStats(), getChannels(), getChannelRanking(),
    ]);
    if (statsRes.success) stats.value = statsRes.data;
    if (chRes.success) channels.value = (chRes.data.channels || []).map((c: Record<string, unknown>) => c.url as string);
    if (rankRes.success) ranking.value = rankRes.data || [];
    await loadSummaries();
  } catch {
    message.error("加载统计数据失败");
  } finally {
    loading.value = false;
  }
}

function handlePageChange(page: number) {
  pagination.value.page = page;
  loadSummaries();
}

async function loadSummaries() {
  loadingSummaries.value = true;
  try {
    const offset = (pagination.value.page - 1) * pagination.value.pageSize;
    const res = await getSummaries(filterChannel.value || undefined, pagination.value.pageSize, offset);
    if (res.success) {
      summaries.value = res.data.summaries || [];
      totalSummaries.value = res.data.total || summaries.value.length;
      pagination.value.itemCount = totalSummaries.value;
    }
  } catch {
    message.error("加载总结列表失败");
  } finally {
    loadingSummaries.value = false;
  }
}

onMounted(loadData);
</script>
