<template>
  <n-spin :show="loading" description="加载中...">
    <div>
      <!-- 统计卡片 -->
      <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
        <n-gi span="0:4 640:2 1024:1">
          <n-card>
            <n-statistic label="总结向量数">
              <template #prefix>📄</template>
              {{ stats.summaries?.total_vectors ?? 0 }}
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi span="0:4 640:2 1024:1">
          <n-card>
            <n-statistic label="消息向量数">
              <template #prefix>💬</template>
              {{ stats.messages?.total_vectors ?? 0 }}
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi span="0:4 640:2 1024:1">
          <n-card>
            <n-statistic label="总计向量数">
              <template #prefix>🔢</template>
              {{ totalVectors }}
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi span="0:4 640:2 1024:1">
          <n-card>
            <n-statistic label="存储状态">
              <template #prefix>
                <span :style="{ color: stats.available ? '#18a058' : '#d03050' }">●</span>
              </template>
              {{ stats.available ? '可用' : '不可用' }}
            </n-statistic>
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 语义搜索 -->
      <n-card title="语义搜索" class="mt-md">
        <n-space vertical>
          <n-space>
            <n-input
              v-model:value="searchQuery"
              placeholder="输入搜索文本..."
              class="flex-1"
              style="min-width: 300px"
              @keyup.enter="handleSearch"
            />
            <n-select
              v-model:value="searchCollection"
              :options="searchCollectionOptions"
              style="width: 140px"
            />
            <n-input-number v-model:value="searchTopK" :min="1" :max="50" style="width: 100px" />
            <n-button type="primary" :loading="searching" @click="handleSearch">搜索</n-button>
          </n-space>

          <n-data-table
            v-if="searchResults.length > 0"
            :columns="searchResultColumns"
            :data="searchResults"
            :bordered="false"
            :row-key="(row: VectorSearchResult) => row.doc_id"
          />
          <n-empty v-else-if="searchDone && searchResults.length === 0" description="未找到匹配结果" />
        </n-space>
      </n-card>

      <!-- 集合浏览 -->
      <n-card title="集合浏览" class="mt-md">
        <template #header-extra>
          <n-space>
            <n-select
              v-model:value="activeCollection"
              :options="collectionOptions"
              style="width: 160px"
              @update:value="handleCollectionChange"
            />
            <n-button @click="loadDocuments">刷新</n-button>
          </n-space>
        </template>

        <!-- 批量操作栏 -->
        <n-space v-if="checkedRowKeys.length > 0" class="mb-md" align="center">
          <n-text>已选中 {{ checkedRowKeys.length }} 项</n-text>
          <n-button type="error" size="small" @click="handleBatchDelete">
            批量删除
          </n-button>
          <n-button size="small" @click="checkedRowKeys = []">取消选择</n-button>
        </n-space>

        <n-data-table
          :columns="docColumns"
          :data="documents"
          :bordered="false"
          :loading="loadingDocs"
          :remote="true"
          :pagination="docPagination"
          :row-key="(row: VectorDocument) => row.id"
          :checked-row-keys="checkedRowKeys"
          @update:page="handleDocPageChange"
          @update:checked-row-keys="handleCheckChange"
        />
      </n-card>

      <!-- 文档详情弹窗 -->
      <n-modal v-model:show="showDetailModal" preset="card" title="文档详情" style="width: 700px">
        <n-spin :show="loadingDetail">
          <template v-if="currentDoc">
            <n-descriptions bordered :column="1" label-placement="left">
              <n-descriptions-item label="文档 ID">{{ currentDoc.id }}</n-descriptions-item>
              <n-descriptions-item label="向量维度">
                {{ currentDoc.embedding_dimension ?? '未知' }}
              </n-descriptions-item>
              <n-descriptions-item label="元数据">
                <n-code :code="JSON.stringify(currentDoc.metadata, null, 2)" language="json" word-wrap />
              </n-descriptions-item>
            </n-descriptions>

            <n-card title="文档内容" size="small" class="mt-md">
              <n-scrollbar style="max-height: 400px">
                <n-text>{{ currentDoc.document }}</n-text>
              </n-scrollbar>
            </n-card>
          </template>
        </n-spin>
      </n-modal>
    </div>
  </n-spin>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from "vue";
