<template>
  <div>
    <n-card title="转发规则管理">
      <template #header-extra>
        <n-space>
          <n-switch v-model:value="forwardingEnabled" @update:value="handleToggle">
            <template #checked>已启用</template>
            <template #unchecked>已禁用</template>
          </n-switch>
          <n-button type="primary" @click="openAddRule">添加规则</n-button>
        </n-space>
      </template>

      <n-data-table :columns="columns" :data="rules" :bordered="false" />
    </n-card>

    <!-- 添加/编辑规则弹窗 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="editingIndex >= 0 ? '编辑规则' : '添加规则'"
      style="width: 600px" positive-text="保存" negative-text="取消" @positive-click="handleSaveRule">
      <n-form label-placement="left" label-width="120">
        <n-form-item label="源频道">
          <n-input v-model:value="ruleForm.source_channel" placeholder="https://t.me/source_channel" />
        </n-form-item>
        <n-form-item label="目标频道">
          <n-input v-model:value="ruleForm.target_channel" placeholder="https://t.me/target_channel" />
        </n-form-item>
        <n-form-item label="复制模式">
          <n-switch v-model:value="ruleForm.copy_mode" />
        </n-form-item>
        <n-form-item label="关键词过滤">
          <n-dynamic-tags v-model:value="ruleForm.keywords" />
        </n-form-item>
        <n-form-item label="黑名单">
          <n-dynamic-tags v-model:value="ruleForm.blacklist" />
        </n-form-item>
        <n-form-item label="自定义页脚">
          <n-input v-model:value="ruleForm.custom_footer" type="textarea" :rows="2"
            placeholder="📢 来源: {source_title}\n🔗 {source_link}" />
        </n-form-item>
      </n-form>
    </n-modal>

    <!-- 删除确认 -->
    <n-modal v-model:show="showDeleteModal" preset="dialog" type="error" title="确认删除"
      positive-text="删除" negative-text="取消" @positive-click="handleDeleteRule">
      <p>确定要删除这条转发规则吗？</p>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from "vue";
import { NButton, NTag, NSpace, useMessage } from "naive-ui";
import type { DataTableColumns } from "naive-ui";
import {
  getForwardingConfig, toggleForwarding, addForwardingRule,
  updateForwardingRule, deleteForwardingRule,
} from "../api/modules";

const message = useMessage();
const forwardingEnabled = ref(false);
const rules = ref<Array<Record<string, unknown>>>([]);
const showModal = ref(false);
const showDeleteModal = ref(false);
const editingIndex = ref(-1);
const deleteIndex = ref(-1);

const ruleForm = reactive({
  source_channel: "",
  target_channel: "",
  copy_mode: false,
  keywords: [] as string[],
  blacklist: [] as string[],
  custom_footer: "",
});

const columns: DataTableColumns = [
  { title: "#", key: "index", width: 50, render: (_, i) => i + 1 },
  {
    title: "源频道", key: "source",
    render: (row) => (row.source_channel as string).replace("https://t.me/", "@"),
  },
  {
    title: "目标频道", key: "target",
    render: (row) => (row.target_channel as string).replace("https://t.me/", "@"),
  },
  {
    title: "模式", key: "mode", width: 80,
    render: (row) => h(NTag, { size: "small", type: row.copy_mode ? "info" : "default" }, () => row.copy_mode ? "复制" : "转发"),
  },
  {
    title: "关键词", key: "keywords", width: 200,
    render: (row) => {
      const kw = row.keywords as string[];
      if (!kw?.length) return "-";
      return h(NSpace, { size: 4 }, () => kw.map((k) => h(NTag, { size: "small" }, () => k)));
    },
  },
  {
    title: "操作", key: "actions", width: 150,
    render: (_, i) => [
      h(NButton, { size: "small", quaternary: true, onClick: () => editRule(i) }, () => "编辑"),
      h(NButton, { size: "small", type: "error", quaternary: true, onClick: () => { deleteIndex.value = i; showDeleteModal.value = true; } }, () => "删除"),
    ],
  },
];

function openAddRule() {
  editingIndex.value = -1;
  Object.assign(ruleForm, { source_channel: "", target_channel: "", copy_mode: false, keywords: [], blacklist: [], custom_footer: "" });
  showModal.value = true;
}

function editRule(index: number) {
  const rule = rules.value[index];
  editingIndex.value = index;
  Object.assign(ruleForm, {
    source_channel: rule.source_channel || "",
    target_channel: rule.target_channel || "",
    copy_mode: rule.copy_mode || false,
    keywords: (rule.keywords as string[]) || [],
    blacklist: (rule.blacklist as string[]) || [],
    custom_footer: rule.custom_footer || "",
  });
  showModal.value = true;
}

async function handleToggle(enabled: boolean) {
  try {
    const res = await toggleForwarding(enabled);
    message[res.success ? "success" : "error"](res.message);
  } catch {
    message.error("操作失败");
  }
}

async function handleSaveRule() {
  try {
    const data = { ...ruleForm, patterns: [], blacklist_patterns: [], forward_original_only: false };
    let res;
    if (editingIndex.value >= 0) {
      res = await updateForwardingRule(editingIndex.value, data);
    } else {
      res = await addForwardingRule(data);
    }
    message[res.success ? "success" : "error"](res.message);
    if (res.success) {
      showModal.value = false;
      await loadData();
    }
  } catch {
    message.error("保存失败");
  }
  return true;
}

async function handleDeleteRule() {
  try {
    const res = await deleteForwardingRule(deleteIndex.value);
    message[res.success ? "success" : "error"](res.message);
    if (res.success) await loadData();
  } catch {
    message.error("删除失败");
  }
}

async function loadData() {
  try {
    const res = await getForwardingConfig();
    if (res.success) {
      forwardingEnabled.value = res.data.enabled;
      rules.value = res.data.rules || [];
    }
  } catch {
    message.error("加载转发配置失败");
  }
}

onMounted(loadData);
</script>
