"""Mini Git에서 사용하는 데이터 모델을 정의한다."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Commit:
    """하나의 커밋이 가진 메타데이터를 표현한다."""

    hash: str
    message: str
    author: str
    timestamp: float
    parents: tuple[str, ...] = ()


@dataclass
class Branch:
    """브랜치 이름과 현재 브랜치가 가리키는 커밋을 표현한다."""

    name: str
    head_hash: str | None = None