"""
Tests for the queue service.
"""

import pytest
from backend.services.queue_service import QueueService, InMemoryQueue


@pytest.mark.unit
class TestQueueService:
    """
    Unit tests for QueueService.
    """

    def test_enqueue(self, queue_service):
        """
        Test enqueueing a job.
        """
        job_id = "job-123"
        queue_service.enqueue(job_id)
        assert queue_service.size() == 1

    def test_dequeue(self, queue_service):
        """
        Test dequeueing a job.
        """
        job_id = "job-123"
        queue_service.enqueue(job_id)

        dequeued = queue_service.dequeue(timeout=0.1)
        assert dequeued == job_id
        assert queue_service.size() == 0

    def test_dequeue_empty(self, queue_service):
        """
        Test dequeueing from an empty queue.
        """
        result = queue_service.dequeue(timeout=0.1)
        assert result is None

    def test_size(self, queue_service):
        """
        Test getting queue size.
        """
        assert queue_service.size() == 0

        queue_service.enqueue("job-1")
        queue_service.enqueue("job-2")
        queue_service.enqueue("job-3")

        assert queue_service.size() == 3

    def test_clear(self, queue_service):
        """
        Test clearing the queue.
        """
        queue_service.enqueue("job-1")
        queue_service.enqueue("job-2")
        assert queue_service.size() == 2

        queue_service.clear()
        assert queue_service.size() == 0

    def test_fifo_order(self, queue_service):
        """
        Test that queue operates in FIFO order.
        """
        queue_service.enqueue("job-1")
        queue_service.enqueue("job-2")
        queue_service.enqueue("job-3")

        assert queue_service.dequeue(timeout=0.1) == "job-1"
        assert queue_service.dequeue(timeout=0.1) == "job-2"
        assert queue_service.dequeue(timeout=0.1) == "job-3"
