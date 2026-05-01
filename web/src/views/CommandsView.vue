<template>
  <div class="commands-view">
    <n-grid :cols="24" :x-gap="16" :y-gap="16" responsive="screen">
      <n-gi span="24 1024:8">
        <n-card title="命令目录" class="catalog-card">
          <n-space vertical>
            <n-input v-model:value="keyword" placeholder="搜索命令、说明或分类" clearable />
            <n-select v-model:value="riskFilter" :options="riskOptions" clearable placeholder="风险等级" />
            <n-alert type="info" :bordered="false">
              共 {{ catalogTotal }} 个命令，{{ executableCount }} 个可执行，{{ dangerCount }} 个高危。
            </n-alert>
            <n-spin :show="loading">
              <n-collapse accordion>
                <n-collapse-item
                  v-for="category in filteredCategories"
                  :key="category.category"
                  :title="`${category.category} (${category.commands.length})`"
                >
                  <n-list hoverable clickable>
                    <n-list-item
                      v-for="cmd in category.commands"
                      :key="cmd.operation_id"
                      :class="{ selected: selectedCommand?.operation_id === cmd.operation_id }"
                      @click="selectCommand(cmd)"
                    >
                      <n-space justify="space-between" align="center" :wrap-item="false">
                        <div class="command-row-main">
                          <div class="command-name">/{{ cmd.command }}</div>
                          <n-text depth="3" class="command-description">{{ cmd.description }}</n-text>
                        </div>
                        <n-space size="small" align="center">
                          <n-tag size="small" :type="riskTagType(cmd.risk)">{{ riskLabel(cmd.risk) }}</n-tag>
                          <n-tag v-if="!cmd.executable" size="small" type="default">目录</n-tag>
                        </n-space>
                      </n-space>
                    </n-list-item>
                  </n-list>
                </n-collapse-item>
              </n-collapse>
            </n-spin>
          </n-space>
        </n-card>
      </n-gi>

      <n-gi span="24 1024:16">
        <n-card v-if="selectedCommand" :title="`/${selectedCommand.command}`">
          <template #header-extra>
            <n-space>
              <n-tag :type="riskTagType(selectedCommand.risk)">{{ riskLabel(selectedCommand.risk) }}</n-tag>
              <n-tag v-if="selectedCommand.covered_by_page" type="info" size="small">
                已覆盖：{{ selectedCommand.covered_by_page }}
              </n-tag>
            </n-space>
          </template>

          <n-space vertical size="large">
            <n-text>{{ selectedCommand.description }}</n-text>

            <n-alert v-if="!selectedCommand.executable" type="warning" :bordered="false">
              该命令已展示在目录中，但暂未接入结构化执行。请使用对应 WebUI 页面或 Telegram 命令。
            </n-alert>

            <n-form v-if="selectedCommand.parameters.length" label-placement="left" label-width="130">
              <n-form-item
                v-for="param in selectedCommand.parameters"
                :key="param.name"
                :label="param.label"
                :required="param.required"
              >
                <n-input
                  v-if="param.type === 'string'"
                  v-model:value="formState[param.name]"
                  :placeholder="param.placeholder || param.description"
                />
                <n-input
                  v-else-if="param.type === 'textarea'"
                  v-model:value="formState[param.name]"
                  type="textarea"
                  :rows="4"
                  :placeholder="param.placeholder || param.description"
                />
                <n-input-number
                  v-else-if="param.type === 'number'"
                  v-model:value="formState[param.name]"
                  :placeholder="param.placeholder || param.description"
                />
                <n-switch v-else-if="param.type === 'boolean'" v-model:value="formState[param.name]" />
                <n-select
                  v-else-if="param.type === 'select'"
                  v-model:value="formState[param.name]"
                  :options="param.options || []"
                  :placeholder="param.placeholder || param.description"
                />
                <n-dynamic-tags v-else-if="param.type === 'tags'" v-model:value="formState[param.name]" />
              </n-form-item>
            </n-form>

            <n-alert v-if="selectedCommand.risk === 'danger'" type="error" :bordered="false">
              高危操作会改变运行状态或删除数据。执行前需要输入 {{ dangerConfirmText }} 二次确认。
            </n-alert>

            <n-space>
              <n-button
                type="primary"
                :disabled="!selectedCommand.executable"
                :loading="executing"
                @click="handleExecute"
              >
                执行命令
              </n-button>
              <n-button secondary @click="resetForm">重置参数</n-button>
            </n-space>

            <n-alert v-if="lastResult" :type="lastResult.success ? 'success' : 'error'" :bordered="false">
              {{ lastResult.message || (lastResult.success ? "执行成功" : "执行失败") }}
            </n-alert>

            <n-card v-if="lastResult" size="small" title="执行结果">
              <n-data-table
                v-if="resultChannels.length"
                :columns="channelColumns"
                :data="resultChannels"
                :bordered="false"
                size="small"
              />
              <n-log v-else :log="JSON.stringify(lastResult.data || {}, null, 2)" language="json" trim />
            </n-card>
          </n-space>
        </n-card>

        <n-empty v-else description="请选择一个命令" />
      </n-gi>
    </n-grid>

    <n-modal
      v-model:show="showDangerConfirm"
      preset="dialog"
      type="error"
      title="确认执行高危命令"
      positive-text="确认执行"
      negative-text="取消"
      @positive-click="executeSelectedDangerCommand"
    >
      <n-space vertical>
        <n-alert type="error" :bordered="false">
          即将执行 /{{ selectedCommand?.command }}。此操作可能中断服务或删除数据。
        </n-alert>
        <n-input v-model:value="confirmText" :placeholder="`请输入 ${dangerConfirmText}`" />
      </n-space>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useMessage } from "naive-ui";
