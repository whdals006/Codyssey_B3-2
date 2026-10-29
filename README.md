# 파일이 언제 어떻게 바뀌었는지 기록하는 작은 프로그램 만들기

Python으로 구현한 메모리 기반 CLI 버전 관리 프로그램이다.

Git의 커밋 그래프, 브랜치, 검색 인덱스와 정렬 알고리즘의 동작 원리를 학습하는 것이 목적이다.

## 1. 개발 환경

- Python 3.12.3

## 2. 실행 방법

프로젝트 루트 디렉터리에서 실행한다.

```bash
python main.py
```

## 3. 지원 명령어

### 저장소 및 브랜치

* 저장소 초기화, main 브랜치 생성
```
INIT <user_name>
```

* 브랜치 생성
```
BRANCH <branch_name>
```

* 브랜치 전환
```
SWITCH <branch_name>
```

* 커밋 생성
```
COMMIT <commit_message>
```

문자열에 공백이 포함되면 따옴표로 감싼다.

```
(예시)

mini-git> INIT "Alice"
mini-git> COMMIT "Initial commit"
mini-git> BRANCH feature
mini-git> SWITCH feature
mini-git> COMMIT "Add login feature"
```

### commit 로그

* 커밋 로그 출력
```
LOG
```

* 날짜 오름차순 출력
```
LOG --sort-by=date
```

* 작성자 이름 기준 출력
```
LOG --sort-by=author
```

- 기본 LOG는 부모 커밋이 자식 커밋보다 먼저 출력된다.
- date는 타임스탬프 오름차순으로 정렬한다.
- author는 작성자 이름 기준으로 정렬한다.
- 정렬 옵션을 지정하면 지정한 정렬 기준을 우선한다.

### 그래프 탐색

* 경로 출력
```
PATH <commit1> <commit2>
```

```
ANCESTORS <commit_hash>
```

- PATH는 부모·자식 연결을 무방향 간선으로 간주한다.
- PATH는 간선 수가 최소인 경로를 반환한다.
- 최단 경로가 여러 개라면 사전순으로 가장 작은 경로를 선택한다.
- 경로가 없으면 `No path`를 출력한다.
- ANCESTORS는 대상 커밋 자신을 제외한 모든 조상을 출력한다.

### 검색

* 키워드로 commit 검색하기
```
SEARCH <keyword>
```

* 사용자 이름으로 commit 검색하기
```
SEARCH --author=<name>
```

키워드는 소문자로 정규화해 검색하며 작성자 검색은
대소문자를 구분하지 않는다.

여러 검색 토큰을 입력하면 모든 토큰을 포함한 커밋을 찾는다.

```
(예시)

mini-git> SEARCH "login feature"
mini-git> SEARCH --author="Alice"
```

### 종료

```
exit
```

또는

```
quit
```

명령어 이름은 대소문자를 구분하지 않는다.

## 4. 자료구조와 알고리즘

### 커밋 그래프

- 커밋은 해시를 키로 하는 딕셔너리에 저장한다.
- 커밋은 부모 커밋의 해시를 보관한다.
- 부모가 먼저 존재해야 새 커밋을 추가할 수 있으므로
  커밋 그래프에 사이클이 생기지 않는다.
- 기본 LOG는 Kahn 알고리즘을 이용한 위상 정렬을 사용한다.
- ANCESTORS는 깊이 우선 탐색(DFS)을 사용한다.
- PATH는 너비 우선 탐색(BFS)을 사용한다.

그래프의 정점 수를 V, 간선 수를 E라고 하면
위상 정렬과 DFS 탐색의 시간복잡도는 O(V + E)이다.
BFS 경로 탐색에도 O(V + E)의 그래프 순회가 사용되며,
사전순 경로 선택을 위해 이웃 목록을 추가로 정렬한다.

### 역색인

두 가지 역색인을 사용한다.

- keyword -> commit_hash 목록
- author -> commit_hash 목록

검색할 때 역색인에서 후보를 가져오기 때문에 모든 커밋을
매번 검사하는 순회 검색을 피할 수 있다.

### 정렬

병합 정렬(Merge Sort)을 직접 구현한다.

- 평균 시간복잡도: O(n log n)
- 최악 시간복잡도: O(n log n)
- 추가 공간복잡도: O(n)
- 같은 비교 키를 가진 항목의 상대 순서를 유지하는 안정 정렬

정렬이 필요한 기능은 구현한 병합 정렬을 이용하며
Python 내장 정렬 API는 사용하지 않는다.

## 5. 프로젝트 구조

```text
B3-2/
├── main.py
├── README.md
├── .gitignore
└── mini_git/
    ├── __init__.py
    ├── models.py
    ├── sorting.py
    ├── index.py
    ├── graph.py
    ├── repository.py
    └── cli.py
```

## 6. 범위 및 제한 사항

- 파일 내용 변경 내역을 추적하지 않는다.
- 네트워크 통신을 구현하지 않는다.
- 저장소 데이터의 파일 영속성을 구현하지 않는다.
- Diff와 Merge 등의 보너스 기능은 구현하지 않는다.