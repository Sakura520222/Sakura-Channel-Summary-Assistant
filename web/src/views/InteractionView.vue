<template>
  <n-spin :show="loading" description="加载中...">
  <div>
    <n-tabs type="line" animated>
      <!-- 投票设置 -->
      <n-tab-pane name="poll" tab="投票设置">
        <n-card title="投票功能">
          <n-descriptions bordered :column="1" label-placement="left" size="small">
            <n-descriptions-item label="投票功能">
              <n-tag :type="pollSettings.enable_poll ? 'success' : 'default'" size="small">
                {{ pollSettings.enable_poll ? '已启用' : '已禁用' }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="重新生成阈值">{{ pollSettings.poll_regen_threshold }}</n-descriptions-item>
          </n-descriptions>

          <n-divider>频道投票配置</n-divider>
          <n-empty v-if="!Object.keys(pollSettings.settings || {}).length" description="暂无频道投票配置" />
          <n-list v-else>
            <n-list-item v-for="(setting, channel) in pollSettings.settings" :key="String(channel)">
              <n-thing :title="getChannelName(String(channel))">
                <template #description>
                  <n-space>
                    <n-tag :type="(setting as any).enabled ? 'success' : 'default'" size="small">
                      {{ (setting as any).enabled ? '已启用' : '已禁用' }}
                    </n-tag>
                    <n-tag v-if="(setting as any).send_to_channel" size="small">发送到频道</n-tag>
                  </n-space>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
        </n-card>
      </n-tab-pane>

      <!-- 自动投票 -->
      <n-tab-pane name="auto-poll" tab="自动投票">
        <n-card title="自动投票">
          <template #header-extra>
            <n-switch v-model:value="autoPollEnabled" @update:value="handleAutoPollToggle">
              <template #checked>已启用</template>
              <template #unchecked>已禁用</template>
            </n-switch>
          </template>
          <n-empty v-if="!Object.keys(autoPollChannelSettings || {}).length"
            description="暂无频道自动投票配置" />
          <n-list v-else>
            <n-list-item v-for="(setting, channel) in autoPollChannelSettings" :key="String(channel)">
              <n-thing :title="getChannelName(String(channel))">
                <template #description>
                  <n-tag :type="(setting as any).enabled ? 'success' : 'default'" size="small">
                    {{ (setting as any).enabled ? '已启用' : '已禁用' }}
                  </n-tag>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
        </n-card>
      </n-tab-pane>

      <!-- 评论区欢迎 -->
      <n-tab-pane name="welcome" tab="评论区欢迎">
        <n-card title="评论区欢迎配置">
          <n-form label-placement="left" label-width="120">
            <n-form-item label="启用">
              <n-switch v-model:value="welcomeConfig.enabled" />
            </n-form-item>
            <n-form-item label="欢迎消息">
              <n-input v-model:value="welcomeConfig.welcome_message" type="textarea" :rows="2" />
            </n-form-item>
            <n-form-item label="按钮文本">
              <n-input v-model:value="welcomeConfig.button_text" />
            </n-form-item>
            <n-form-item label="按钮动作">
              <n-select v-model:value="welcomeConfig.button_action"
                :options="[{ label: '申请总结', value: 'request_summary' }]" />
            </n-form-item>
            <n-form-item>
              <n-button type="primary" :loading="savingWelcome" @click="saveWelcomeConfig">保存配置</n-button>
            </n-form-item>
          </n-form>
        </n-card>
      </n-tab-pane>
    </n-tabs>
  </div>
  </n-spin>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useMessage } from "naive-ui";
import {
  getPollSettings, getAutoPollSettings, updateAutoPoll,
  getCommentWelcomeConfig, updateDefaultCommentWelcome,
} from "@/api/modules";
import { getChannelName } from "@/utils/formatters";

const message = useMessage();
const loading = ref(true);
const pollSettings = ref<Record<string, unknown>>({});
const autoPollEnabled = ref(false);
const autoPollChannelSettings = ref<Record<string, unknown>>({});
const savingWelcome = ref(false);

const welcomeConfig = reactive({
  enabled: true,
  welcome_message: "",
  button_text: "",
  button_action: "request_summary",
});

async function loadData() {
  loading.value = true;
  try {
    const [pollRes, autoPollRes, welcomeRes] = await Promise.all([
      getPollSettings(), getAutoPollSettings(), getCommentWelcomeConfig(),
    ]);
    if (pollRes.success) pollSettings.value = pollRes.data;
    if (autoPollRes.success) {
      autoPollEnabled.value = autoPollRes.data.enabled;
      autoPollChannelSettings.value = autoPollRes.data.channel_settings;
    }
    if (welcomeRes.success) {
      const def = welcomeRes.data.default || {};
      welcomeConfig.enabled = def.enabled ?? true;
      welcomeConfig.welcome_message = def.welcome_message ?? "";
      welcomeConfig.button_text = def.button_text ?? "";
      welcomeConfig.button_action = def.button_action ?? "request_summary";
    }
  } catch {
    message.error("加载数据失败");
  } finally {
    loading.value = false;
  }
}

async function handleAutoPollToggle(enabled: boolean) {
  try {
    const res = await updateAutoPoll(enabled);
    message[res.success ? "success" : "error"](res.message);
  } catch {
    message.error("操作失败");
  }
}

async function saveWelcomeConfig() {
  savingWelcome.value = true;
  try {
    const res = await updateDefaultCommentWelcome({ ...welcomeConfig });
    message[res.success ? "success" : "error"](res.message);
  } catch {
    message.error("保存失败");
  } finally {
    savingWelcome.value = false;
  }
}

onMounted(loadData);
</script>
