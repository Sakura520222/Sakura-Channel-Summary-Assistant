# -*- coding: utf-8 -*-
# Copyright 2026 Sakura-频道总结助手
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可，
# 并附加非商业使用限制条款。
#
# - 署名：必须提供本项目的原始来源链接
# - 非商业：禁止任何商业用途和分发
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Channel-Summary-Assistant
# 许可证全文：参见 LICENSE 文件

"""
国际化（I18n）模块

提供多语言支持，允许用户切换界面语言。
当前支持：zh-CN（简体中文）、en-US（英语）
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


# ==================== 翻译文本字典 ====================

# 中文翻译（简体中文）
MESSAGE_ZH_CN = {
    # ========== 语言设置 ==========
    'language.current': '当前语言：{language}',
    'language.changed': '语言已更改为：{language}',
    'language.invalid': '无效的语言代码：{language}\n\n支持的语言：\n• zh-CN - 简体中文\n• en-US - 英语',
    'language.usage': '使用格式：/language <语言代码>\n\n示例：\n/language zh-CN\n/language en-US',
    'language.supported': '支持的语言：\n• zh-CN - 简体中文\n• en-US - 英语',

    # ========== 欢迎消息 ==========
    'welcome.title': '🌸 **欢迎使用 Sakura-频道总结助手**',
    'welcome.description': '🤖 我是Telegram智能频道管理助手，专门帮助频道主自动化管理 Telegram 频道内容。',
    'welcome.features_title': '✨ **主要功能**',
    'welcome.feature_summary': '• 📊 AI智能总结频道消息',
    'welcome.feature_schedule': '• ⏰ 支持每天/每周自动总结',
    'welcome.feature_custom': '• 🎯 自定义总结风格和频率',
    'welcome.feature_poll': '• 📝 自动生成投票互动',
    'welcome.feature_multi': '• 👥 多频道同时管理',
    'welcome.feature_history': '• 📜 历史总结记录与查询',
    'welcome.commands_title': '📚 **常用命令**',
    'welcome.command_basic': '**基础命令**\n/start - 查看此欢迎消息\n/summary - 立即生成本周汇总',
    'welcome.command_config': '**配置命令**\n/showchannels - 查看频道列表\n/addchannel - 添加监控频道\n/setchannelschedule - 设置自动总结时间',
    'welcome.command_history': '**历史记录**\n/history - 查看历史总结\n/export - 导出历史记录\n/stats - 查看统计数据',
    'welcome.command_admin': '**管理命令**\n/pause - 暂停定时任务\n/resume - 恢复定时任务\n/changelog - 查看更新日志',
    'welcome.tip': '💡 **提示**\n• 发送 /help 查看完整命令列表\n• 更多信息请访问项目[开源仓库](https://github.com/Sakura520222/Sakura-Channel-Summary-Assistant)',

    # ========== 帮助消息 ==========
    'help.title': '📚 **Sakura-频道总结助手 - 完整命令列表**',
    'help.section_basic': '**🤖 基础命令**',
    'help.section_prompt': '**⚙️ 提示词管理**',
    'help.section_ai': '**🤖 AI 配置**',
    'help.section_log': '**📊 日志管理**',
    'help.section_control': '**🔄 机器人控制**',
    'help.section_channel': '**📺 频道管理**',
    'help.section_schedule': '**⏰ 时间配置**',
    'help.section_data': '**🗑️ 数据管理**',
    'help.section_report': '**📤 报告设置**',
    'help.section_poll': '**🗳️ 投票配置**',
    'help.section_cache': '**💾 缓存管理**',
    'help.section_history': '**📜 历史记录**',
    'help.new_feature': ' (新功能)',
    'help.tip': '---\n💡 **提示**\n• 大多数命令支持中英文别名\n• 配置类命令需要管理员权限\n• 使用 /start 查看快速入门指南',

    # ========== 命令描述 ==========
    'cmd.start': '/start - 查看欢迎消息和基本介绍',
    'cmd.help': '/help - 查看此完整命令列表',
    'cmd.summary': '/summary - 立即生成本周频道消息汇总',
    'cmd.changelog': '/changelog - 查看项目更新日志',
    'cmd.showprompt': '/showprompt - 查看当前使用的提示词',
    'cmd.setprompt': '/setprompt - 设置自定义提示词',
    'cmd.showpollprompt': '/showpollprompt - 查看当前投票提示词',
    'cmd.setpollprompt': '/setpollprompt - 设置自定义投票提示词',
    'cmd.showaicfg': '/showaicfg - 查看当前 AI 配置信息',
    'cmd.setaicfg': '/setaicfg - 设置自定义 AI 配置（API Key、Base URL、Model）',
    'cmd.showloglevel': '/showloglevel - 查看当前日志级别',
    'cmd.setloglevel': '/setloglevel - 设置日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）',
    'cmd.restart': '/restart - 重启机器人',
    'cmd.shutdown': '/shutdown - 彻底停止机器人',
    'cmd.pause': '/pause - 暂停所有定时任务',
    'cmd.resume': '/resume - 恢复所有定时任务',
    'cmd.showchannels': '/showchannels - 查看当前监控的频道列表',
    'cmd.addchannel': '/addchannel - 添加新频道到监控列表\n• 示例：/addchannel https://t.me/examplechannel',
    'cmd.deletechannel': '/deletechannel - 从监控列表中删除频道\n• 示例：/deletechannel https://t.me/examplechannel',
    'cmd.showchannelschedule': '/showchannelschedule - 查看频道自动总结时间配置',
    'cmd.setchannelschedule': '/setchannelschedule - 设置频道自动总结时间\n• 每天：/setchannelschedule 频道 daily 小时 分钟\n• 每周：/setchannelschedule 频道 weekly 星期,星期 小时 分钟',
    'cmd.deletechannelschedule': '/deletechannelschedule - 删除频道自动总结时间配置',
    'cmd.clearsummarytime': '/clearsummarytime - 清除上次总结时间记录',
    'cmd.setsendtosource': '/setsendtosource - 设置是否将报告发送回源频道',
    'cmd.channelpoll': '/channelpoll - 查看频道投票配置',
    'cmd.setchannelpoll': '/setchannelpoll - 设置频道投票配置\n• 格式：/setchannelpoll 频道 true/false channel/discussion',
    'cmd.deletechannelpoll': '/deletechannelpoll - 删除频道投票配置',
    'cmd.clearcache': '/clearcache - 清除讨论组ID缓存\n• /clearcache - 清除所有缓存\n• /clearcache 频道URL - 清除指定频道缓存',
    'cmd.history': '/history - 查看历史总结\n• /history - 查看所有频道最近10条\n• /history channel1 - 查看指定频道\n• /history channel1 30 - 查看最近30天',
    'cmd.export': '/export - 导出历史记录\n• /export - 导出所有记录为JSON\n• /export channel1 csv - 导出为CSV\n• /export channel1 md - 导出为md',
    'cmd.stats': '/stats - 查看统计数据\n• /stats - 查看所有频道统计\n• /stats channel1 - 查看指定频道统计',
    'cmd.language': '/language - 切换界面语言\n• /language - 查看当前语言\n• /language zh-CN - 切换为中文\n• /language en-US - 切换为英文',

    # ========== 通用消息 ==========
    'error.permission_denied': '您没有权限执行此命令',
    'error.invalid_command': '无效的命令格式',
    'success': '操作成功',
    'failed': '操作失败',
    'error.unknown': '发生未知错误',
}

# 英文翻译
MESSAGE_EN_US = {
    # ========== Language Settings ==========
    'language.current': 'Current language: {language}',
    'language.changed': 'Language changed to: {language}',
    'language.invalid': 'Invalid language code: {language}\n\nSupported languages:\n• zh-CN - Simplified Chinese\n• en-US - English',
    'language.usage': 'Usage: /language <language_code>\n\nExamples:\n/language zh-CN\n/language en-US',
    'language.supported': 'Supported languages:\n• zh-CN - Simplified Chinese\n• en-US - English',

    # ========== Welcome Message ==========
    'welcome.title': '🌸 **Welcome to Sakura-Channel Summary Assistant**',
    'welcome.description': '🤖 I am an intelligent Telegram channel management assistant, specializing in helping channel owners automate Telegram channel content management.',
    'welcome.features_title': '✨ **Main Features**',
    'welcome.feature_summary': '• 📊 AI-powered channel message summarization',
    'welcome.feature_schedule': '• ⏰ Support for daily/weekly automatic summaries',
    'welcome.feature_custom': '• 🎯 Customizable summary styles and frequency',
    'welcome.feature_poll': '• 📝 Automatic poll generation',
    'welcome.feature_multi': '• 👥 Multi-channel management',
    'welcome.feature_history': '• 📜 Summary history records and queries',
    'welcome.commands_title': '📚 **Common Commands**',
    'welcome.command_basic': '**Basic Commands**\n/start - View this welcome message\n/summary - Generate weekly summary immediately',
    'welcome.command_config': '**Configuration Commands**\n/showchannels - View channel list\n/addchannel - Add monitoring channel\n/setchannelschedule - Set automatic summary time',
    'welcome.command_history': '**History**\n/history - View summary history\n/export - Export history records\n/stats - View statistics',
    'welcome.command_admin': '**Management Commands**\n/pause - Pause scheduled tasks\n/resume - Resume scheduled tasks\n/changelog - View changelog',
    'welcome.tip': '💡 **Tips**\n• Send /help to view complete command list\n• Visit [GitHub repository](https://github.com/Sakura520222/Sakura-Channel-Summary-Assistant) for more information',

    # ========== Help Message ==========
    'help.title': '📚 **Sakura-Channel Summary Assistant - Complete Command List**',
    'help.section_basic': '**🤖 Basic Commands**',
    'help.section_prompt': '**⚙️ Prompt Management**',
    'help.section_ai': '**🤖 AI Configuration**',
    'help.section_log': '**📊 Log Management**',
    'help.section_control': '**🔄 Bot Control**',
    'help.section_channel': '**📺 Channel Management**',
    'help.section_schedule': '**⏰ Schedule Configuration**',
    'help.section_data': '**🗑️ Data Management**',
    'help.section_report': '**📤 Report Settings**',
    'help.section_poll': '**🗳️ Poll Configuration**',
    'help.section_cache': '**💾 Cache Management**',
    'help.section_history': '**📜 History**',
    'help.new_feature': ' (New Feature)',
    'help.tip': '---\n💡 **Tips**\n• Most commands support Chinese/English aliases\n• Configuration commands require admin permissions\n• Use /start for quick start guide',

    # ========== Command Descriptions ==========
    'cmd.start': '/start - View welcome message and basic introduction',
    'cmd.help': '/help - View this complete command list',
    'cmd.summary': '/summary - Generate weekly channel message summary immediately',
    'cmd.changelog': '/changelog - View project changelog',
    'cmd.showprompt': '/showprompt - View current prompt',
    'cmd.setprompt': '/setprompt - Set custom prompt',
    'cmd.showpollprompt': '/showpollprompt - View current poll prompt',
    'cmd.setpollprompt': '/setpollprompt - Set custom poll prompt',
    'cmd.showaicfg': '/showaicfg - View current AI configuration',
    'cmd.setaicfg': '/setaicfg - Set custom AI configuration (API Key, Base URL, Model)',
    'cmd.showloglevel': '/showloglevel - View current log level',
    'cmd.setloglevel': '/setloglevel - Set log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)',
    'cmd.restart': '/restart - Restart bot',
    'cmd.shutdown': '/shutdown - Shutdown bot completely',
    'cmd.pause': '/pause - Pause all scheduled tasks',
    'cmd.resume': '/resume - Resume all scheduled tasks',
    'cmd.showchannels': '/showchannels - View currently monitored channel list',
    'cmd.addchannel': '/addchannel - Add new channel to monitoring list\n• Example: /addchannel https://t.me/examplechannel',
    'cmd.deletechannel': '/deletechannel - Remove channel from monitoring list\n• Example: /deletechannel https://t.me/examplechannel',
    'cmd.showchannelschedule': '/showchannelschedule - View channel auto-summary schedule',
    'cmd.setchannelschedule': '/setchannelschedule - Set channel auto-summary schedule\n• Daily: /setchannelschedule channel daily hour minute\n• Weekly: /setchannelschedule channel weekly day,day hour minute',
    'cmd.deletechannelschedule': '/deletechannelschedule - Delete channel auto-summary schedule',
    'cmd.clearsummarytime': '/clearsummarytime - Clear last summary time record',
    'cmd.setsendtosource': '/setsendtosource - Set whether to send report back to source channel',
    'cmd.channelpoll': '/channelpoll - View channel poll configuration',
    'cmd.setchannelpoll': '/setchannelpoll - Set channel poll configuration\n• Format: /setchannelpoll channel true/false channel/discussion',
    'cmd.deletechannelpoll': '/deletechannelpoll - Delete channel poll configuration',
    'cmd.clearcache': '/clearcache - Clear discussion group ID cache\n• /clearcache - Clear all cache\n• /clearcache channel_url - Clear specific channel cache',
    'cmd.history': '/history - View summary history\n• /history - View 10 most recent from all channels\n• /history channel1 - View specific channel\n• /history channel1 30 - View last 30 days',
    'cmd.export': '/export - Export history records\n• /export - Export all as JSON\n• /export channel1 csv - Export as CSV\n• /export channel1 md - Export as Markdown',
    'cmd.stats': '/stats - View statistics\n• /stats - View all channel stats\n• /stats channel1 - View specific channel stats',
    'cmd.language': '/language - Switch interface language\n• /language - View current language\n• /language zh-CN - Switch to Chinese\n• /language en-US - Switch to English',

    # ========== Common Messages ==========
    'error.permission_denied': 'You do not have permission to execute this command',
    'error.invalid_command': 'Invalid command format',
    'success': 'Operation successful',
    'failed': 'Operation failed',
    'error.unknown': 'An unknown error occurred',
}


class I18nManager:
    """国际化管理器（单例模式）"""

    _instance: Optional['I18nManager'] = None

    def __new__(cls) -> 'I18nManager':
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化国际化管理器"""
        if self._initialized:
            return

        self._initialized = True
        self._current_language = 'zh-CN'  # 默认语言
        self._supported_languages = ['zh-CN', 'en-US']

        # 加载翻译文本
        self._messages: Dict[str, Dict[str, str]] = {
            'zh-CN': MESSAGE_ZH_CN,
            'en-US': MESSAGE_EN_US
        }

        logger.info(f"国际化管理器初始化完成，当前语言：{self._current_language}")

    def get_language(self) -> str:
        """获取当前语言

        Returns:
            str: 当前语言代码（如 'zh-CN'）
        """
        return self._current_language

    def set_language(self, language: str) -> bool:
        """设置当前语言

        Args:
            language: 语言代码（如 'zh-CN' 或 'en-US'）

        Returns:
            bool: 是否成功设置语言
        """
        if language not in self._supported_languages:
            logger.warning(f"不支持的语言：{language}，支持的语言：{self._supported_languages}")
            return False

        old_language = self._current_language
        self._current_language = language
        logger.info(f"语言已从 {old_language} 更改为 {language}")
        return True

    def get_supported_languages(self) -> list:
        """获取支持的语言列表

        Returns:
            list: 支持的语言代码列表
        """
        return self._supported_languages.copy()

    def get_text(self, key: str, **kwargs) -> str:
        """获取指定 key 的翻译文本

        支持变量插值和回退机制：
        1. 首先尝试从当前语言获取
        2. 如果当前语言不存在该 key，回退到 zh-CN
        3. 如果回退后仍不存在，返回 key 本身

        Args:
            key: 翻译文本的 key
            **kwargs: 用于文本插值的变量

        Returns:
            str: 翻译后的文本
        """
        # 获取当前语言的翻译
        message = self._messages.get(self._current_language, {}).get(key)

        # 如果当前语言没有该 key，回退到中文
        if message is None:
            logger.debug(f"key '{key}' 在语言 '{self._current_language}' 中不存在，回退到 zh-CN")
            message = self._messages.get('zh-CN', {}).get(key)

        # 如果回退后仍不存在，返回 key 本身
        if message is None:
            logger.warning(f"key '{key}' 在所有语言中都不存在，返回 key 本身")
            return key

        # 支持变量插值
        try:
            if kwargs:
                return message.format(**kwargs)
            return message
        except (KeyError, ValueError) as e:
            logger.error(f"文本插值失败 (key={key}, kwargs={kwargs}): {e}")
            return message


# 全局单例实例
_i18n_manager = I18nManager()


def get_language() -> str:
    """获取当前语言（快捷函数）"""
    return _i18n_manager.get_language()


def set_language(language: str) -> bool:
    """设置当前语言（快捷函数）

    Args:
        language: 语言代码

    Returns:
        bool: 是否成功设置
    """
    return _i18n_manager.set_language(language)


def get_supported_languages() -> list:
    """获取支持的语言列表（快捷函数）"""
    return _i18n_manager.get_supported_languages()


def get_text(key: str, **kwargs) -> str:
    """获取翻译文本（快捷函数）

    Args:
        key: 翻译文本的 key
        **kwargs: 用于文本插值的变量

    Returns:
        str: 翻译后的文本
    """
    return _i18n_manager.get_text(key, **kwargs)


def t(key: str, **kwargs) -> str:
    """获取翻译文本的简写别名

    Args:
        key: 翻译文本的 key
        **kwargs: 用于文本插值的变量

    Returns:
        str: 翻译后的文本
    """
    return get_text(key, **kwargs)
