/**
 * 公共工具函数
 */

/**
 * 从频道 URL 中提取显示名称
 * @param url 频道 URL 或 ID
 * @returns 格式化后的名称（如 @channel_name）
 */
export function getChannelName(url: string | undefined | null): string {
  if (!url) return "-";
  return String(url).replace("https://t.me/", "@");
}

/**
 * 格式化运行时长
 * @param seconds 总秒数
 * @returns 人类可读的时长字符串
 */
export function formatUptime(seconds: number | undefined): string {
  if (!seconds) return "未知";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 24) return `${Math.floor(h / 24)} 天 ${h % 24} 小时`;
  return `${h} 小时 ${m} 分钟`;
}
