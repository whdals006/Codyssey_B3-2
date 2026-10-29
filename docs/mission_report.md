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


## 5. Commit Graph 와 탐색 알고리즘 구현하기

### commit graph의 구조 이해하기

Git의 commit은 단순한 목록이 아니라, 각 commit이 부모 commit을 가리키는 graph 구조이다.

* `DAG` (Directed Acyclic Graph, 방향성 비순환 그래프)

    - **방향성**: 부모에서 자식으로 향하는 방향이 있다.
    - **비순환**: 어떤 commit에서 출발해 edge 방향대로 이동해서 다시 자기 자신으로 돌아올 수 없다.
    - **다중 부모**: commit은 부모가 업거나 하나 또는 여러개일 수 있다.

이번 코드에서는 2개의 딕셔너리로 commit 관계를 관리한다.

```python
self.commits: dict[str, Commit] = {}
self.children: dict[str, list[str]] = {}
```

`commits`은 해시로 commit을 빠르게 찾고,
`chidren`은 특정 commit의 자식 commit들을 조회하는 역할을 한다.

`Commit.parents`에는 부모 해시가 저장되고,
`children`에는 자식 해시가 저장된다.

따라서 부모 방향과 자식 방향 모두 탐색할 수 있다.

**왜 사이클이 생기지 않을까?**

`add_commit()`에서는 부모로 지정한 commit이 이미 존재하는지 검사한다.
새 commit이 기존 commit을 부모로 삼을 수 있지만, 기존 commit이 아직 존재하지 않는 새 commit을 새 부모로 삼는 상황은 만들 수 없다.
따라서 이 방식으로 commit을 추가하는 한 cycle이 생기지 않는다.

### 기본 LOG: 위상정렬

기본 `LOG`는 최신 commit부터 출력하는 방식이 아니라, 반드시 부모 commit이 자식 commit보다 먼저 출력되어야 한다.

이 조건을 만족시키는 알고리즘이 **위상 정렬(Topological Sort)**이다.

이번 코드에서는 **Kahn 알고리즘**을 사용한다.

핵심 흐름은 다음과 간다.

    ① 각 commit이 가진 부모의 수를 계산한다.
    ② 부모가 없는 commit부터 처리 목록에 넣는다.
    ③ commit을 처리하면서 자식 commit들의 부모 수를 하나씩 줄인다.
    ④ 부모 수가 0이 된 자식 commit을 처리 목록에 추가한다.
    ⑤ 모든 commit이 처리될 때까지 반복한다.

위상 정렬의 시간복잡도는 vertex(=node) 수를 V, edge 수를 E 라고 할 때, **O(V+E)** 이다.

### ANCESTORS: DFS로 모든 조상 찾기

`ANCESTORS`는 특정 commit보다 앞선 모든 조상 commit을 찾아야 한다.

이번 코드에서는 DFS(Depth First Search)를 사용한다.

```python
stack = list(self.commits[commit_hash].parents)
```

대상 commit의 부모를 stack에 넣고, 하나씩 꺼내 그 부모들을 다시 stack에 넣는 방식이다.

```python
if current_hash in ancestor_hashes:
    continue
```

이 부분은 이미 방문한 commit을 다시 처리하지 않게 막는 역할을 한다.
여러 commit이 같은 조상을 공유할 수 있으므로 중복 방문 방지는 중요한다.

조상을 찾는 탐색 자체는 O(V+E)의 시간복잡도를 가진다.
최종 결과는 위상 정렬 순서에 맞춰 반환하기 때문에 부모가 자식보다 먼저 출력된다.

### PATH: BFS로 최단 경로 찾기

`PATH`는 commit을 연결하는 edge 수가 가장 적은 경로를 찾아야 한다.

특히 이번 미션에서는 부모 방향으로만 이동하는 것이 아니라, **부모,자식 연결을 무방향 edge로 취급**한다.

**BFS를 사용하는 이유**

BFS(Breadth-First Search)는 시작점에서 가까운 vertex부터 차례대로 탐색을 한다. 따라서 처음 도착점을 발견한 경로는 edge 수 기준으로 최단 경로이다.

코드에서는 `previous` 딕셔너리에 각 node에 도달하기 직전에 node를 저장한다.

```python
previous[neighbor_hash] = current_hash
```

도착점에 도달하면 `_restore_path()`에서 이 기록을 역으로 따라가 전체 경로를 복원한다.

**최단 경로가 여러 개라면?**

요구사항에서는 같은 길이의 경로가 여러 개라면 `hash1 -> hash2 -> ...` 문자열이 사전순으로 가장 작은 경로를 선택해야 한다.

