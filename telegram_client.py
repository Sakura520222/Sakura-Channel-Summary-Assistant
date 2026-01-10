import logging
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN, CHANNELS, ADMIN_LIST, SEND_REPORT_TO_SOURCE
from error_handler import retry_with_backoff, record_error

logger = logging.getLogger(__name__)

# 全局变量，用于存储活动的Telegram客户端实例
_active_client = None

def set_active_client(client):
    """设置活动的Telegram客户端实例"""
    global _active_client
    _active_client = client
    logger.info("已设置活动的Telegram客户端实例")

def get_active_client():
    """获取活动的Telegram客户端实例"""
    return _active_client

@retry_with_backoff(
    max_retries=3,
    base_delay=2.0,
    max_delay=60.0,
    exponential_backoff=True,
    retry_on_exceptions=(ConnectionError, TimeoutError, Exception)
)
async def fetch_last_week_messages(channels_to_fetch=None, start_time=None, report_message_ids=None):
    """抓取指定时间范围的频道消息
    
    Args:
        channels_to_fetch: 可选，要抓取的频道列表。如果为None，则抓取所有配置的频道。
        start_time: 可选，开始抓取的时间。如果为None，则默认抓取过去一周的消息。
        report_message_ids: 可选，要排除的报告消息ID列表，按频道分组。
    """
    # 确保 API_ID 是整数
    logger.info("开始抓取指定时间范围的频道消息")
    
    async with TelegramClient('session_name', int(API_ID), API_HASH) as client:
        # 如果没有提供开始时间，则默认抓取过去一周的消息
        if start_time is None:
            start_time = datetime.now(timezone.utc) - timedelta(days=7)
            logger.info(f"未提供开始时间，默认抓取过去一周的消息")
        
        messages_by_channel = {}  # 按频道分组的消息字典
        report_message_ids = report_message_ids or {}
        
        # 确定要抓取的频道
        if channels_to_fetch and isinstance(channels_to_fetch, list):
            # 只抓取指定的频道
            channels = channels_to_fetch
            logger.info(f"正在抓取指定的 {len(channels)} 个频道的消息，时间范围: {start_time} 至今")
        else:
            # 抓取所有配置的频道
            if not CHANNELS:
                logger.warning("没有配置任何频道，无法抓取消息")
                return messages_by_channel
            channels = CHANNELS
            logger.info(f"正在抓取所有 {len(channels)} 个频道的消息，时间范围: {start_time} 至今")
        
        total_message_count = 0
        
        # 遍历所有要抓取的频道
        for channel in channels:
            channel_messages = []
            channel_message_count = 0
            skipped_report_count = 0
            logger.info(f"开始抓取频道: {channel}")
            
            # 获取当前频道要排除的报告消息ID列表
            exclude_ids = report_message_ids.get(channel, [])
            logger.info(f"频道 {channel} 要排除的报告消息ID列表: {exclude_ids}")
            
            try:
                async for message in client.iter_messages(channel, offset_date=start_time, reverse=True):
                    total_message_count += 1
                    channel_message_count += 1
                    
                    # 跳过报告消息
                    if message.id in exclude_ids:
                        skipped_report_count += 1
                        logger.debug(f"跳过报告消息，ID: {message.id}")
                        continue
                    
                    if message.text:
                        # 动态获取频道名用于生成链接
                        channel_part = channel.split('/')[-1]
                        msg_link = f"https://t.me/{channel_part}/{message.id}"
                        channel_messages.append(f"内容: {message.text[:500]}\n链接: {msg_link}")
                        
                        # 每抓取10条消息记录一次日志
                        if len(channel_messages) % 10 == 0:
                            logger.debug(f"频道 {channel} 已抓取 {len(channel_messages)} 条有效消息")
            except Exception as e:
                record_error(e, f"fetch_messages_channel_{channel}")
                logger.error(f"抓取频道 {channel} 消息时出错: {e}")
                # 继续处理其他频道
                continue
            
            # 将当前频道的消息添加到字典中
            messages_by_channel[channel] = channel_messages
            logger.info(f"频道 {channel} 抓取完成，共处理 {channel_message_count} 条消息，其中 {len(channel_messages)} 条包含文本内容，跳过了 {skipped_report_count} 条报告消息")
        
        logger.info(f"所有指定频道消息抓取完成，共处理 {total_message_count} 条消息")
        return messages_by_channel

