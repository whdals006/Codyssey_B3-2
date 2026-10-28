# mini Git 만들기


## 1. 프로젝트 기본 구조 만들기

```
B3-2/
├── mini_git/
│    └── __init__.py
│
├── .gitignore
└── README.md
```


## 2. 데이터 모델 만들기

Mini Git 에서 사용하는 데이터 모델을 정의

### Commit 클래스

* @dataclass(`frozen=True`) 옵션으로 **불변객체**를 생성.

    - 인스턴스 생성된 후 필드값을 변경할 수 없다.
    - 인스턴스 생성된 후 필드값 수정 시 오류가 발생한다.

### Branch 클래스

* `Branch` 는 새로운 commit이 생성될 때, `head_hash`를 갱신해야 하므로 필드값이 변경가능 해야 한다.


## 3. 정렬 알고리즘 구현하기

Python의 `sorted()`와 `list.sort()`를 사용하지 않는 **병합 정렬(Merge Sort)** 을 구현한다.

### 병합 정렬의 동작 원리 이해하기

병합 정렬은 크게 **분할 → 정렬 → 병합** 순서로 동작한다.

### 각 코드에서 하는 역할

| 코드 | 역할 |
| :--- | :--- |
| `len(items) <= 1` | 더 이상 분할할 필요가 없는 종료 조건 |
| `middle = len(items) // 2` | 목록을 절반으로 나누는 기준 |
| `items[:middle]` | 왼쪽 절반 |
| `items[middle:]` | 오른쪽 절반 |
| `while ...` | 양쪽의 원소를 비교해 작은 쪽부터 병합 |
| `key` | 무엇을 기준으로 비교할지 결정 |
| `reverse` | 오름차순 또는 내림차순 결정 |

key 매개변수 덕분에 숫자뿐 아니라 커밋 객체도 정렬할 수 있다.

### 정렬 알고리즘 테스트

```bash
python3 - <<'PY'
from mini_git.sorting import merge_sort

numbers = [7, 2, 5, 1, 9, 3]

print("원본:", numbers)
print("오름차순:", merge_sort(numbers))
print("내림차순:", merge_sort(numbers, reverse=True))

people = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 20},
    {"name": "Charlie", "age": 25},
]

result = merge_sort(people, key=lambda person: person["age"])

print("나이순:", result)
print("원본 유지:", numbers)
PY
```

결과

```
원본: [7, 2, 5, 1, 9, 3]
오름차순: [1, 2, 3, 5, 7, 9]
내림차순: [9, 7, 5, 3, 2, 1]
나이순: [{'name': 'Bob', 'age': 20}, {'name': 'Alice', 'age': 25}, {'name': 'Charlie', 'age': 25}]
원본 유지: [7, 2, 5, 1, 9, 3]
```

### 시간복잡도 이해하기

| 항목 | 병합 정렬 |
| :--- | :--- |
| 평균 시간복잡도 |	\(O(n\log n)\) |
| 최악 시간복잡도 |	\(O(n\log n)\) |
| 안정 정렬	| 예 |
| 원본 목록 변경 | 아니요 |

목록을 계속 절반으로 나누면 분할 단계는 약 \(\log n\)번 발생한다. 
각 단계에서 전체 원소를 병합하는 데 \(O(n)\)이 걸리므로 전체 시간복잡도는 \(O(n\log n)\)이 된다.

주의할 점은 **안정 정렬**이란 비교 기준이 같은 데이터의 상대적인 순서를 유지한다는 의미이다. 예를 들어 작성자 이름이 같은 두 커밋이 있다면 별도의 동률 기준을 추가하지 않는 한 먼저 들어온 커밋이 먼저 남는다.