import { useMessage, useDialog, NButton, NSpace, NTag, NPopconfirm } from "naive-ui";
import type { DataTableColumns } from "naive-ui";
import {
  getVectorStats,
  listVectorDocuments,
  getVectorDocument,
  deleteVectorDocument,
  deleteVectorDocumentsBatch,
  searchVectors,
  clearVectorCollection,
} from "@/api/modules";
import type { VectorStats, VectorDocument, VectorSearchResult } from "@/api/modules";

const message = useMessage();
const dialog = useDialog();

// ── 统计 ───────────────────────────────────────────────
const loading = ref(true);
const stats = ref<VectorStats>({
  available: false,
  summaries: {},
  messages: {},
});

const totalVectors = computed(
  () =>
    (stats.value.summaries?.total_vectors ?? 0) + (stats.value.messages?.total_vectors ?? 0)
);

// ── 搜索 ───────────────────────────────────────────────
const searchQuery = ref("");
const searchCollection = ref<string>("all");
const searchTopK = ref(10);
const searching = ref(false);
const searchDone = ref(false);
const searchResults = ref<VectorSearchResult[]>([]);

const searchCollectionOptions = [
  { label: "全部", value: "all" },
  { label: "总结 (summaries)", value: "summaries" },
  { label: "消息 (messages)", value: "messages" },
];

const searchResultColumns: DataTableColumns<VectorSearchResult> = [
  {
    title: "来源",
    key: "source",
    width: 100,
    render: (row) =>
      h(
        NTag,
        { size: "small", type: row.source === "summary" ? "info" : "success" },
        { default: () => (row.source === "summary" ? "总结" : "消息") }
      ),
  },
  { title: "ID", key: "doc_id", width: 160, ellipsis: { tooltip: true } },
  {
    title: "相似度",
    key: "similarity",
    width: 100,
    render: (row) => `${(row.similarity * 100).toFixed(1)}%`,
  },
  {
    title: "内容",
    key: "summary_text",
    ellipsis: { tooltip: true },
    render: (row) => row.summary_text?.substring(0, 150) || "",
  },
  {
    title: "元数据",
    key: "metadata_channel",
    width: 120,
    render: (row) => {
      const ch = row.metadata?.channel_name || row.metadata?.channel_id || "";
      return ch ? ch.toString().substring(0, 20) : "-";
    },
  },
];

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    message.warning("请输入搜索文本");
    return;
  }
  searching.value = true;
  searchDone.value = false;
  try {
    const res = await searchVectors(
      searchQuery.value.trim(),
      searchCollection.value === "all" ? null : searchCollection.value,
      searchTopK.value
    );
    if (res.success) {
      searchResults.value = res.data.results || [];
      searchDone.value = true;
      message.success(`找到 ${searchResults.value.length} 个匹配结果`);
    } else {
      message.error(res.message || "搜索失败");
    }
  } catch {
    message.error("搜索请求失败");
  } finally {
    searching.value = false;
  }
}

// ── 集合浏览 ───────────────────────────────────────────
const activeCollection = ref("summaries");
const documents = ref<VectorDocument[]>([]);
const totalDocs = ref(0);
const loadingDocs = ref(false);
const checkedRowKeys = ref<string[]>([]);
const docPagination = ref({ page: 1, pageSize: 20, itemCount: 0 });

const collectionOptions = [
  { label: "总结 (summaries)", value: "summaries" },
  { label: "消息 (messages)", value: "messages" },
];

