import apiClient from "./client";

// ==================== 通用类型 ====================

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
}

// ==================== 认证 ====================

export async function loginWithToken(token: string) {
  const res = await apiClient.post("/auth/login", { token });
  return res.data;
}

export async function checkAuthStatus() {
  const res = await apiClient.get("/auth/status");
  return res.data;
}

export async function refreshToken() {
  const res = await apiClient.post("/auth/refresh");
  return res.data;
}

// ==================== 频道管理 ====================

export interface ChannelInfo {
  url: string;
  has_schedule: boolean;
  has_poll_settings: boolean;
}

export async function getChannels() {
  const res = await apiClient.get("/channels");
  return res.data;
}

export async function addChannel(channelUrl: string) {
  const res = await apiClient.post("/channels", { channel_url: channelUrl });
  return res.data;
}

export async function deleteChannel(channelUrl: string) {
  const res = await apiClient.delete("/channels", { data: { channel_url: channelUrl } });
  return res.data;
}

// ==================== AI 配置 ====================

export interface AIConfig {
  base_url: string;
  model: string;
  api_key_set: boolean;
  api_key_preview: string;
}

export interface PromptInfo {
  prompt_type: string;
  content: string;
  is_default: boolean;
}

export async function getAIConfig() {
  const res = await apiClient.get("/ai/config");
  return res.data;
}

export async function updateAIConfig(data: Partial<AIConfig & { api_key?: string }>) {
  const res = await apiClient.put("/ai/config", data);
  return res.data;
}

export async function getPrompts() {
  const res = await apiClient.get("/ai/prompts");
  return res.data;
}

export async function getPrompt(type: string) {
  const res = await apiClient.get(`/ai/prompts/${type}`);
  return res.data;
}

export async function updatePrompt(type: string, content: string) {
  const res = await apiClient.put(`/ai/prompts/${type}`, { content });
  return res.data;
}

export async function resetPrompt(type: string) {
  const res = await apiClient.post(`/ai/prompts/${type}/reset`);
  return res.data;
}

// ==================== 定时任务 ====================

export interface ScheduleInfo {
  channel: string;
  frequency: string;
  hour: number;
  minute: number;
  days: string[];
}

export async function getSchedules() {
  const res = await apiClient.get("/schedules");
  return res.data;
}

export async function getSchedule(channel: string) {
  const res = await apiClient.get(`/schedules/${encodeURIComponent(channel)}`);
  return res.data;
}

export async function updateSchedule(channel: string, data: Partial<ScheduleInfo>) {
  const res = await apiClient.put(`/schedules/${encodeURIComponent(channel)}`, data);
  return res.data;
}

export async function deleteSchedule(channel: string) {
  const res = await apiClient.delete(`/schedules/${encodeURIComponent(channel)}`);
  return res.data;
}

// ==================== 转发规则 ====================

export interface ForwardingRule {
  source_channel: string;
  target_channel: string;
  keywords?: string[];
  blacklist?: string[];
  patterns?: string[];
  blacklist_patterns?: string[];
  copy_mode?: boolean;
  forward_original_only?: boolean;
  custom_footer?: string;
}

export async function getForwardingConfig() {
  const res = await apiClient.get("/forwarding");
  return res.data;
}

export async function toggleForwarding(enabled: boolean) {
  const res = await apiClient.put("/forwarding/enabled", { enabled });
  return res.data;
}

export async function addForwardingRule(rule: ForwardingRule) {
  const res = await apiClient.post("/forwarding/rules", rule);
  return res.data;
}

export async function updateForwardingRule(index: number, rule: ForwardingRule) {
  const res = await apiClient.put(`/forwarding/rules/${index}`, rule);
  return res.data;
}

export async function deleteForwardingRule(index: number) {
  const res = await apiClient.delete(`/forwarding/rules/${index}`);
  return res.data;
}

// ==================== 系统运维 ====================

