"""Python Heap Examples

Source code for docs/notes/basic/python-heap.rst
"""

import heapq

import pytest


# 基本堆操作
def heapify_list(items: list) -> list:
    """Convert list to heap in-place."""
    h = items.copy()
    heapq.heapify(h)
    return h


def heap_push(h: list, item) -> list:
    """Push item onto heap."""
    heapq.heappush(h, item)
    return h


def heap_pop(h: list):
    """Pop smallest item from heap."""
    return heapq.heappop(h)


def heap_pushpop(h: list, item):
    """Push item then pop smallest."""
    return heapq.heappushpop(h, item)


def heap_replace(h: list, item):
    """Pop smallest then push item."""
    return heapq.heapreplace(h, item)


# 堆排序
def heap_sort(items: list) -> list:
    """Sort using heap."""
    h = items.copy()
    heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]


# 最大堆
def max_heap_sort(items: list) -> list:
    """Sort descending using negated values."""
    h = [-x for x in items]
    heapq.heapify(h)
    return [-heapq.heappop(h) for _ in range(len(h))]


class MaxHeapItem:
    """Wrapper for max heap behavior."""

    def __init__(self, val):
        self.val = val

    def __lt__(self, other):
        return self.val > other.val


# 优先级 Queue
def priority_queue_example():
    """Priority queue using tuples."""
    pq = []
    heapq.heappush(pq, (2, "medium"))
    heapq.heappush(pq, (1, "high"))
    heapq.heappush(pq, (3, "low"))
    return [heapq.heappop(pq) for _ in range(len(pq))]


# 定制Objects
class Task:
    """Task with priority for heap."""

    def __init__(self, priority: int, name: str):
        self.priority = priority
        self.name = name

    def __lt__(self, other):
        return self.priority < other.priority

    def __repr__(self):
        return f"Task({self.priority}, {self.name!r})"


def task_queue():
    """Process tasks by priority."""
    h = []
    heapq.heappush(h, Task(3, "low"))
    heapq.heappush(h, Task(1, "high"))
    heapq.heappush(h, Task(2, "medium"))
    return [heapq.heappop(h) for _ in range(len(h))]


# K 最小/最大
def k_smallest(items: list, k: int) -> list:
    """Find k smallest elements."""
    return heapq.nsmallest(k, items)


def k_largest(items: list, k: int) -> list:
    """Find k largest elements."""
    return heapq.nlargest(k, items)


def k_largest_by_key(items: list, k: int, key) -> list:
    """Find k largest by key function."""
    return heapq.nlargest(k, items, key=key)


# 合并排序
def merge_sorted(*iterables) -> list:
    """Merge sorted iterables."""
    return list(heapq.merge(*iterables))


def merge_sorted_reverse(*iterables) -> list:
    """Merge sorted iterables in reverse."""
    return list(heapq.merge(*iterables, reverse=True))


# 固定大小的堆
def top_k(items: list, k: int) -> list:
    """Keep track of k largest elements."""
    h = []
    for x in items:
        if len(h) < k:
            heapq.heappush(h, x)
        elif x > h[0]:
            heapq.heapreplace(h, x)
    return sorted(h, reverse=True)


# 索引堆
class IndexedHeap:
    """Heap with priority updates."""

    REMOVED = "<removed>"

    def __init__(self):
        self.heap = []
        self.entry_finder = {}

    def push(self, item, priority):
        if item in self.entry_finder:
            self.remove(item)
        entry = [priority, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.heap, entry)

    def remove(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = self.REMOVED

    def pop(self):
        while self.heap:
            priority, item = heapq.heappop(self.heap)
            if item is not self.REMOVED:
                del self.entry_finder[item]
                return item
        raise KeyError("pop from empty heap")


# 测试
class TestBasicHeap:
    def test_heapify(self):
        h = heapify_list([5, 1, 3, 2, 6])
        assert h[0] == 1

    def test_push_pop(self):
        h = []
        heap_push(h, 3)
        heap_push(h, 1)
        heap_push(h, 2)
        assert heap_pop(h) == 1
        assert heap_pop(h) == 2

    def test_pushpop(self):
        h = [1, 3, 5]
        heapq.heapify(h)
        assert heap_pushpop(h, 2) == 1

    def test_replace(self):
        h = [1, 3, 5]
        heapq.heapify(h)
        assert heap_replace(h, 2) == 1
        assert h[0] == 2


class TestHeapSort:
    def test_sort(self):
        assert heap_sort([5, 1, 3, 2, 6]) == [1, 2, 3, 5, 6]

    def test_max_sort(self):
        assert max_heap_sort([5, 1, 3, 2, 6]) == [6, 5, 3, 2, 1]


class TestPriorityQueue:
    def test_priority_order(self):
        result = priority_queue_example()
        assert result[0] == (1, "high")
        assert result[1] == (2, "medium")
        assert result[2] == (3, "low")


class TestCustomObjects:
    def test_max_heap_item(self):
        h = []
        for x in [5, 1, 3]:
            heapq.heappush(h, MaxHeapItem(x))
        assert heapq.heappop(h).val == 5

    def test_task_queue(self):
        tasks = task_queue()
        assert tasks[0].name == "high"
        assert tasks[1].name == "medium"
        assert tasks[2].name == "low"


class TestKElements:
    def test_k_smallest(self):
        assert k_smallest([5, 1, 8, 3, 9], 3) == [1, 3, 5]

    def test_k_largest(self):
        assert k_largest([5, 1, 8, 3, 9], 3) == [9, 8, 5]

    def test_k_largest_by_key(self):
        data = [{"score": 85}, {"score": 92}, {"score": 78}]
        result = k_largest_by_key(data, 2, key=lambda x: x["score"])
        assert result[0]["score"] == 92
        assert result[1]["score"] == 85


class TestMerge:
    def test_merge_sorted(self):
        assert merge_sorted([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]

    def test_merge_three(self):
        assert merge_sorted([1, 3], [2, 4], [0, 5]) == [0, 1, 2, 3, 4, 5]

    def test_merge_reverse(self):
        assert merge_sorted_reverse([5, 3, 1], [6, 4, 2]) == [6, 5, 4, 3, 2, 1]


class TestTopK:
    def test_top_k(self):
        assert top_k([5, 1, 8, 3, 9, 2, 7, 4, 6], 3) == [9, 8, 7]


class TestIndexedHeap:
    def test_push_pop(self):
        h = IndexedHeap()
        h.push("a", 3)
        h.push("b", 1)
        h.push("c", 2)
        assert h.pop() == "b"

    def test_update_priority(self):
        h = IndexedHeap()
        h.push("task1", 3)
        h.push("task2", 1)
        h.push("task1", 0)  # 更新优先级
        assert h.pop() == "task1"