import type { DataTableColumns, SelectOption } from "naive-ui";
import {
  executeCommand,
  getCommandCatalog,
  type CommandCategory,
  type CommandItem,
  type CommandRisk,
} from "@/api/modules";

const message = useMessage();
const loading = ref(false);
const executing = ref(false);
const categories = ref<CommandCategory[]>([]);
const selectedCommand = ref<CommandItem | null>(null);
const keyword = ref("");
const riskFilter = ref<CommandRisk | null>(null);
const catalogTotal = ref(0);
const executableCount = ref(0);
const dangerCount = ref(0);
const dangerConfirmText = ref("CONFIRM");
const showDangerConfirm = ref(false);
const confirmText = ref("");
const formState = reactive<Record<string, unknown>>({});
const lastResult = ref<{ success: boolean; message?: string; data?: unknown } | null>(null);

const channelColumns: DataTableColumns<Record<string, unknown>> = [
  { title: "#", key: "index", width: 56, render: (_row, index) => index + 1 },
  { title: "频道名", key: "title" },
  {
    title: "用户名",
    key: "username",
    render: (row) => (row.username ? `@${row.username}` : "-"),
  },
  { title: "ID", key: "id" },
];

const resultChannels = computed(() => {
  const data = lastResult.value?.data;
  if (!data || typeof data !== "object" || !("channels" in data)) return [];
  const channels = (data as { channels?: unknown }).channels;
  return Array.isArray(channels) ? channels as Record<string, unknown>[] : [];
});

const riskOptions: SelectOption[] = [
  { label: "安全", value: "safe" },
  { label: "普通", value: "normal" },
  { label: "高危", value: "danger" },
];

const filteredCategories = computed(() => {
  const q = keyword.value.trim().toLowerCase();
  return categories.value
    .map((category) => ({
      ...category,
      commands: category.commands.filter((cmd) => {
        const matchesRisk = !riskFilter.value || cmd.risk === riskFilter.value;
        const matchesKeyword = !q
          || cmd.command.toLowerCase().includes(q)
          || cmd.description.toLowerCase().includes(q)
          || category.category.toLowerCase().includes(q);
        return matchesRisk && matchesKeyword;
      }),
    }))
    .filter((category) => category.commands.length > 0);
});

