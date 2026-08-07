"""
core/scheduler.py — DOT Assistant Scheduler

Background scheduler for one-shot and recurring tasks.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from core.logger import get_logger

log = get_logger("scheduler")


@dataclass
class ScheduledTask:
    task_id: str
    fn: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    timer: Optional[threading.Timer] = field(default=None, repr=False)
    recurring: bool = False
    interval: float = 0.0


class Scheduler:
    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._lock = threading.Lock()
        self._counter = 0

    def _next_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"task_{self._counter}"

    def schedule_once(
        self,
        delay_seconds: float,
        fn: Callable,
        *args: Any,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        tid = task_id or self._next_id()

        def _run() -> None:
            try:
                fn(*args, **kwargs)
            except Exception:
                log.exception("Scheduled task %s raised an exception", tid)
            finally:
                with self._lock:
                    self._tasks.pop(tid, None)

        timer = threading.Timer(delay_seconds, _run)
        timer.daemon = True
        task = ScheduledTask(task_id=tid, fn=fn, args=args, kwargs=kwargs, timer=timer)
        with self._lock:
            self._tasks[tid] = task
        timer.start()
        log.info("Scheduled once: %s in %.1fs", tid, delay_seconds)
        return tid

    def schedule_recurring(
        self,
        interval_seconds: float,
        fn: Callable,
        *args: Any,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        tid = task_id or self._next_id()

        def _run() -> None:
            try:
                fn(*args, **kwargs)
            except Exception:
                log.exception("Recurring task %s raised an exception", tid)
            finally:
                with self._lock:
                    if tid in self._tasks:
                        timer = threading.Timer(interval_seconds, _run)
                        timer.daemon = True
                        self._tasks[tid].timer = timer
                        timer.start()

        timer = threading.Timer(interval_seconds, _run)
        timer.daemon = True
        task = ScheduledTask(
            task_id=tid, fn=fn, args=args, kwargs=kwargs,
            timer=timer, recurring=True, interval=interval_seconds,
        )
        with self._lock:
            self._tasks[tid] = task
        timer.start()
        log.info("Scheduled recurring: %s every %.1fs", tid, interval_seconds)
        return tid

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.pop(task_id, None)
        if task and task.timer:
            task.timer.cancel()
            log.info("Cancelled task: %s", task_id)
            return True
        return False

    def cancel_all(self) -> None:
        with self._lock:
            tasks = list(self._tasks.values())
            self._tasks.clear()
        for t in tasks:
            if t.timer:
                t.timer.cancel()

    def list_tasks(self) -> list[str]:
        with self._lock:
            return list(self._tasks.keys())
