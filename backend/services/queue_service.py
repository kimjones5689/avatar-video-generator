"""
Talking Photo AI
Queue Service

Thread-safe job queue abstraction.

This implementation uses Python's standard Queue for
development and small deployments. The interface is
designed so it can later be backed by Redis, RabbitMQ,
Amazon SQS, or another queue implementation.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from queue import Empty, Queue
from threading import Lock
from typing import Optional


class BaseQueue(ABC):
    """Abstract queue interface."""

    @abstractmethod
    def enqueue(self, job_id: str) -> None:
        ...

    @abstractmethod
    def dequeue(self, timeout: float = 1.0) -> Optional[str]:
        ...

    @abstractmethod
    def size(self) -> int:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...


class InMemoryQueue(BaseQueue):
    """
    Thread-safe queue implementation using queue.Queue.
    """

    def __init__(self):
        self._queue: Queue[str] = Queue()
        self._lock = Lock()

    def enqueue(self, job_id: str) -> None:
        self._queue.put(job_id)

    def dequeue(
        self,
        timeout: float = 1.0,
    ) -> Optional[str]:
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            return None

    def task_done(self):
        self._queue.task_done()

    def join(self):
        self._queue.join()

    def size(self) -> int:
        return self._queue.qsize()

    def clear(self):
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    self._queue.task_done()
                except Empty:
                    break


class QueueService:
    """
    High-level queue wrapper.

    The rest of the application depends on this class
    instead of a specific queue implementation.
    """

    def __init__(
        self,
        backend: Optional[BaseQueue] = None,
    ):
        self.backend = backend or InMemoryQueue()

    def enqueue(self, job_id: str):
        self.backend.enqueue(job_id)

    def dequeue(self):
        return self.backend.dequeue()

    def size(self):
        return self.backend.size()

    def clear(self):
        self.backend.clear()