function riskLabel(risk: CommandRisk) {
  const map: Record<CommandRisk, string> = {
    safe: "安全",
    normal: "普通",
    danger: "高危",
  };
  return map[risk];
}

function riskTagType(risk: CommandRisk) {
  if (risk === "danger") return "error";
  if (risk === "safe") return "success";
  return "warning";
}

function selectCommand(cmd: CommandItem) {
  selectedCommand.value = cmd;
  lastResult.value = null;
  resetForm();
}

function resetForm() {
  Object.keys(formState).forEach((key) => delete formState[key]);
  if (!selectedCommand.value) return;
  for (const param of selectedCommand.value.parameters) {
    if (param.default !== undefined && param.default !== null) {
      formState[param.name] = param.default;
    } else if (param.type === "boolean") {
      formState[param.name] = false;
    } else if (param.type === "tags") {
      formState[param.name] = [];
    } else {
      formState[param.name] = undefined;
    }
  }
}

function validateRequired() {
  if (!selectedCommand.value) return false;
  for (const param of selectedCommand.value.parameters) {
    if (!param.required) continue;
    const value = formState[param.name];
    if (value === undefined || value === null || value === "") {
      message.error(`缺少必填参数：${param.label}`);
      return false;
    }
  }
  return true;
}

async function handleExecute() {
  if (!selectedCommand.value || !validateRequired()) return;
  if (selectedCommand.value.risk === "danger") {
    confirmText.value = "";
    showDangerConfirm.value = true;
    return;
  }
  await executeSelectedCommand(false);
}

async function executeSelectedDangerCommand() {
  if (confirmText.value !== dangerConfirmText.value) {
    message.error(`请输入 ${dangerConfirmText.value} 以确认`);
    return false;
  }
  await executeSelectedCommand(true);
  return true;
}

async function executeSelectedCommand(confirm: boolean) {
  if (!selectedCommand.value) return;
  executing.value = true;
  try {
    const res = await executeCommand(selectedCommand.value.operation_id, {
      params: { ...formState },
      confirm,
      confirm_text: confirm ? confirmText.value : "",
    });
    lastResult.value = res;
    message[res.success ? "success" : "error"](res.message || (res.success ? "执行成功" : "执行失败"));
  } catch (error) {
    lastResult.value = { success: false, message: "执行失败", data: error };
    message.error("执行失败");
  } finally {
    executing.value = false;
  }
}

async function loadCatalog() {
  loading.value = true;
  try {
    const res = await getCommandCatalog();
    if (res.success) {
      categories.value = res.data.categories || [];
      catalogTotal.value = res.data.total || 0;
      executableCount.value = res.data.executable_count || 0;
      dangerCount.value = res.data.danger_count || 0;
      dangerConfirmText.value = res.data.danger_confirm_text || "CONFIRM";
      const firstExecutable = categories.value.flatMap((category) => category.commands).find((cmd) => cmd.executable);
      if (firstExecutable) selectCommand(firstExecutable);
    }
  } catch {
    message.error("加载命令目录失败");
  } finally {
    loading.value = false;
  }
}

onMounted(loadCatalog);
</script>

<style scoped>
.commands-view {
  min-height: 100%;
}
.catalog-card {
  position: sticky;
  top: 0;
}
.command-row-main {
  min-width: 0;
}
.command-name {
  font-weight: 700;
  color: var(--n-text-color);
}
.command-description {
  display: block;
  margin-top: 2px;
  font-size: 12px;
}
.selected {
  background: color-mix(in srgb, var(--n-primary-color) 10%, transparent);
  border-radius: 8px;
}
</style>