이를 위해 각 node의 이웃 목록을 직접 구현한 `merge_sort()`로 정렬한다.

```python
neighbors = merge_sort(
    neighbors,
    key=lambda value: value,
)
```

일반적으로 BFS의 시간복잡도는 O(V+E)지만, 이 구현은 사전순 선택을 위해 각 vertex의 이웃을 정렬하므로 정렬 비용이 추가된다.

각 vertex의 이웃 수를 $d_v$라고 할 때 추가 비용은 대략 다음과 같다.

$$
O\left(\sum_v d_v\log d_v\right)
$$

### 그래프 기능 테스트

```bash
python3 - <<'PY'
from mini_git.models import Commit
from mini_git.graph import CommitGraph

graph = CommitGraph()

# 공통 조상
graph.add_commit(
    Commit("a000", "Initial commit", "Alice", 1000.0)
)

# 두 갈래의 커밋
graph.add_commit(
    Commit("b001", "Branch A", "Alice", 1100.0, ("a000",))
)
graph.add_commit(
    Commit("b002", "Branch B", "Bob", 1200.0, ("a000",))
)

# 두 부모를 가진 그래프 노드.
# 그래프 알고리즘을 테스트하기 위한 데이터이며 merge 명령은 구현하지 않는다.
graph.add_commit(
    Commit(
        "c000",
        "Join branches",
        "Alice",
        1300.0,
        ("b001", "b002"),
    )
)

# 별도의 연결 요소: a000과 연결되지 않은 커밋
graph.add_commit(
    Commit("z999", "Independent commit", "Bob", 1400.0)
)

# 1. 위상 정렬 테스트
ordered = graph.topological_order()
ordered_hashes = [commit.hash for commit in ordered]

print("위상 정렬:", ordered_hashes)

position = {
    commit.hash: index
    for index, commit in enumerate(ordered)
}

for commit in ordered:
    for parent_hash in commit.parents:
        assert position[parent_hash] < position[commit.hash]

print("부모 우선 순서: 통과")

# 2. 조상 탐색 테스트
ancestors = graph.get_ancestors("c000")
ancestor_hashes = [commit.hash for commit in ancestors]

print("c000의 조상:", ancestor_hashes)

assert set(ancestor_hashes) == {"a000", "b001", "b002"}
assert "c000" not in ancestor_hashes

print("조상 탐색: 통과")

# 3. 최단 경로 테스트
path = graph.shortest_path("b001", "b002")
print("b001 -> b002:", path)

assert path == ["b001", "a000", "b002"]
print("최단 경로: 통과")

# 4. 사전순 동률 경로 테스트
path = graph.shortest_path("a000", "c000")
print("a000 -> c000:", path)

assert path == ["a000", "b001", "c000"]
print("사전순 경로 선택: 통과")

# 5. 경로가 없는 경우
path = graph.shortest_path("a000", "z999")
print("a000 -> z999:", path)

assert path is None
print("경로 없음 처리: 통과")

# 6. 존재하지 않는 부모 방지 테스트
try:
    graph.add_commit(
        Commit("bad1", "Invalid parent", "Alice", 1500.0, ("unknown",))
    )
except ValueError as error:
    print("잘못된 부모 처리:", error)
else:
    raise AssertionError("존재하지 않는 부모가 허용되었습니다.")

print("모든 그래프 테스트 통과!")
PY
```

결과값

```
b001 -> b002: ['b001', 'a000', 'b002']
최단 경로: 통과

a000 -> c000: ['a000', 'b001', 'c000']
사전순 경로 선택: 통과

a000 -> z999: None
경로 없음 처리: 통과

모든 그래프 테스트 통과!
```


## 6. 저장소 및 브랜치 관리 구현하기

이번 단계에서는 지금까지 만든 `Commit`, `CommitGraph`, `InvertedIndex`, `merge_sort()`를 하나로 연결한다.

`respository.py`는 저장소 초기화, 브랜치 생성 및 전환, commit 생성, log 조회, 검색, 그래프 탐색을 담당한다.

### 저장소 클래스의 역할

`MiniGitRepository`는 지금까지 만든 파일들의 독립된 기능들을 연결하고 현재 저장소의 상태를 관리한다.

### 브랜치와 HEAD의 관계

`branches`는 브랜치 이름으로 `Branch` 객체를 찾는 딕셔너리이다.

```python
self.branches: dict[str, Branch] = {}
```

각 브랜치는 `head_hash`로 자신이 가리키는 commit을 기억한다.
아직 commit이 하나도 없는 브랜치라면 `head_hash` 값은 `None`이다.

### commit 생성과 해시 관리

