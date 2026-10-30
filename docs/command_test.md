# Mini Git 명령어 전체 목록

* 실행

```bash
python3 main.py
```

## 저장소 및 브랜치 관리

| 명령어 | 기능 | 간단한 예시 |
| :--- | :--- | :--- |
| `INIT <user_name>` | 저장소를 초기화하고 main 브랜치를 생성한다. | INIT Alice |
| `BRANCH <branch_name>` | 현재 HEAD를 가리키는 새 브랜치를 만든다. |	BRANCH feature |
| `SWITCH <branch_name>` | 작업할 브랜치를 변경한다. | SWITCH feature |
| `COMMIT <commit_message>` | 새 커밋을 생성하고 현재 브랜치의 HEAD를 갱신한다. | COMMIT "Add login feature" |

- commit hash는 현재 프로그램에서 순차 번호를 16진수 문자열로 변환해 생성한다.

## 커밋 로그 및 그래프 탐색

| 명령어 | 기능 | 간단한 예시 |
| :--- | :--- | :--- |
| `LOG` | 부모 커밋이 자식 커밋보다 먼저 나오도록 로그를 출력한다. | LOG |
| `LOG --sort-by=date` | 커밋을 날짜 오름차순으로 정렬한다.	| LOG --sort-by=date |
| `LOG --sort-by=author` | 작성자 이름 기준으로 정렬한다. | LOG --sort-by=author |
| `PATH <commit_hash_1> <commit_hash_2>` | 두 커밋 사이의 최단 경로를 찾는다. |	PATH 000000000002 000000000003 |
| `ANCESTORS <commit_hash>` | 지정한 커밋의 모든 조상을 출력한다. | ANCESTORS 000000000002 |

- `PATH`는 부모 방향으로만 이동하는 것이 아니라 부모와 자식 간의 연결을 undirected edge로 간주한다.

- 최단 경로가 여러 개라면 사전순으로 가장 작은 경로를 선택하도록 구현했다.

- `ANCESTORS`는 대상 커밋 자신을 제외한 조상만 출력한다.

## 검색

| 명령어 | 기능	| 간단한 예시 |
| :--- | :--- | :--- |
| `SEARCH "키워드"` | 커밋 메시지에 키워드가 포함된 커밋을 검색한다. | SEARCH login |
| `SEARCH "키워드1 키워드2"` | 두 키워드를 모두 포함한 커밋을 검색한다. | SEARCH "login feature" |
| `SEARCH --author=<user_name>` | 작성자로 커밋을 검색한다. | SEARCH --author=Alice |

- 검색은 Inverted-Index를 이용하기 때문에 매번 전체 commit의 메시지를 처음부터  검사하지 않아도 된다.

- 예를 들어 `SEARCH "login feature"`는 `login`과 `feature` 두 키워드를 모두 가진 commit을 검색한다.

## 종료

| 명령어 | 기능 |
| :--- | :--- |
| exit | 프로그램을 종료한다. |
| quit | 프로그램을 종료한다. |

## 오류 처리

| 상황 | 간단한 예시 |
| :--- | :--- |
| 존재하지 않는 브랜치 오류를 출력한다. <br> 즉, 생성되지 않은 브랜치 이름을 입력했을 때 | SWITCH abcd |
| 잘못된 정렬 옵션 오류를 출력한다. <br> 즉, `date` 와 `author` 이외의 옵션을 입력했을 때 | LOG --sort-by=abcd |
| 알 수 없는 명령어 오류를 출력한다. <br> 즉, 저장되지 않은 명령어를 입력했을 때 | abcd |

## 주의사항

* 명령어 이름은 대소문자를 구분하지 않는다.
* 문자열에 공백이 포함되면 따옴표로 감싸야 한다.

    (예시)

    ```bash
    INIT "Alice Smith"
    COMMIT "Add login feature"
    SEARCH "login feature"
    SEARCH --author="Alice Smith"
    ```

