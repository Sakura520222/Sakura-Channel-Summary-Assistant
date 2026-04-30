<template>
  <div>
    <n-card title="频道列表">
      <template #header-extra>
        <n-button type="primary" @click="showAddModal = true">添加频道</n-button>
      </template>

      <n-spin :show="loading" description="加载中...">
        <n-data-table :columns="columns" :data="channels" :bordered="false" />
      </n-spin>
    </n-card>

    <!-- 添加频道弹窗 -->
    <n-modal v-model:show="showAddModal" preset="dialog" title="添加频道" positive-text="确认" negative-text="取消"
      @positive-click="handleAdd">
      <n-form-item label="频道 URL">
        <n-input v-model:value="newChannel" placeholder="https://t.me/channel_name" />
      </n-form-item>
    </n-modal>

    <!-- 删除确认弹窗 -->
    <n-modal v-model:show="showDeleteModal" preset="dialog" type="error" title="确认删除"
      positive-text="删除" negative-text="取消" @positive-click="handleDelete">
      <p>确定要删除频道 <strong>{{ deleteTarget }}</strong> 吗？</p>
      <p>相关的定时任务和投票设置也将被清除。</p>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from "vue";
import { NButton, NTag, NSpace, useMessage } from "naive-ui";
import type { DataTableColumns } from "naive-ui";
import { getChannels, addChannel, deleteChannel, generateSummary } from "@/api/modules";
import { getChannelName } from "@/utils/formatters";

const message = useMessage();
const loading = ref(true);
const channels = ref<Array<Record<string, unknown>>>([]);
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const newChannel = ref("");
const deleteTarget = ref("");
const generatingChannels = ref<Set<string>>(new Set());

const columns: DataTableColumns = [
  { title: "#", key: "index", width: 60, render: (_, i) => i + 1 },
  { title: "频道", key: "url", render: (row) => getChannelName(row.url as string) },
  {
    title: "定时任务", key: "has_schedule", width: 100,
    render: (row) => h(NTag, { type: row.has_schedule ? 'success' : 'default', size: 'small' }, () => row.has_schedule ? '已配置' : '未配置'),
  },
  {
    title: "投票设置", key: "has_poll_settings", width: 100,
    render: (row) => h(NTag, { type: row.has_poll_settings ? 'success' : 'default', size: 'small' }, () => row.has_poll_settings ? '已配置' : '未配置'),
  },
  {
    title: "操作", key: "actions", width: 180,
    render: (row) => {
      const url = String(row.url);
      const isGenerating = generatingChannels.value.has(url);
      return h(NSpace, { size: 'small' }, () => [
        h(NButton, {
          size: 'small', type: 'primary', quaternary: true,
          loading: isGenerating,
          disabled: isGenerating,
          onClick: () => handleGenerate(url),
        }, () => '生成总结'),
        h(NButton, {
          size: 'small', type: 'error', quaternary: true,
          onClick: () => { deleteTarget.value = url; showDeleteModal.value = true; },
        }, () => '删除'),
      ]);
    },
  },
];

async function loadData() {
  loading.value = true;
  try {
    const res = await getChannels();
    if (res.success) channels.value = res.data.channels;
  } catch {
    message.error("加载频道列表失败");
  } finally {
    loading.value = false;
  }
}

async function handleAdd() {
  if (!newChannel.value.trim()) {
    message.warning("请输入频道 URL");
    return false;
  }
  try {
    const res = await addChannel(newChannel.value.trim());
    if (res.success) {
      message.success(res.message);
      newChannel.value = "";
      await loadData();
    } else {
      message.error(res.message);
    }
  } catch {
    message.error("添加频道失败");
  }
  return true;
}

async function handleGenerate(channelUrl: string) {
  generatingChannels.value.add(channelUrl);
  try {
    const res = await generateSummary(channelUrl);
    if (res.success) {
      message.success(res.message || `总结生成成功`);
    } else {
      message.error(res.message || "总结生成失败");
    }
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "生成总结请求失败";
    message.error(msg);
  } finally {
    generatingChannels.value.delete(channelUrl);
  }
}

async function handleDelete() {
  try {
    const res = await deleteChannel(deleteTarget.value);
    if (res.success) {
      message.success(res.message);
      showDeleteModal.value = false;
      await loadData();
    } else {
      message.error(res.message);
    }
  } catch {
    message.error("删除频道失败");
  }
}

onMounted(loadData);
</script>
