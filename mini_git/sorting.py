"""Python 내장 정렬 API를 사용하지 않는 정렬 알고리즘."""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def merge_sort(
    items: list[T],
    key: Callable[[T], Any] | None = None,
    reverse: bool = False,
) -> list[T]:
    """리스트를 병합 정렬하고 새로운 리스트를 반환한다.

    Args:
        items: 정렬할 항목 목록.
        key: 각 항목의 비교 기준을 반환하는 함수.
        reverse: True이면 내림차순으로 정렬한다.

    Returns:
        정렬된 새로운 리스트.

    Notes:
        평균 및 최악 시간복잡도는 O(n log n)이다.
        같은 비교 키를 가진 항목의 상대적 순서를 유지하는 안정 정렬이다.
    """
    if key is None:
        key = lambda item: item

    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2

    left = merge_sort(
        items[:middle],
        key=key,
        reverse=reverse,
    )
    right = merge_sort(
        items[middle:],
        key=key,
        reverse=reverse,
    )

    merged: list[T] = []
    left_index = 0
    right_index = 0

    # 두 정렬된 리스트에서 비교 결과가 작은 항목부터 선택한다.
    while left_index < len(left) and right_index < len(right):
        left_key = key(left[left_index])
        right_key = key(right[right_index])

        if reverse:
            take_left = left_key >= right_key
        else:
            take_left = left_key <= right_key

        # 키가 같을 때 왼쪽 항목을 먼저 선택하여 안정성을 유지한다.
        if take_left:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    # 한쪽에 남은 항목을 순서대로 추가한다.
    while left_index < len(left):
        merged.append(left[left_index])
        left_index += 1

    while right_index < len(right):
        merged.append(right[right_index])
        right_index += 1

    return merged