export interface BotStatus {
  status: string;
  version: string;
  log_level: string;
  channel_count: number;
  forwarding_enabled: boolean;
  qa_bot_running: boolean;
  userbot_connected: boolean;
}

export async function getSystemStatus() {
  const res = await apiClient.get("/system/status");
  return res.data;
}

export async function pauseBot() {
  const res = await apiClient.post("/system/pause");
  return res.data;
}

export async function resumeBot() {
  const res = await apiClient.post("/system/resume");
  return res.data;
}

export async function updateLogLevel(level: string) {
  const res = await apiClient.put("/system/log-level", { level });
  return res.data;
}

export async function restartBot() {
  const res = await apiClient.post("/system/restart");
  return res.data;
}

// ==================== 统计数据 ====================

export async function getStats() {
  const res = await apiClient.get("/stats");
  return res.data;
}

export async function getSummaries(channel?: string, limit?: number, offset?: number) {
  const params: Record<string, unknown> = {};
  if (channel) params.channel = channel;
  if (limit) params.limit = limit;
  if (offset) params.offset = offset;
  const res = await apiClient.get("/stats/summaries", { params });
  return res.data;
}

export async function getChannelRanking() {
  const res = await apiClient.get("/stats/ranking");
  return res.data;
}

// ==================== 互动设置 ====================

export async function getPollSettings() {
  const res = await apiClient.get("/interaction/poll-settings");
  return res.data;
}

export async function updateGlobalPollSettings(data: Record<string, unknown>) {
  const res = await apiClient.put("/interaction/poll-settings/global", data);
  return res.data;
}

export async function updatePollSettings(channel: string, data: Record<string, unknown>) {
  const res = await apiClient.put(`/interaction/poll-settings/${encodeURIComponent(channel)}`, data);
  return res.data;
}

export async function deletePollSettings(channel: string) {
  const res = await apiClient.delete(`/interaction/poll-settings/${encodeURIComponent(channel)}`);
  return res.data;
}

export async function getAutoPollSettings() {
  const res = await apiClient.get("/interaction/auto-poll");
  return res.data;
}

export async function updateAutoPoll(enabled: boolean) {
  const res = await apiClient.put("/interaction/auto-poll", { enabled });
  return res.data;
}

export async function updateChannelAutoPoll(channel: string, enabled: boolean) {
  const res = await apiClient.put(`/interaction/auto-poll/${encodeURIComponent(channel)}`, { enabled });
  return res.data;
}

export async function deleteChannelAutoPoll(channel: string) {
  const res = await apiClient.delete(`/interaction/auto-poll/${encodeURIComponent(channel)}`);
  return res.data;
}

export async function getInteractionChannels() {
  const res = await apiClient.get("/interaction/channels");
  return res.data;
}

export async function getCommentWelcomeConfig() {
  const res = await apiClient.get("/interaction/comment-welcome");
  return res.data;
}

export async function updateDefaultCommentWelcome(data: Record<string, unknown>) {
  const res = await apiClient.put("/interaction/comment-welcome/default", data);
  return res.data;
}

// ==================== UserBot ====================

export async function getUserBotStatus() {
  const res = await apiClient.get("/userbot/status");
  return res.data;
}

export async function userBotJoinChannel(channelUrl: string) {
  const res = await apiClient.post("/userbot/join", { channel_url: channelUrl });
  return res.data;
}

export async function userBotLeaveChannel(channelUrl: string) {
  const res = await apiClient.post("/userbot/leave", { channel_url: channelUrl });
  return res.data;
}

// ==================== 总结生成 ====================

export async function generateSummary(channel: string) {
  const res = await apiClient.post(`/summaries/${encodeURIComponent(channel)}/summarize`);
  return res.data;
}

// ==================== 仪表板 ====================

export async function getDashboard() {
  const res = await apiClient.get("/dashboard");
  return res.data;
}