`creae_commit()`은 다음 순서로 실행된다.

    ① 저장소가 초기화되어 있는지 확인한다.
    ② commit message가 비어 있는지 검사한다.
    ③ session 내에서 중복되지 않는 commit hash를 생성한다.
    ④ 현재 HEAD를 새 commit의 부모로 설정한다.
    ⑤ commit graph와 Inverted Index를 갱신한다.
    ⑥ 현재 브랜치의 HEAD를 새 commit으로 변경한다.

최초 commit에는 부모가 없다.

```
Initial commit
parents = ()
```

두번째 commit부터는 현재 HEAD가 부모가 된다.

```
Initial commit
      |
Add login feature
```

### 저장소 기능 테스트

```bash
python3 - <<'PY'
from mini_git.repository import (
    MiniGitError,
    MiniGitRepository,
    UnknownBranchError,
    UnknownCommitError,
)

repo = MiniGitRepository()

# 1. 저장소 초기화
assert repo.initialize("Alice")
assert repo.initialized
assert repo.current_branch == "main"
assert repo.current_user == "Alice"
print("저장소 초기화: 통과")

# 2. 첫 번째 커밋 생성
initial = repo.create_commit("Initial commit")
assert initial.parents == ()
assert repo.current_head_hash == initial.hash
print("첫 번째 커밋:", initial.hash)

# 3. 브랜치 생성 및 전환
feature = repo.create_branch("feature")
assert feature.head_hash == initial.hash

repo.switch_branch("feature")
login = repo.create_commit("Add login feature")

assert login.parents == (initial.hash,)
assert repo.current_head_hash == login.hash
print("feature 브랜치 및 커밋 생성: 통과")

# 4. main으로 돌아와 별도의 커밋 생성
repo.switch_branch("main")
payment = repo.create_commit("Add payment feature")

assert payment.parents == (initial.hash,)
assert repo.current_head_hash == payment.hash
print("main 브랜치의 독립 커밋: 통과")

# 5. 부모 우선 기본 로그
commits = repo.list_commits()
hashes = [commit.hash for commit in commits]
print("기본 LOG:", hashes)

position = {
    commit.hash: index
    for index, commit in enumerate(commits)
}

for commit in commits:
    for parent_hash in commit.parents:
        assert position[parent_hash] < position[commit.hash]

print("부모 우선 로그: 통과")

# 6. 날짜 및 작성자 정렬
by_date = repo.list_commits(sort_by="date")
by_author = repo.list_commits(sort_by="author")

assert by_date[0].timestamp <= by_date[-1].timestamp
assert [
    commit.author.casefold() for commit in by_author
] == [
    "alice" for commit in by_author
]

print("날짜 및 작성자 정렬: 통과")

# 7. 키워드 및 작성자 검색
login_results = repo.search_keyword("LOGIN")
assert [commit.hash for commit in login_results] == [login.hash]

multi_results = repo.search_keyword("login feature")
assert [commit.hash for commit in multi_results] == [login.hash]

author_results = repo.search_author("alice")
assert len(author_results) == 3

print("키워드 및 작성자 검색: 통과")

# 8. 그래프 탐색
path = repo.find_shortest_path(login.hash, payment.hash)
assert path == [
    login.hash,
    initial.hash,
    payment.hash,
]

ancestors = repo.get_ancestors(login.hash)
assert [commit.hash for commit in ancestors] == [initial.hash]

print("최단 경로 및 조상 탐색: 통과")

# 9. 잘못된 입력 확인
try:
    repo.switch_branch("unknown")
except UnknownBranchError:
    print("존재하지 않는 브랜치 처리: 통과")
else:
    raise AssertionError("존재하지 않는 브랜치가 허용되었습니다.")

try:
    repo.find_shortest_path(login.hash, "unknown")
except UnknownCommitError:
    print("존재하지 않는 커밋 처리: 통과")
else:
    raise AssertionError("존재하지 않는 커밋이 허용되었습니다.")

try:
    repo.create_commit("   ")
except MiniGitError:
    print("빈 커밋 메시지 처리: 통과")
else:
    raise AssertionError("빈 커밋 메시지가 허용되었습니다.")

print("모든 저장소 테스트 통과!")
PY
```

결과

```
저장소 초기화: 통과
첫 번째 커밋: 000000000001
feature 브랜치 및 커밋 생성: 통과
main 브랜치의 독립 커밋: 통과
기본 LOG: [...]
부모 우선 로그: 통과
날짜 및 작성자 정렬: 통과
키워드 및 작성자 검색: 통과
최단 경로 및 조상 탐색: 통과
존재하지 않는 브랜치 처리: 통과
존재하지 않는 커밋 처리: 통과
빈 커밋 메시지 처리: 통과
모든 저장소 테스트 통과!
```

