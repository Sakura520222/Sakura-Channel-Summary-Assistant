<template>
  <n-spin :show="loading" description="加载中...">
    <div>
      <!-- 表概览卡片 -->
      <n-grid v-if="!activeTable" :cols="4" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
        <n-gi v-for="t in tables" :key="t.table_name" span="0:2 640:1">
          <n-card hoverable class="table-card" @click="selectTable(t.table_name)">
            <n-statistic :label="t.table_name">
              <template #prefix>
                <span class="table-emoji">📋</span>
              </template>
              {{ t.table_rows }}
            </n-statistic>
            <template #footer>
              <n-space justify="space-between" align="center">
                <n-text depth="3">{{ t.engine }} · {{ t.data_size_mb }} MB</n-text>
                <n-button text type="primary" size="small">浏览数据 →</n-button>
              </n-space>
            </template>
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 数据浏览区 -->
      <div v-if="activeTable">
        <n-page-header @back="activeTable = null" title="" class="mb-md">
          <template #title>
            <n-text strong>{{ activeTable }}</n-text>
            <n-text depth="3" style="font-size: 13px; margin-left: 8px">
              {{ schema?.columns?.length ?? 0 }} 列 · {{ totalRows }} 行
            </n-text>
          </template>
          <template #extra>
            <n-space>
              <n-button size="small" @click="handleRefresh">刷新</n-button>
              <n-button size="small" type="primary" @click="openCreateModal">新增行</n-button>
            </n-space>
          </template>
        </n-page-header>

        <!-- 搜索栏 -->
        <n-card class="mb-md">
          <n-space align="center">
            <n-select
              v-model:value="searchColumn"
              :options="columnOptions"
              placeholder="选择列"
              clearable
              style="width: 180px"
            />
            <n-input
              v-model:value="searchKeyword"
              placeholder="输入关键词..."
              clearable
              style="width: 240px"
              @keyup.enter="handleSearch"
            />
            <n-button type="primary" @click="handleSearch">搜索</n-button>
            <n-button @click="handleClearSearch">清除</n-button>
          </n-space>
        </n-card>

        <!-- 数据表格 -->
        <n-data-table
          :columns="dataColumns"
          :data="rows"
          :bordered="false"
          :loading="loadingRows"
          :remote="true"
          :pagination="pagination"
          :row-key="getRowKey"
          :scroll-x="scrollX"
          @update:page="handlePageChange"
          @update:sorter="handleSorterChange"
        />
      </div>

      <!-- 编辑/新增弹窗 -->
      <n-modal v-model:show="showEditModal" preset="card" :title="editModalTitle" style="width: 600px">
        <n-spin :show="saving">
          <n-form ref="editFormRef" label-placement="left" label-width="auto">
            <n-form-item
              v-for="col in editableColumns"
              :key="col.field"
              :label="col.field"
            >
              <template #label>
                <n-text>{{ col.field }}</n-text>
                <n-text depth="3" style="font-size: 12px; margin-left: 4px">
                  {{ col.type }}
                </n-text>
              </template>
              <n-input
                v-if="isTextType(col.type)"
                v-model:value="editForm[col.field]"
                type="textarea"
                :autosize="{ minRows: 1, maxRows: 6 }"
                :placeholder="col.default !== null ? String(col.default) : 'NULL'"
              />
              <n-input-number
                v-else-if="isNumberType(col.type)"
                v-model:value="editForm[col.field]"
                :placeholder="col.default !== null ? String(col.default) : 'NULL'"
                style="width: 100%"
              />
              <n-switch
                v-else-if="isBooleanType(col.type)"
                v-model:value="editForm[col.field]"
              />
              <n-input
                v-else
                v-model:value="editForm[col.field]"
                :placeholder="col.default !== null ? String(col.default) : 'NULL'"
              />
            </n-form-item>
          </n-form>
        </n-spin>
        <template #action>
          <n-space justify="end">
            <n-button @click="showEditModal = false">取消</n-button>
            <n-button type="primary" :loading="saving" @click="handleSaveRow">保存</n-button>
          </n-space>
        </template>
      </n-modal>

      <!-- 行详情弹窗 -->
      <n-modal v-model:show="showDetailModal" preset="card" title="行详情" style="width: 700px">
        <n-descriptions bordered :column="1" label-placement="left">
          <n-descriptions-item v-for="(val, key) in detailRow" :key="String(key)" :label="String(key)">
            <template v-if="isObjectValue(val)">
              <n-code :code="JSON.stringify(val, null, 2)" language="json" word-wrap />
            </template>
            <template v-else>
              {{ val === null ? "NULL" : String(val) }}
            </template>
          </n-descriptions-item>
        </n-descriptions>
      </n-modal>
    </div>
  </n-spin>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from "vue";
