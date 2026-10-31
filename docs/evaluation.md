# 동료평가

## 7. 커밋 저장소/브랜치/HEAD/사용자 정보를 어떤 구조로 분리했고, 각 책임을 설명할 수 있는가?

| 구분 | 저장 위치 | 자료구조 및 변수 | 책임 |
| :--- | :--- | :--- | :--- |
| 커밋 저장소 | graph.py | commits: dict | commit hash를 key로 Commit 객체 관리 |
| 브랜치 | repository.py | branches: dict | 브랜치 이름과 브랜치별 HEAD 관리 |
| HEAD | repository.py | current_branch | 현재 작업 중인 브랜치 지정 |
| 사용자 | repository.py | current_user | 현재 사용자의 이름 관리 |

## 8. 커밋 hash로 빠르게 조회하기 위해 어떤 키-값 구조를 사용했고, 중복/충돌을 어떻게 방지했는지 설명할 수 있는가?

### 어떤 key-value 구조를 사용했는가?

`graph.py` 의 `CommitGraph` 클래스에서 확인 가능

```python
commits = {commit_hash : Commit 객체}
```

dictionary를 사용하면 commit_hash를 이용해 특정 commit을 빠르게 조회 가능

시간복잡도 : O(1)

### commit hash의 충돌 방지

순차적으로 증가하는 번호를 16진수 문자열로 변환해서 commi hash로 사용.

처음 생성되는 commit의 commit number

```python
self._next_commit_number = 1
```

이후 생성되는 commit은 1씩 늘어난다.

```python
commit_hash = f"{self._next_commit_number:012x}"
self._next_commit_number += 1
```

번호가 계속 증가하기 때문에 이전에 사용한 hash와 절대 중복이 발생하지 않는다.

`graph.py` 에서 `add_commit()` 메서드에 한번 더 중복 hash가 있는지 검사를 한다.

```python
if commit.hash in self.commits:
    raise ValueError(
        f"Duplicate commit hash: {commit.hash}"
    )
```

## 9. 커밋이 추가될 때 역색인(author/keyword)을 어떤 시점에, 어떤 방식으로 갱신하도록 설계했는지 설명할 수 있는가?

### 언제 역색인이 갱신되는가?

commit이 생성되는 시점에서 역색인을 갱신하도록 설계했다.

`repository.py`의 `create_commit()` 메서드에서 확인 가능.

```python
self.graph.add_commit(commit)
self.index.add_commit(commit)
self.branches[self.current_branch].head_hash = commit.hash
```

① **commit 생성** - Commit 객체 생성 및 메타데이터 설정
② **commit graph** 등록
③ **역색인 갱식** - keyword / author 등록
④ **branch HEAD 갱신** - 현재 브랜치가 새 commit을 가리키도록 변경

### 어떤 방식으로 갱신되는가?

keyword와 author를 **key값**으로, commit hash를 **value값**으로 저장.

`index.py` 의 `add_commit()` 메서드

```python
def add_commit(self, commit: Commit) -> None:
    """새 커밋의 키워드와 작성자를 인덱스에 등록한다."""
    seen_keywords: set[str] = set()

    # 같은 메시지 안에서 키워드가 여러 번 나와도 한 번만 등록한다.
    for raw_token in commit.message.split():
        token = raw_token.lower()

        if token and token not in seen_keywords:
            self.keyword_to_hashes.setdefault(token, []).append(
                commit.hash
            )
            seen_keywords.add(token)
```

① commit message를 공백 기준으로 분리
② 각 단어를 소문자로 변환
③ `seen_keywords`를 이용해서 동일한 commit에서 중복되는 단어는 제거
④ 해당 keyword의 index에 commit hash를 추가

## 10. LOG, PATH, ANCESTORS에서 사용하는 그래프 탐색 로직을 어떻게 재사용 가능하게 구성했는지 설명할 수 있는가?

독립적인 클래스로 분리해서 재사용하도록 설계.

`graph.py` 에서 `CommitGraph` 클래스를 만들고 이 안에 graph 관련 기능을 모아 관리.

| 명령어 | 메서드 | 사용 알고리즘 | 역할 |
| :--- | :--- | :--- | :--- |
| `LOG` | topological_order() | 위상 정렬 | 부모 우선 commit 순서 반환 |
| `PATH` | shortest_path() | BFS | 두 commit 사이의 최단 경로 탐색 |
| `ANCESTORS` | get_ancestors() | DFS | 특정 commit의 모든 조상 탐색 |
| - | has_commit() | 딕셔너리 조회 | commit의 존재 여부 확인 |
| - | _restore_path() | 경로 복원 | BFS에서 찾은 최단 경로 복원 |

## 12. 커밋 그래프가 왜 DAG여야 하는지, 사이클이 생기면 어떤 문제가 발생하는지 설명할 수 있는가?

### commit graph는 왜 DAG여야 하는가?

