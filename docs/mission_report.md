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

@dataclass(`frozen=True`) 옵션으로 **불변객체**를 생성.

인스턴스 생성된 후 필드값을 변경할 수 없다.
인스턴스 생성된 후 필드값 수정 시 오류가 발생한다.

### Branch 클래스