import { useMessage, useDialog, NButton, NSpace, NTag, NPopconfirm } from "naive-ui";
import type { DataTableColumns, DataTableSortState } from "naive-ui";
import {
  getDatabaseTables,
  getTableSchema,
  getTableRows,
  createTableRow,
  updateTableRow,
  deleteTableRow,
} from "@/api/modules";
import type { TableInfo, TableColumn, TableSchema, TableRowsData } from "@/api/modules";

const message = useMessage();
const dialog = useDialog();

// ── 表概览 ────────────────────────────────────────
const loading = ref(true);
const tables = ref<TableInfo[]>([]);
const activeTable = ref<string | null>(null);

// ── 表结构 ────────────────────────────────────────
const schema = ref<TableSchema | null>(null);

// ── 数据浏览 ────────────────────────────────────────
const rows = ref<Record<string, unknown>[]>([]);
const totalRows = ref(0);
const loadingRows = ref(false);
const searchColumn = ref<string | null>(null);
const searchKeyword = ref<string | null>(null);
const orderBy = ref<string | null>(null);
const orderDir = ref<"ASC" | "DESC">("ASC");
const pagination = ref({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  showSizePicker: false,
});

// ── 编辑弹窗 ────────────────────────────────────────
const showEditModal = ref(false);
const editMode = ref<"create" | "edit">("create");
const editForm = ref<Record<string, unknown>>({});
const editingPk = ref<string | number | null>(null);
const saving = ref(false);

// ── 行详情弹窗 ──────────────────────────────────────
const showDetailModal = ref(false);
const detailRow = ref<Record<string, unknown>>({});

// ── 计算属性 ────────────────────────────────────────

const editModalTitle = computed(() =>
  editMode.value === "create" ? "新增行" : "编辑行"
);

const columnOptions = computed(() =>
  (schema.value?.columns ?? []).map((c) => ({
    label: `${c.field} (${c.type})`,
    value: c.field,
  }))
);

const primaryKey = computed(() => schema.value?.primary_key ?? null);

const editableColumns = computed(() => {
  const cols = schema.value?.columns ?? [];
  if (editMode.value === "create") return cols;
  // 编辑时排除自增主键
  const pk = primaryKey.value;
  return cols.filter((c) => c.field !== pk || !c.extra.includes("auto_increment"));
});

const scrollX = computed(() => {
  const colCount = schema.value?.columns?.length ?? 0;
  return colCount > 8 ? colCount * 140 : undefined;
});

const dataColumns = computed<DataTableColumns>(() => {
  const cols = schema.value?.columns ?? [];
  if (cols.length === 0) return [];

  const columns: DataTableColumns = [
    ...cols.map((col) => ({
      title: col.field,
      key: col.field,
      width: _columnWidth(col),
      ellipsis: { tooltip: true },
      sorter: "default" as const,
      render: (row: Record<string, unknown>) => {
        const val = row[col.field];
        if (val === null || val === undefined) return h(NTag, { size: "small", type: "default" }, () => "NULL");
        const str = String(val);
        return str.length > 60 ? str.substring(0, 60) + "..." : str;
      },
    })),
    {
      title: "操作",
      key: "_actions",
      width: 180,
      fixed: "right",
      render: (row: Record<string, unknown>) => {
        const pk = primaryKey.value;
        const pkVal = pk ? row[pk] : null;
        return h(NSpace, { size: "small" }, () => [
          h(NButton, { size: "small", quaternary: true, onClick: () => openDetailModal(row) }, () => "详情"),
          pk && pkVal !== undefined
            ? h(
                NButton,
                { size: "small", quaternary: true, type: "primary", onClick: () => openEditModal(row) },
                () => "编辑"
              )
            : null,
          pk && pkVal !== undefined
            ? h(
                NPopconfirm,
                { onPositiveClick: () => handleDeleteRow(pkVal) },
                {
                  trigger: () =>
                    h(NButton, { size: "small", quaternary: true, type: "error" }, () => "删除"),
                  default: () => `确认删除主键为 ${String(pkVal)} 的行？`,
                }
              )
            : null,
        ]);
      },
    },
  ];
  return columns;
});

// ── 方法 ──────────────────────────────────────────

function _columnWidth(col: TableColumn): number {
  const t = col.type.toLowerCase();
  if (t.includes("bigint") || t.includes("int")) return 100;
  if (t.includes("datetime") || t.includes("timestamp")) return 170;
  if (t.includes("date")) return 110;
  if (t.includes("bool") || t.includes("tinyint(1)")) return 80;
  if (t === "json") return 160;
  if (t.includes("varchar")) return 160;
  return 160;
}

function isTextType(type: string): boolean {
  const t = type.toLowerCase();
  return t.includes("text") || t.includes("varchar") || t.includes("char") || t === "json";
}

function isNumberType(type: string): boolean {
  const t = type.toLowerCase();
  return t.includes("int") && !t.includes("tinyint(1)");
}

