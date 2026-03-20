# core/config/event_bus.py
import asyncio
import logging
import weakref
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class AsyncIOEventBus:
    """支持优先级和超时保护的异步事件总线"""

    # 优先级常量
    PRIORITY_CRITICAL = 0
    PRIORITY_HIGH = 10
    PRIORITY_NORMAL = 50
    PRIORITY_LOW = 100

    # 默认超时设置（秒）
    DEFAULT_TIMEOUT = 30.0
    CRITICAL_TIMEOUT = 60.0

    def __init__(self, sequential_mode: bool = True):
        """
        Args:
            sequential_mode: 是否按优先级顺序执行（默认True）
        """
        self._subscribers: dict[type, list[tuple[int, Callable, float]]] = {}
        self._lock = asyncio.Lock()
        self._sequential_mode = sequential_mode
        self._weak_refs: dict[Callable, weakref.ref] = {}  # 存储弱引用，避免循环引用

    def _make_weak_callback(self, callback: Callable) -> Callable:
        """为回调函数创建弱引用，避免循环引用导致的内存泄漏"""
        if callback in self._weak_refs:
            ref = self._weak_refs[callback]
            if ref() is not None:
                return ref()

        def weak_callback(*args, **kwargs):
            cb = self._weak_refs.get(callback)
            if cb is None:
                return None
            actual_cb = cb()
            if actual_cb is None:
                # 回调已被回收，清理弱引用
                self._weak_refs.pop(callback, None)
                return None
            return actual_cb(*args, **kwargs)

        self._weak_refs[callback] = weakref.ref(
            callback, lambda _: self._weak_refs.pop(callback, None)
        )
        return callback

    async def subscribe(
        self,
        event_type: type,
        callback: Callable,
        priority: int = PRIORITY_NORMAL,
        timeout: float | None = None,
    ) -> None:
        """
        订阅事件（带优先级和超时保护）

        Args:
            event_type: 事件类型
            callback: 回调函数
            priority: 优先级（越小越优先）
            timeout: 超时时间（秒），None使用默认值
        """
        # 根据优先级设置默认超时
        if timeout is None:
            timeout = (
                self.CRITICAL_TIMEOUT if priority <= self.PRIORITY_HIGH else self.DEFAULT_TIMEOUT
            )

        async with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []

            self._subscribers[event_type].append((priority, callback, timeout))
            self._subscribers[event_type].sort(key=lambda x: x[0])

            logger.debug(
                f"订阅事件: {event_type.__name__} -> {callback.__name__} "
                f"(优先级: {priority}, 超时: {timeout}s)"
            )

    async def unsubscribe(
        self,
        event_type: type,
        callback: Callable,
    ) -> bool:
        """
        取消订阅事件

        Args:
            event_type: 事件类型
            callback: 要移除的回调函数

        Returns:
            是否成功移除（False表示未找到该订阅）
        """
        async with self._lock:
            if event_type not in self._subscribers:
                return False

            original_length = len(self._subscribers[event_type])
            self._subscribers[event_type] = [
                (priority, cb, timeout)
                for priority, cb, timeout in self._subscribers[event_type]
                if cb != callback
            ]

            removed = len(self._subscribers[event_type]) < original_length

            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

            if removed:
                logger.debug(f"取消订阅事件: {event_type.__name__} -> {callback.__name__}")

            return removed

    async def publish(self, event: Any):
        """发布事件（带超时保护）"""
        event_type = type(event)

        async with self._lock:
            subscribers = self._subscribers.get(event_type, []).copy()

        if not subscribers:
            logger.debug(f"没有订阅者监听事件: {event_type.__name__}")
            return

        logger.info(
            f"发布事件: {event_type.__name__} -> {len(subscribers)} 个订阅者 "
            f"(模式: {'顺序' if self._sequential_mode else '并发'})"
        )

        if self._sequential_mode:
            # 顺序执行：每个订阅者都有超时保护
            for priority, callback, timeout in subscribers:
                await self._safe_notify_with_timeout(callback, event, priority, timeout)
        else:
            # 并发执行：每个订阅者独立超时
            tasks = [
                asyncio.create_task(
                    self._safe_notify_with_timeout(callback, event, priority, timeout)
                )
                for priority, callback, timeout in subscribers
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_notify_with_timeout(
        self, callback: Callable, event: Any, priority: int, timeout: float
    ):
        """带超时保护的安全通知"""
        try:
            # 使用 asyncio.wait_for 添加超时保护
            if asyncio.iscoroutinefunction(callback):
                await asyncio.wait_for(callback(event), timeout=timeout)
            else:
                # 同步函数也需要超时保护
                await asyncio.wait_for(asyncio.to_thread(callback, event), timeout=timeout)

            logger.debug(f"✓ {callback.__name__} 执行成功 (优先级: {priority})")

        except TimeoutError:
            logger.error(
                f"✗ {callback.__name__} 执行超时 (>{timeout}s, 优先级: {priority})，"
                f"跳过此订阅者继续执行"
            )
        except Exception as e:
            logger.error(
                f"✗ {callback.__name__} 执行失败 (优先级: {priority}) - {e}", exc_info=True
            )

    async def shutdown(self):
        """关闭事件总线"""
        # 清理所有订阅
        await self.unsubscribe_all()

        # 清理弱引用
        self._weak_refs.clear()

        logger.info("事件总线已关闭")

    async def unsubscribe_all(self, event_type: type | None = None) -> int:
        """取消所有订阅，释放资源

        Args:
            event_type: 可选，指定要取消订阅的事件类型。如果为 None 则取消所有订阅

        Returns:
            取消的订阅数量
        """
        async with self._lock:
            if event_type is None:
                # 取消所有订阅
                count = sum(len(subs) for subs in self._subscribers.values())
                self._subscribers.clear()
                logger.debug(f"已取消所有事件订阅: {count} 个")
                return count
            else:
                # 取消特定事件的订阅
                if event_type in self._subscribers:
                    count = len(self._subscribers[event_type])
                    del self._subscribers[event_type]
                    logger.debug(f"已取消 {event_type.__name__} 事件的所有订阅: {count} 个")
                    return count
                return 0
