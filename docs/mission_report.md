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


## 4. 역색인 구현하기

### 역색인(Inverted Index)란?

일반적으로 commit을 검색하는 가장 단순한 방법은 저장된 모든 commit을 하나씩 확인하는 것이다.

예를 들어 commit이 10,000개 있다면 `login`이라는 단어를 찾기 위해 최대 10,000개의 commit message를 검사할 수 있다.

**역색인**은 검색할 단어를 기준으로 관련 commit의 hash를 미리 기록해 두는 방식이다.

### 핵심 코드 이해하기

* `add_commit()`

```python
for raw_token in commit.message.split():
    token = raw_token.lower()

    if token and token not in seen_keywords:
        self.keyword_to_hashes.setdefault(token, []).append(
            commit.hash
        )
        seen_keywords.add(token)
```

이 코드는 commit message를 공백으로 분리하고, 각 단어를 소문자로 변환한 뒤 인덱스에 등록한다.

예를 들어 commit message가 다음과 같다면,

```
Add LOGIN feature login
```

실제로 등록되는 키워드는 다음과 같다.

```
add
login
feature
```

* `seen_keywords`

같은 message 안에서 `login`이 여러번 등장해도 해당 commit hash를 중복으로 등록하지 않는다.

* `setdefault()`

지정한 key가 아직 없으면 빈 리스트를 만들고, 있으면 기존 리스트를 반환한다. 따라서 새로운 단어와 기존 단어를 동일한 방식으로 처리할 수 있다.

* `search_keyword()`

검색어가 "login feature"라면 다음 순서로 처리한다.

    ① 검색어를 `login`, `feature` 두 토큰으로 분리한다.
    ② 각 토큰에 해당하는 commit hash 목록을 인덱스에 조회한다.
    ③ 두 목록의 교집합을 구한다.
    ④ 모두 검색 토큰이 포함된 commit만 반환한다.

따라서 message에 `login`만 있거나 `feature`만 있는 commit은 `"login feature"` 검색 결과에 포함되지 않는다.

* `search_author()`

```python
author_key = author.casefold()
```

작성자 이름은 `casefold()`로 정규화해서 대소문자 차이를 무시하고 검색한다.

예를 들어 인덱스에 `Alice`가 등록되어 있으면 `alice`, `ALICE`로 검색해도 같은 결과를 얻는다.

### 역색인 테스트

```bash
python3 - <<'PY'
from mini_git.models import Commit
from mini_git.index import InvertedIndex

index = InvertedIndex()

commits = [
    Commit(
        hash="a001",
        message="Add login feature",
        author="Alice",
        timestamp=1000.0,
    ),
    Commit(
        hash="a002",
        message="Fix login bug",
        author="Alice",
        timestamp=2000.0,
    ),
    Commit(
        hash="a003",
        message="Add payment feature",
        author="Bob",
        timestamp=3000.0,
    ),
]

for commit in commits:
    index.add_commit(commit)

print("login 검색:", index.search_keyword("login"))
print("login feature 검색:", index.search_keyword("login feature"))
print("Alice 검색:", index.search_author("Alice"))
print("alice 검색:", index.search_author("alice"))
print("없는 키워드 검색:", index.search_keyword("database"))
print("빈 검색어:", index.search_keyword(""))
PY
```

결과값

```
login 검색: ['a001', 'a002']
login feature 검색: ['a001']
Alice 검색: ['a001', 'a002']
alice 검색: ['a001', 'a002']
없는 키워드 검색: []
빈 검색어: []
```

이 결과로 `키워드 검색`, `여러 단어의 교집합 검색`, `작성자 검색`, `없는 키워드 검색` 까지 확인할 수 있다.