async def send_long_message(client, chat_id, text, max_length=4000):
    """分段发送长消息"""
    logger.info(f"开始发送长消息，接收者: {chat_id}，消息总长度: {len(text)}字符，最大分段长度: {max_length}字符")
    
    if len(text) <= max_length:
        logger.info(f"消息长度未超过限制，直接发送")
        await client.send_message(chat_id, text, link_preview=False)
        return
    
    # 确定标题
    # 对于更新日志，使用固定标题
    channel_title = "更新日志"
    
    # 计算标题长度
    # 标题格式：📋 **{channel_title} ({i+1}/{len(parts)})**\n\n
    # 计算最大可能标题长度
    max_title_length = len(f"📋 **{channel_title} (99/99)**\n\n")
    
    # 实际可用于内容的最大长度
    content_max_length = max_length - max_title_length
    
    logger.info(f"消息需要分段发送，开始分段处理，标题长度: {max_title_length}字符，内容最大长度: {content_max_length}字符")
    
    # 简单直接的分段方法：按字符数分割
    parts = []
    text_length = len(text)
    
    for i in range(0, text_length, content_max_length):
        part = text[i:i+content_max_length]
        if part:
            parts.append(part)
    
    logger.info(f"消息分段完成，共分成 {len(parts)} 段")
    
    # 验证分段结果
    total_content_length = sum(len(part) for part in parts)
    logger.debug(f"分段后总内容长度: {total_content_length}字符，原始长度: {text_length}字符")
    
    # 发送所有部分
    for i, part in enumerate(parts):
        # 构建完整消息，包含标题
        full_message = f"📋 **{channel_title} ({i+1}/{len(parts)})**\n\n{part}"
        full_message_length = len(full_message)
        logger.info(f"正在发送第 {i+1}/{len(parts)} 段，长度: {full_message_length}字符")
        
        # 验证消息长度不超过限制
        if full_message_length > max_length:
            logger.error(f"第 {i+1} 段消息长度 {full_message_length} 超过限制 {max_length}，将进行紧急分割")
            # 紧急分割：直接按字符分割
            for j in range(0, full_message_length, max_length):
                emergency_part = full_message[j:j+max_length]
                await client.send_message(chat_id, emergency_part, link_preview=False)
                logger.warning(f"发送紧急分割段 {j//max_length + 1}")
        else:
            await client.send_message(chat_id, full_message, link_preview=False)
            logger.debug(f"成功发送第 {i+1}/{len(parts)} 段")

