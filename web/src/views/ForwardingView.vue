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

      <n-spin :show="loading" description="加载中...">
        <n-data-table :columns="columns" :data="rules" :bordered="false" />
      </n-spin>
    </n-card>

    <!-- 添加/编辑规则弹窗 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="editingIndex >= 0 ? '编辑规则' : '添加规则'"
      class="modal-responsive" positive-text="保存" negative-text="取消" @positive-click="handleSaveRule">
      <n-form label-placement="left" label-width="120">
        <n-form-item label="源频道">
          <n-select
            v-model:value="ruleForm.source_channel"
            :options="sourceChannelOptions"
            :loading="sourceChannelsLoading"
            clearable
            filterable
            tag
            placeholder="选择 UserBot 已加入频道，或手动输入频道链接/ID"
          />
          <template #feedback>
            候选项来自 UserBot 已加入频道；列表为空时可手动输入。
          </template>
        </n-form-item>
        <n-form-item label="目标频道">
          <n-select
            v-model:value="ruleForm.target_channel"
            :options="targetChannelOptions"
            :loading="targetChannelsLoading"
            clearable
            filterable
            tag
            placeholder="选择机器人管理频道，或手动输入频道链接/ID"
          />
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
        <n-form-item label="页脚模板">
          <n-select
            :options="footerTemplateOptions"
            clearable
            placeholder="选择模板并填入自定义页脚"
            @update:value="applyFooterTemplate"
          />
          <template #feedback>
            留空自定义页脚将使用全局默认底栏；模板可继续手动编辑。
          </template>
        </n-form-item>
        <n-form-item label="自定义页脚">
          <n-input
            v-model:value="ruleForm.custom_footer"
            type="textarea"
            :rows="3"
            :placeholder="defaultFooterTemplate"
          />
        </n-form-item>
        <n-form-item label="占位符">
          <n-space size="small" vertical>
            <n-space size="small">
              <n-tooltip
                v-for="placeholder in footerPlaceholders"
                :key="placeholder.value"
              >
                <template #trigger>
                  <n-tag
                    size="small"
                    class="cursor-pointer"
                    @click="insertFooterPlaceholder(placeholder.value)"
                  >
                    {{ placeholder.value }}
                  </n-tag>
                </template>
                {{ placeholder.description }}
              </n-tooltip>
            </n-space>
            <n-text depth="3" class="placeholder-help">
              点击标签可追加到自定义页脚，悬停查看说明。
            </n-text>
          </n-space>
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
import { ref, reactive, computed, onMounted, h } from "vue";
import { NButton, NTag, NSpace, NTooltip, useMessage } from "naive-ui";
import type { DataTableColumns, SelectOption } from "naive-ui";
import {
  addForwardingRule,
  deleteForwardingRule,
  getChannels,
  getForwardingConfig,
  toggleForwarding,
  updateForwardingRule,
  userBotListChannels,
  type ChannelInfo,
  type UserBotChannel,
} from "@/api/modules";
import { getChannelName } from "@/utils/formatters";

const message = useMessage();
const loading = ref(true);
const forwardingEnabled = ref(false);
const rules = ref<Array<Record<string, unknown>>>([]);
const showModal = ref(false);
const showDeleteModal = ref(false);
const editingIndex = ref(-1);
const deleteIndex = ref(-1);
const sourceChannelsLoading = ref(false);
const targetChannelsLoading = ref(false);
const userbotChannels = ref<UserBotChannel[]>([]);
const targetChannels = ref<string[]>([]);

const ruleForm = reactive({
  source_channel: "",
  target_channel: "",
  copy_mode: false,
  keywords: [] as string[],
  blacklist: [] as string[],
  custom_footer: "",
});

const footerTemplates = [
  {
    label: "全局默认",
    value: "[Source]({source_link}) {target_channel}\n🌸[助推](https://t.me/boost/{target_channel}) | {assistant_bot} | {submission}",
  },
  {
    label: "简洁来源",
    value: "📢 来源: {source_title}\n🔗 {source_link}",
  },
  {
    label: "频道署名",
    value: "Source: {source_title} | {source_link}",
  },
  {
    label: "完整信息",
    value: "📌 来源频道: {source_title}\n🎯 目标频道: {target_title}\n🆔 消息 ID: {message_id}\n🔗 原文: {source_link}",
  },
  {
    label: "仅原文链接",
    value: "🔗 {source_link}",
  },
  {
    label: "清空自定义页脚",
    value: "",
  },
];

