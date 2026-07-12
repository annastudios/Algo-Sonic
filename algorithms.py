"""
Each function below is a generator that sorts/searches `arr` in place and
yields one small tuple per meaningful step:

    ("compare", i, j)   comparing two indices
    ("swap", i, j)      swapping two indices
    ("visit", i)        looking at a single index (search algorithms)
    ("set", i, val)      overwriting arr[i] with val (merge sort's writeback)

The engine just needs to call next() on whichever generator is active and
react to whatever tuple comes out - the algorithm itself has no idea
audio or video exists.
"""


def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            yield ("compare", j, j + 1)
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                yield ("swap", j, j + 1)


def insertion_sort(arr):
    for i in range(1, len(arr)):
        j = i
        while j > 0:
            yield ("compare", j - 1, j)
            if arr[j - 1] > arr[j]:
                arr[j - 1], arr[j] = arr[j], arr[j - 1]
                yield ("swap", j - 1, j)
                j -= 1
            else:
                break


def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield ("compare", min_idx, j)
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            yield ("swap", i, min_idx)


def quick_sort(arr):
    def partition(lo, hi):
        pivot = arr[hi]
        i = lo
        for j in range(lo, hi):
            yield ("compare", j, hi)
            if arr[j] < pivot:
                arr[i], arr[j] = arr[j], arr[i]
                if i != j:
                    yield ("swap", i, j)
                i += 1
        arr[i], arr[hi] = arr[hi], arr[i]
        yield ("swap", i, hi)
        return i

    def sort(lo, hi):
        if lo >= hi:
            return
        p = yield from partition(lo, hi)
        yield from sort(lo, p - 1)
        yield from sort(p + 1, hi)

    yield from sort(0, len(arr) - 1)


def merge_sort(arr):
    def sort(lo, hi):
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        yield from sort(lo, mid)
        yield from sort(mid, hi)

        merged = []
        left, right = lo, mid
        while left < mid and right < hi:
            yield ("compare", left, right)
            if arr[left] <= arr[right]:
                merged.append(arr[left])
                left += 1
            else:
                merged.append(arr[right])
                right += 1
        merged.extend(arr[left:mid])
        merged.extend(arr[right:hi])

        for offset, val in enumerate(merged):
            idx = lo + offset
            arr[idx] = val
            yield ("set", idx, val)

    yield from sort(0, len(arr))


def heap_sort(arr):
    n = len(arr)

    def sift_down(root, end):
        while True:
            child = 2 * root + 1
            if child > end:
                break
            if child + 1 <= end:
                yield ("compare", child, child + 1)
                if arr[child] < arr[child + 1]:
                    child += 1
            yield ("compare", root, child)
            if arr[root] < arr[child]:
                arr[root], arr[child] = arr[child], arr[root]
                yield ("swap", root, child)
                root = child
            else:
                break

    for start in range((n - 2) // 2, -1, -1):
        yield from sift_down(start, n - 1)

    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        yield ("swap", 0, end)
        yield from sift_down(0, end - 1)


def linear_search(arr, target):
    """Works on unsorted data - unlike binary search, no ordering required."""
    for i in range(len(arr)):
        yield ("visit", i)
        if arr[i] == target:
            return


def binary_search(arr, target):
    """arr must already be sorted."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        yield ("visit", mid)
        if arr[mid] == target:
            return
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1


ALGORITHMS = {
    "Bubble Sort": bubble_sort,
    "Insertion Sort": insertion_sort,
    "Selection Sort": selection_sort,
    "Quick Sort": quick_sort,
    "Merge Sort": merge_sort,
    "Heap Sort": heap_sort,
    "Linear Search": linear_search,
    "Binary Search": binary_search,
}

# needed for switch-algorithm to set up the array correctly, and for the
# info panel - kept as plain data next to the algorithms it describes
NEEDS_TARGET = {"Linear Search", "Binary Search"}
NEEDS_SORTED = {"Binary Search"}

DESCRIPTIONS = {
    "Bubble Sort": {
        "desc": "Repeatedly steps through the array, swapping adjacent elements "
                "that are out of order. Each pass bubbles the largest remaining "
                "value to the end.",
        "time": "Best: O(n)   Avg/Worst: O(n^2)",
        "space": "O(1)",
    },
    "Insertion Sort": {
        "desc": "Builds the sorted array one element at a time, taking each new "
                "element and sliding it left into its correct position among the "
                "already-sorted elements.",
        "time": "Best: O(n)   Avg/Worst: O(n^2)",
        "space": "O(1)",
    },
    "Selection Sort": {
        "desc": "Repeatedly scans the unsorted remainder for the smallest value "
                "and swaps it into place at the front. Fewer swaps than bubble "
                "sort, but still scans everything every pass.",
        "time": "Best/Avg/Worst: O(n^2)",
        "space": "O(1)",
    },
    "Quick Sort": {
        "desc": "Picks a pivot, partitions the array so smaller values end up on "
                "one side and larger on the other, then recursively sorts each "
                "side. Fast in practice despite worst-case O(n^2).",
        "time": "Best/Avg: O(n log n)   Worst: O(n^2)",
        "space": "O(log n) (recursion stack)",
    },
    "Merge Sort": {
        "desc": "Recursively splits the array in half until pieces are trivially "
                "sorted, then merges sorted halves back together in order. "
                "Predictable performance, needs extra memory for the merge.",
        "time": "Best/Avg/Worst: O(n log n)",
        "space": "O(n)",
    },
    "Heap Sort": {
        "desc": "Builds a max-heap out of the array, then repeatedly swaps the "
                "largest element (the root) to the end and shrinks the heap. "
                "In-place and never degrades to O(n^2).",
        "time": "Best/Avg/Worst: O(n log n)",
        "space": "O(1)",
    },
    "Linear Search": {
        "desc": "Checks every element in order until it finds the target (or "
                "runs out). Works on unsorted data - the tradeoff for not "
                "needing binary search's sorted-array requirement.",
        "time": "Best: O(1)   Avg/Worst: O(n)",
        "space": "O(1)",
    },
    "Binary Search": {
        "desc": "Repeatedly halves a sorted array: compares the target to the "
                "middle element and discards the half that can't contain it. "
                "Requires the data to already be sorted.",
        "time": "Best: O(1)   Avg/Worst: O(log n)",
        "space": "O(1)",
    },
}