async def send_report(summary_text, source_channel=None, client=None, skip_admins=False):
    """发送报告
    
    Args:
        summary_text: 报告内容
        source_channel: 源频道，可选。如果提供，将向该频道发送报告
        client: 可选。已存在的Telegram客户端实例，如果不提供，将尝试使用活动的客户端实例或创建新实例
        skip_admins: 是否跳过向管理员发送报告，默认为False
    
    Returns:
        list: 发送到源频道的消息ID列表
    """
    logger.info("开始发送报告")
    logger.debug(f"报告长度: {len(summary_text)}字符")
    
    # 存储发送到源频道的消息ID
    report_message_ids = []
    
    try:
        # 确定使用哪个客户端实例
        # 1. 如果提供了客户端实例，直接使用它
        # 2. 否则，尝试使用活动的客户端实例
        # 3. 否则，创建新实例
        if client:
            logger.info("使用提供的客户端实例发送报告")
            use_client = client
            # 如果提供了客户端实例，我们假设它已经启动并连接
            use_existing_client = True
        else:
            # 尝试获取活动的客户端实例
            active_client = get_active_client()
            if active_client:
                logger.info("使用活动的客户端实例发送报告")
                use_client = active_client
                use_existing_client = True
            else:
                logger.info("没有活动的客户端实例，创建新客户端实例发送报告")
                use_client = TelegramClient('bot_session', int(API_ID), API_HASH)
                use_existing_client = False
        
        if use_existing_client:
            # 使用现有的客户端实例（已经启动并连接）
            # 向所有管理员发送消息（除非跳过）
            if not skip_admins:
                for admin_id in ADMIN_LIST:
                    try:
                        logger.info(f"正在向管理员 {admin_id} 发送报告")
                        await send_long_message(use_client, admin_id, summary_text)
                        logger.info(f"成功向管理员 {admin_id} 发送报告")
                    except Exception as e:
                        logger.error(f"向管理员 {admin_id} 发送报告失败: {type(e).__name__}: {e}", exc_info=True)
            else:
                logger.info("跳过向管理员发送报告")
            
            # 如果提供了源频道且配置允许，向源频道发送报告
            if source_channel and SEND_REPORT_TO_SOURCE:
                try:
                    logger.info(f"正在向源频道 {source_channel} 发送报告")
                    # 直接调用use_client.send_message并收集消息ID
                    if len(summary_text) <= 4000:
                        # 短消息直接发送
                        msg = await use_client.send_message(source_channel, summary_text, link_preview=False)
                        report_message_ids.append(msg.id)
                    else:
                        # 长消息分段发送，收集每个分段的消息ID
                        # 提取频道名称用于分段消息标题
                        channel_title = "频道周报汇总"
                        if "**" in summary_text and "** " in summary_text:
                            start_idx = summary_text.index("**") + 2
                            end_idx = summary_text.index("** ", start_idx)
                            channel_title = summary_text[start_idx:end_idx]
                        
                        # 分段发送
                        parts = []
                        current_part = ""
                        
                        for line in summary_text.split('\n'):
                            if len(current_part) + len(line) + 1 <= 4000:
                                current_part += line + '\n'
                            else:
                                if current_part:
                                    parts.append(current_part.strip())
                                if len(line) > 4000:
                                    for i in range(0, len(line), 4000):
                                        parts.append(line[i:i+4000])
                                else:
                                    current_part = line + '\n'
                        
                        if current_part:
                            parts.append(current_part.strip())
                        
                        # 发送所有部分并收集消息ID
                        for i, part in enumerate(parts):
                            part_text = f"📋 **{channel_title} ({i+1}/{len(parts)})**\n\n{part}"
                            msg = await use_client.send_message(source_channel, part_text, link_preview=False)
                            report_message_ids.append(msg.id)
                    
                    logger.info(f"成功向源频道 {source_channel} 发送报告，消息ID: {report_message_ids}")
                except Exception as e:
                    logger.error(f"向源频道 {source_channel} 发送报告失败: {type(e).__name__}: {e}", exc_info=True)
        else:
            # 创建新的客户端实例
            async with use_client:
                await use_client.start(bot_token=BOT_TOKEN)
                logger.info("Telegram机器人客户端已启动")
                
                # 向所有管理员发送消息（除非跳过）
                if not skip_admins:
                    for admin_id in ADMIN_LIST:
                        try:
                            logger.info(f"正在向管理员 {admin_id} 发送报告")
                            await send_long_message(use_client, admin_id, summary_text)
                            logger.info(f"成功向管理员 {admin_id} 发送报告")
                        except Exception as e:
                            logger.error(f"向管理员 {admin_id} 发送报告失败: {type(e).__name__}: {e}", exc_info=True)
                else:
                    logger.info("跳过向管理员发送报告")
                
                # 如果提供了源频道且配置允许，向源频道发送报告
                if source_channel and SEND_REPORT_TO_SOURCE:
                    try:
                        logger.info(f"正在向源频道 {source_channel} 发送报告")
                        # 直接调用use_client.send_message并收集消息ID
                        if len(summary_text) <= 4000:
                            # 短消息直接发送
                            msg = await use_client.send_message(source_channel, summary_text, link_preview=False)
                            report_message_ids.append(msg.id)
                        else:
                            # 长消息分段发送，收集每个分段的消息ID
                            # 提取频道名称用于分段消息标题
                            channel_title = "频道周报汇总"
                            if "**" in summary_text and "** " in summary_text:
                                start_idx = summary_text.index("**") + 2
                                end_idx = summary_text.index("** ", start_idx)
                                channel_title = summary_text[start_idx:end_idx]
                            
                            # 分段发送
                            parts = []
                            current_part = ""
                            
                            for line in summary_text.split('\n'):
                                if len(current_part) + len(line) + 1 <= 4000:
                                    current_part += line + '\n'
                                else:
                                    if current_part:
                                        parts.append(current_part.strip())
                                    if len(line) > 4000:
                                        for i in range(0, len(line), 4000):
                                            parts.append(line[i:i+4000])
                                    else:
                                        current_part = line + '\n'
                            
                            if current_part:
                                parts.append(current_part.strip())
                            
                            # 发送所有部分并收集消息ID
                            for i, part in enumerate(parts):
                                part_text = f"📋 **{channel_title} ({i+1}/{len(parts)})**\n\n{part}"
                                msg = await use_client.send_message(source_channel, part_text, link_preview=False)
                                report_message_ids.append(msg.id)
                        
                        logger.info(f"成功向源频道 {source_channel} 发送报告，消息ID: {report_message_ids}")
                    except Exception as e:
                        logger.error(f"向源频道 {source_channel} 发送报告失败: {type(e).__name__}: {e}", exc_info=True)
        
        return report_message_ids
        
    except Exception as e:
        logger.error(f"发送报告时发生严重错误: {type(e).__name__}: {e}", exc_info=True)
        # 返回空列表，而不是让程序崩溃
        return []