const docColumns: DataTableColumns<VectorDocument> = [
  { type: "selection" },
  {
    title: "ID",
    key: "id",
    width: 160,
    ellipsis: { tooltip: true },
  },
  {
    title: "内容",
    key: "document",
    ellipsis: { tooltip: true },
    render: (row) => {
      const text = row.document || "";
      return text.substring(0, 120) + (text.length > 120 ? "..." : "");
    },
  },
  {
    title: "频道",
    key: "channel",
    width: 140,
    render: (row) => {
      const ch = row.metadata?.channel_name || row.metadata?.channel_id || "";
      return ch ? ch.toString().substring(0, 20) : "-";
    },
  },
  {
    title: "创建时间",
    key: "created_at",
    width: 170,
    render: (row) => {
      const t = row.metadata?.created_at as string | undefined;
      return t ? new Date(t).toLocaleString("zh-CN") : "-";
    },
  },
  {
    title: "操作",
    key: "actions",
    width: 180,
    fixed: "right",
    render: (row) =>
      h(NSpace, { size: "small" }, () => [
        h(
          NButton,
          { size: "small", quaternary: true, onClick: () => viewDocument(row.id) },
          { default: () => "详情" }
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete(row.id) },
          {
            trigger: () =>
              h(NButton, { size: "small", type: "error", quaternary: true }, { default: () => "删除" }),
            default: () => "确定删除该文档？",
          }
        ),
      ]),
  },
];

function handleCollectionChange() {
  docPagination.value.page = 1;
  checkedRowKeys.value = [];
  loadDocuments();
}

function handleDocPageChange(page: number) {
  docPagination.value.page = page;
  loadDocuments();
}

function handleCheckChange(keys: string[]) {
  checkedRowKeys.value = keys;
}

async function loadDocuments() {
  loadingDocs.value = true;
  try {
    const { page, pageSize } = docPagination.value;
    const offset = (page - 1) * pageSize;
    const res = await listVectorDocuments(activeCollection.value, pageSize, offset);
    if (res.success) {
      documents.value = res.data.documents || [];
      totalDocs.value = res.data.total || 0;
      docPagination.value.itemCount = totalDocs.value;
    }
  } catch {
    message.error("加载文档列表失败");
  } finally {
    loadingDocs.value = false;
  }
}

// ── 文档详情 ───────────────────────────────────────────
const showDetailModal = ref(false);
const loadingDetail = ref(false);
const currentDoc = ref<VectorDocument | null>(null);

async function viewDocument(docId: string) {
  showDetailModal.value = true;
  loadingDetail.value = true;
  try {
    const res = await getVectorDocument(activeCollection.value, docId);
    if (res.success) {
      currentDoc.value = res.data;
    } else {
      message.error(res.message || "获取文档详情失败");
    }
  } catch {
    message.error("获取文档详情失败");
  } finally {
    loadingDetail.value = false;
  }
}

// ── 删除操作 ───────────────────────────────────────────
async function handleDelete(docId: string) {
  try {
    const res = await deleteVectorDocument(activeCollection.value, docId);
    if (res.success) {
      message.success(res.message || "删除成功");
      loadDocuments();
      loadStats();
    } else {
      message.error(res.message || "删除失败");
    }
  } catch {
    message.error("删除请求失败");
  }
}

async function handleBatchDelete() {
  dialog.warning({
    title: "批量删除确认",
    content: `确定要删除选中的 ${checkedRowKeys.value.length} 个文档吗？此操作不可恢复。`,
    positiveText: "确定删除",
    negativeText: "取消",
    onPositiveClick: async () => {
      try {
        const res = await deleteVectorDocumentsBatch(activeCollection.value, checkedRowKeys.value);
        if (res.success) {
          message.success(res.message || "批量删除成功");
          checkedRowKeys.value = [];
          loadDocuments();
          loadStats();
        } else {
          message.error(res.message || "批量删除失败");
        }
      } catch {
        message.error("批量删除请求失败");
      }
    },
  });
}

// ── 初始化 ─────────────────────────────────────────────
async function loadStats() {
  try {
    const res = await getVectorStats();
    if (res.success) {
      stats.value = res.data;
    }
  } catch {
    // 静默处理
  }
}

async function loadData() {
  loading.value = true;
  try {
    await Promise.all([loadStats(), loadDocuments()]);
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>