부모 commit이 자식 commit보다 먼저 출력되어야 하기 때문.

DAG의 두가지 특성

* Directed(방향성) : edge에 방향이 존재
* Acyclic(비순환) : edge의 방향을 따라 이동햇을 때 자기 자신으로 돌아오는 경로가 없다.

이번 미션에서 commit간의 edge방향을 **부모 commit → 자식 commit** 으로 정의했다.

이 구조에서는 commit이 생성된 순서와 부모ㆍ자식 관계가 일관성을 유지한다.

A → B → C 의 관계에서 

A는 B의 부모
B는 C의 부모관계가 되는데, 

C에서 A방향으로 edge가 생기면 
C가 A의 부모가 되는 관계가 발생하면 안되기 때문에 순환이 되면 안된다.

### cycle이 생기면 어떤 문제가 발생하는가?

① 위상 정렬이 불가능해 진다.

    - 진입차수가 0인 노드를 찾을 수 없다.

② ANCESTORS 명령어에서 조상 관계가 잘못된다.

    - cycle이 발생하면 자기 자신이 자신의 조상으로 포함되는 문제가 발생.

## 13. LOG에서 “부모가 먼저” 조건을 만족시키기 위해 어떤 접근(예: 위상 정렬 성격의 출력)을 적용했는지 설명할 수 있는가?

### 어떤 알고리즘을 사용했는가?

위상 정렬의 Kahn 알고리즘을 사용

commit graph의 edge 방향은 부모에서 자식으로 향하도록 설계.

`graph.py` 에서 `topological_order()` 메서드

```python
indegree: dict[str, int] = {
    commit_hash: len(commit.parents)
    for commit_hash, commit in self.commits.items()
}
```

부모의 개수가 해당 commit의 진입 차수(indegree)이다.

시간복잡도는 O(V+E) 이다.

(모든 commit과 edge를 한번씩 처리하기 때문)

## 14. PATH에서 최단 경로를 찾기 위해 어떤 알고리즘(예: BFS)을 선택했고, 간선을 무방향으로 정의한 이유를 설명할 수 있는가?

### 어떤 알고리즘을 사용했는가?

BFS(Breadth-First-Search)를 사용.

BFS는 시작 node에서 가까운 node부터 차례대로 탐색하는 알고리즘.

최단 경로 = 두 commit 사이를 이동할 때 거쳐야 하는 edge의 개수가 최소인 경로

### 왜 edge를 무방향으로 정의했는가?

Git의 기본 commit graph는 부모 → 자식 방향성 그래프이다.

하지만 이번 미션 요구사항에서 PATH 명령어의 부모ㆍ자식 연결을 무방향 edge로 간주하도록 명시.

`graph.py`의 `shortedst_path()` 메서드

```python
# PATH에서는 부모와 자식 모두 이웃으로 취급한다.
neighbors = list(
    self.commits[current_hash].parents
)
neighbors.extend(self.children[current_hash])
```

`parents` : 현재 commit의 부모 목록
`children` : 현재 commit의 자식 목록

두 목록을 합쳐 부모와 자식 양쪽으로 이동할 수 있는 이웃 목록을 만듬.

## 15. 정렬 알고리즘의 평균/최악 시간복잡도와 안정 정렬 여부를 설명할 수 있는가?

(※ 위상정렬은 graph 알고리즘임. 정렬 알고리즘이 아님.)

### 시간복잡도

병합 정렬의 시간 복잡도 : O(n*log n)

### 왜 O(n*log n) 인가?

① 데이터를 절반씩 나누기 때문에 분할 단계가 (log n)번 발생.

```
Level 0:          [5, 2, 4, 7, 1, 3, 8, 6]        (총 8개, n = 8)
                        /              \
Level 1:          [5, 2, 4, 7]          [1, 3, 8, 6]      (각 4개씩 2묶음)
                    /      \              /      \
Level 2:         [5, 2]    [4, 7]      [1, 3]    [8, 6]   (각 2개씩 4묶음)
                 /    \    /    \      /    \    /    \
Level 3:       [5]   [2]  [4]  [7]    [1]  [3]  [8]  [6]   (크기가 1인 묶음들)
```

② 병합하는 단계는 O(n)의 시간이 필요. 

```
Level 3:       [5]   [2]  [4]  [7]    [1]  [3]  [8]  [6]
                 \    /    \    /      \    /    \    /
Level 2:         [2, 5]    [4, 7]      [1, 3]    [6, 8]   (두 개씩 정렬하며 합침)
                    \      /              \      /
Level 1:          [2, 4, 5, 7]          [1, 3, 6, 8]      (네 개씩 정렬하며 합침)
                        \              /
Level 0:          [1, 2, 3, 4, 5, 6, 7, 8]        (최종 완성!)
```

### 안정 정렬이란?

