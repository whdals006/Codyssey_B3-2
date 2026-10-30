# 평가 시나리오

## 1. 저장소 초기화 및 첫 commit 생성

```
INIT Alice
COMMIT "Initial commit"
```

INIT 명령어로 저장소를 초기화하면, 자동으로 기본 브랜치인 main을 생성한다.

## 2. 브랜치 생성 및 분기

```
BRANCH feature
SWITCH feature
COMMIT "Add login feature"
SWITCH main
COMMIT "Add payment feature"
```

feature 브랜치를 생성하면 현재 HEAD가 가리키는 commit에서 분기를 합니다.

feature에서 commit을 생성한 뒤, main으로 돌아와 별도의 commit을 생성하면 두 브랜치는 공통 조상을 가지는 구조가 된다.

## 3. 로그 출력

```
mini-git> LOG
mini-git> LOG --sort-by=date
mini-git> LOG --sort-by=author
```

기본 LOG 명령어는 **위상 정렬**을 사용해서 부모 commit이 자식 commit보다 먼저 출력된다. (미션 요구사항)

정렬 옵션을 지정하면 날짜나 작성자 기준의 **병합 정렬**을 사용한다.

## 4. 최단 경로 및 조상 탐색

```
PATH 000000000002 000000000003
ANCESTORS 000000000002
```

PATH 명령어는 **BFS**(너비우선정렬)를 이용해서 edge 수가 가장 적은 경로를 찾는다.

ANCESTORS 명령어는 **DFS**(깊이우선정렬)를 이용해서 부모 방향을 따라가며 모든 조상을 탐색하고 중복 방문을 방지한다.

## 5. 역색인 검색

```
SEARCH login
SEARCH "login feature"
SEARCH --author=Alice
```

commit을 생성할 때 commit message 와 user_name을 **역색인**에 등록한다.

SEARCH 명령어로 검색 시 인덱스에서 관련 commit hash를 가져와서 결과를 반환한다.

여러 키워드를 입력하면 모든 키워드를 포함하는 commit만 검색한다.

## 6. 잘못된 입력 처리

```
SWITCH abcd
LOG --sort-by=abcd
abcd
```

존재하지 않는 브랜치를 입력했을 때,
잘못된 옵션을 입력했을 때,
알수없는 명령어를 입력했을 때,

오류 메시지를 출력하고 프로그램은 계속 실행된다.

## 종료

| 명령어 | 기능 |
| :--- | :--- |
| exit | 프로그램을 종료한다. |
| quit | 프로그램을 종료한다. |

## 명령어별 알고리즘 사용 이유

| 명령어 | 사용한 알고리즘 | 사용한 이유 |
| :--- | :--- | :--- |
| `LOG` | **위상 정렬** | 부모 커밋이 자식 커밋보다 먼저 출력되어야 하기 때문 |
| `LOG --sort-by` | **병합 정렬** | 날짜나 작성자 등 원하는 기준으로 직접 정렬하기 위해 |
| `PATH` | **BFS** | 두 커밋 사이의 간선 수가 가장 적은 최단 경로를 찾기 위해 |
| `ANCESTORS` | **DFS** | 특정 커밋에서 시작해 모든 조상 커밋을 빠짐없이 탐색하기 위해 |
| `SEARCH` | **역색인** | 모든 커밋을 순회하지 않고 키워드나 작성자에 해당하는 커밋을 빠르게 찾기 위해 |