function isBooleanType(type: string): boolean {
  return type.toLowerCase().includes("tinyint(1)") || type.toLowerCase().includes("bool");
}

function isObjectValue(val: unknown): boolean {
  return typeof val === "object" && val !== null;
}

function getRowKey(row: Record<string, unknown>): unknown {
  const pk = primaryKey.value;
  if (pk && row[pk] !== undefined) return row[pk];
  return JSON.stringify(row);
}

// ── 数据加载 ──────────────────────────────────────

async function loadTables() {
  loading.value = true;
  try {
    const res = await getDatabaseTables();
    if (res.success) {
      tables.value = res.data || [];
    } else {
      message.error(res.message || "加载表列表失败");
    }
  } catch {
    message.error("加载表列表失败");
  } finally {
    loading.value = false;
  }
}

async function selectTable(tableName: string) {
  activeTable.value = tableName;
  pagination.value.page = 1;
  searchColumn.value = null;
  searchKeyword.value = null;
  orderBy.value = null;
  orderDir.value = "ASC";

  // 加载表结构
  try {
    const res = await getTableSchema(tableName);
    if (res.success) {
      schema.value = res.data;
    }
  } catch {
    message.error("加载表结构失败");
  }

  // 加载数据
  await loadRows();
}

async function loadRows() {
  if (!activeTable.value) return;
  loadingRows.value = true;
  try {
    const res = await getTableRows(activeTable.value, {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      search_column: searchColumn.value,
      search_keyword: searchKeyword.value,
      order_by: orderBy.value,
      order_dir: orderDir.value,
    });
    if (res.success) {
      const data: TableRowsData = res.data;
      rows.value = data.rows || [];
      totalRows.value = data.total;
      pagination.value.itemCount = data.total;
    }
  } catch {
    message.error("加载数据失败");
  } finally {
    loadingRows.value = false;
  }
}

function handleRefresh() {
  loadRows();
}

function handlePageChange(page: number) {
  pagination.value.page = page;
  loadRows();
}

function handleSorterChange(sorter: DataTableSortState) {
  if (sorter && sorter.columnKey) {
    orderBy.value = String(sorter.columnKey);
    orderDir.value = sorter.order === "descend" ? "DESC" : "ASC";
  } else {
    orderBy.value = null;
    orderDir.value = "ASC";
  }
  pagination.value.page = 1;
  loadRows();
}

function handleSearch() {
  pagination.value.page = 1;
  loadRows();
}

function handleClearSearch() {
  searchColumn.value = null;
  searchKeyword.value = null;
  pagination.value.page = 1;
  loadRows();
}

// ── 行详情 ────────────────────────────────────────

function openDetailModal(row: Record<string, unknown>) {
  detailRow.value = { ...row };
  showDetailModal.value = true;
}

// ── 新增行 ────────────────────────────────────────

function openCreateModal() {
  editMode.value = "create";
  editingPk.value = null;
  editForm.value = {};
  showEditModal.value = true;
}

// ── 编辑行 ────────────────────────────────────────

function openEditModal(row: Record<string, unknown>) {
  editMode.value = "edit";
  const pk = primaryKey.value;
  editingPk.value = pk ? (row[pk] as string | number) : null;
  editForm.value = { ...row };
  showEditModal.value = true;
}

// ── 保存行 ────────────────────────────────────────

async function handleSaveRow() {
  if (!activeTable.value) return;
  saving.value = true;
  try {
    // 过滤掉 undefined 值
    const data: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(editForm.value)) {
      if (value !== undefined) {
        data[key] = value === "" ? null : value;
      }
    }

    if (editMode.value === "create") {
      const res = await createTableRow(activeTable.value, data);
      if (res.success) {
        message.success(res.message || "新增成功");
        showEditModal.value = false;
        await loadRows();
      } else {
        message.error(res.message || "新增失败");
      }
    } else {
      if (editingPk.value === null) {
        message.error("无法确定主键");
        return;
      }
      const res = await updateTableRow(activeTable.value, editingPk.value, data);
      if (res.success) {
        message.success(res.message || "更新成功");
        showEditModal.value = false;
        await loadRows();
      } else {
        message.error(res.message || "更新失败");
      }
    }
  } catch {
    message.error("操作失败");
  } finally {
    saving.value = false;
  }
}

// ── 删除行 ────────────────────────────────────────

async function handleDeleteRow(pkValue: unknown) {
  if (!activeTable.value || pkValue === undefined) return;
  try {
    const res = await deleteTableRow(activeTable.value, pkValue as string | number);
    if (res.success) {
      message.success(res.message || "删除成功");
      await loadRows();
    } else {
      message.error(res.message || "删除失败");
    }
  } catch {
    message.error("删除失败");
  }
}

// ── 初始化 ────────────────────────────────────────

onMounted(loadTables);
</script>

<style scoped>
.table-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.table-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.table-emoji {
  font-size: 14px;
}
</style>