정렬 기준이 같은 데이터끼리 기존의 상대적인 순서를 유지하는 정렬.

`sorting.py`의 `merge_sort()` 메서드

```python
# 키가 같을 때 왼쪽 항목을 먼저 선택하여 안정성을 유지한다.
if take_left:
    merged.append(left[left_index])
    left_index += 1
else:
    merged.append(right[right_index])
    right_index += 1
```

두 데이터의 비교 key가 같으면 왼쪽 데이터를 먼저 선택한다.

## 16. 역색인이 순회 검색보다 빠른 이유를, 자료구조/시간복잡도 관점에서 설명할 수 있는가?

### 일반적인 순회 검색은 어떻게 동작하는가?

commit을 검색할 때마다 전체 commit을 하나씩 확인을 해야한다.

```python
for commit in commits:
    if "login" in commit.message.lower()
        results. append(commit)
```

전체 commit의 개수가 N 이라고 하면 시간복잡도는 O(N)이 된다.

### 역색인은 어떻게 동작하는가?

commit을 할때마다

딕셔너리 형태로 key값에는 keyword를, value값에는 commit hash 목록을 생성한다.

딕셔너리를 사용. 딕셔너리는 hash table 기반의 자료구조이기 때문에 key를 이용한 조회가 O(1)의 시간복잡도를 가진다.

## 17. 커밋 수가 10배 늘어났을 때 병목이 될 지점을 예측하고, 개선 방향(자료구조/알고리즘)을 설명할 수 있는가?

DFS를 사용하는 ANCESTORS 명령어가 문제가 될 수 있다.
기본적으로 stack 자료구조를 사용하기 때문에


## 18. PATH의 간선 정의를 “부모 방향만 허용”으로 바꾸면 결과가 어떻게 달라지고, 구현은 무엇을 바꿔야 하는지 설명할 수 있는가?

### 결과가 어떻게 달라지는가?

현재 코드는 PATH가 부모와 자식 양쪽으로 이동하는 undirected 탐색.
부모 방향으로만 허용으로 바꾸면 서로 다른 브랜치 사이의 commit 경로를 찾을 수 없다.

### 구현은 무서을 바꿔야 하는가?

`graph.py`의 `shortest_path()` 메서드

현재 코드

```python
# PATH에서는 부모와 자식 모두 이웃으로 취급한다.
neighbors = list(
    self.commits[current_hash].parents
)
neighbors.extend(self.children[current_hash])
```

변경 후 코드

```python
neighbors = list(
    self.commits[current_hash].parents
```

## 19. LOG --sort-by=author 요구사항이 “부모-자식 선후도 유지”로 강화된다면, 어떤 전략으로 해결할지 설명할 수 있는가?

작성자 이름순으로 정렬하면서도, 부모 commit이 자식 commit보다 먼저 출력되도록 만드는 방법

현재 `repository.py`의 `list_commits()` 메서드 코드

```python
commits = self.graph.topological_order()

if sort_by == "author":
    return merge_sort(
        commits,
        key=lambda commit: commit.author.casefold(),
    )
```

1. 먼저 **위상 정렬**로 부모 우선 순서를 만든다.
2. 그 결과를 작성자 이름 기준으로 다시 **병합 정렬**한다.

문제는 두번째 병합 정렬 과정에서 부모와 자식의 순서가 뒤바뀔 수 있다.

### 어떤 전략으로 해결할 수 있는가?

`위상정렬` + `우선순위 큐(Priority Queue)` 사용

위상 정렬 과정에서 Queue에 들어간 commit을 꺼낼 때, 작성자 이름이 가장 작은 commit을 꺼내도록 하면 된다.

## 20. 해시 생성 방식을 카운터 기반 ↔ 난수 기반으로 바꿀 때 테스트/재현성/디버깅에 미치는 영향을 설명할 수 있는가?

### 현재는 어떤 방식을 사용하는가?

카운터 기반 해시 생성 방식

`repository.py` 의 `__init__()`

```python
self._next_commit_number = 1
```

`repository.py` 의 `create_commit`

```python
while True:
    commit hash = f"(self ._ next_commit_number:012x}"
    self ._ next_commit_number += 1
```

순차적으로 증가하는 숫자를 16진수 문자열로 변환해서 commi hash로 사용.

### 난수 기반으로 변경한다면?

난수 기반은 commit을 생성할 때 무작위 값을 생성해 hash로 사용하는 방식.

(예시)

```python
import secrets

commit_hash = secrets.token_hex(6)
```

(결과)

```
a91f3c8d21b4
7e2a9f51c603
c82d4a10b735
```

난수를 사용한다고 해서 hash 중복이 절대 발생하지 않는 것은 아니다.

* 테스트

    - hash 생성 결과가 실행할 때마다 달라지기 때문에 테스트 결과를 미리 예측 할 수 없다.

* 재현성

    - 재현 못함

* 디버깅

    - 어려움