const defaultFooterTemplate = footerTemplates[0].value;

const footerTemplateOptions = footerTemplates.map((template) => ({
  label: template.label,
  value: template.value,
}));

const footerPlaceholders = [
  { value: "{source_link}", description: "源消息链接" },
  { value: "{source_title}", description: "源频道名称" },
  { value: "{target_title}", description: "目标频道名称" },
  { value: "{source_channel}", description: "源频道 ID" },
  { value: "{target_channel}", description: "目标频道用户名或 ID" },
  { value: "{message_id}", description: "消息 ID" },
  { value: "{assistant_bot}", description: "助手 BOT 链接" },
  { value: "{submission}", description: "投稿链接" },
];

const sourceChannelOptions = computed<SelectOption[]>(() => {
  const options = userbotChannels.value.map((channel) => {
    const value = getUserBotChannelValue(channel);
    const label = channel.username
      ? `${channel.title} (@${channel.username})`
      : `${channel.title} (ID: ${channel.id})`;

    return { label, value };
  });

  return dedupeOptions(options);
});

const targetChannelOptions = computed<SelectOption[]>(() =>
  dedupeOptions(targetChannels.value.map((channel) => ({
    label: getChannelName(channel),
    value: channel,
  })))
);

function getUserBotChannelValue(channel: UserBotChannel) {
  if (channel.username) return `https://t.me/${channel.username}`;
  return `-100${channel.id}`;
}

function dedupeOptions(options: SelectOption[]) {
  const seen = new Set<string>();
  return options.filter((option) => {
    const value = String(option.value || "");
    if (!value || seen.has(value)) return false;
    seen.add(value);
    return true;
  });
}

function applyFooterTemplate(value: string | null) {
  if (value === null) return;
  ruleForm.custom_footer = value;
}

function insertFooterPlaceholder(placeholder: string) {
  ruleForm.custom_footer = ruleForm.custom_footer
    ? `${ruleForm.custom_footer}${/\s$/.test(ruleForm.custom_footer) ? "" : " "}${placeholder}`
    : placeholder;
}

const columns: DataTableColumns = [
  { title: "#", key: "index", width: 50, render: (_, i) => i + 1 },
  {
    title: "源频道", key: "source",
    render: (row) => getChannelName(row.source_channel as string),
  },
  {
    title: "目标频道", key: "target",
    render: (row) => getChannelName(row.target_channel as string),
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
  if (!ruleForm.source_channel.trim() || !ruleForm.target_channel.trim()) {
    message.warning("请选择或输入源频道和目标频道");
    return false;
  }

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
  loading.value = true;
  try {
    const res = await getForwardingConfig();
    if (res.success) {
      forwardingEnabled.value = res.data.enabled;
      rules.value = res.data.rules || [];
    }
  } catch {
    message.error("加载转发配置失败");
  } finally {
    loading.value = false;
  }
}

async function loadSourceChannels() {
  sourceChannelsLoading.value = true;
  try {
    const res = await userBotListChannels();
    if (res.success) {
      userbotChannels.value = res.channels || [];
    } else if (res.message) {
      message.warning(`UserBot 频道列表不可用：${res.message}`);
    }
  } catch {
    message.warning("加载 UserBot 已加入频道失败，可手动输入源频道");
  } finally {
    sourceChannelsLoading.value = false;
  }
}

async function loadTargetChannels() {
  targetChannelsLoading.value = true;
  try {
    const res = await getChannels();
    if (res.success) {
      targetChannels.value = (res.data.channels || []).map((channel: ChannelInfo) => channel.url);
    }
  } catch {
    message.warning("加载目标频道列表失败，可手动输入目标频道");
  } finally {
    targetChannelsLoading.value = false;
  }
}

onMounted(async () => {
  await Promise.all([loadData(), loadSourceChannels(), loadTargetChannels()]);
});
</script>
