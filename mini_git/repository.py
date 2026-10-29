"""Mini Git의 저장소와 주요 명령 기능을 관리한다."""

import time

from mini_git.graph import CommitGraph
from mini_git.index import InvertedIndex
from mini_git.models import Branch, Commit
from mini_git.sorting import merge_sort


class MiniGitError(Exception):
    """Mini Git에서 발생하는 사용자 처리 가능 오류."""


class UnknownBranchError(MiniGitError):
    """존재하지 않는 브랜치를 요청했을 때 발생한다."""


class UnknownCommitError(MiniGitError):
    """존재하지 않는 커밋을 요청했을 때 발생한다."""


class MiniGitRepository:
    """메모리 기반 Mini Git 저장소를 관리한다."""

    def __init__(self) -> None:
        """저장소의 기본 상태를 초기화한다."""
        self.current_user: str | None = None
        self.current_branch: str | None = None

        self.branches: dict[str, Branch] = {}
        self.graph = CommitGraph()
        self.index = InvertedIndex()

        self._next_commit_number = 1

    @property
    def initialized(self) -> bool:
        """저장소 초기화가 완료되었는지 반환한다."""
        return (
            self.current_user is not None
            and self.current_branch is not None
        )

    @property
    def current_head_hash(self) -> str | None:
        """현재 브랜치가 가리키는 커밋 해시를 반환한다."""
        if self.current_branch is None:
            return None

        branch = self.branches.get(self.current_branch)

        if branch is None:
            return None

        return branch.head_hash

    def _ensure_initialized(self) -> None:
        """저장소 초기화 여부를 검사한다."""
        if not self.initialized:
            raise MiniGitError(
                "Repository not initialized. "
                "Run INIT <user_name> first."
            )

    def initialize(self, user_name: str) -> bool:
        """저장소와 main 브랜치를 초기화한다.

        이미 초기화된 저장소의 데이터를 실수로 지우지 않도록
        재초기화 요청은 거부한다.
        """
        if not user_name.strip():
            raise MiniGitError("Invalid args")

        if self.initialized:
            return False

        self.current_user = user_name.strip()
        self.current_branch = "main"
        self.branches["main"] = Branch(name="main")

        return True

    def create_branch(self, branch_name: str) -> Branch:
        """현재 HEAD를 가리키는 새 브랜치를 만든다."""
        self._ensure_initialized()

        name = branch_name.strip()

        if not name:
            raise MiniGitError("Invalid args")

        if name in self.branches:
            raise MiniGitError(
                f"Branch already exists: {name}"
            )

        branch = Branch(
            name=name,
            head_hash=self.current_head_hash,
        )
        self.branches[name] = branch

        return branch

    def switch_branch(self, branch_name: str) -> Branch:
        """현재 작업 브랜치를 변경한다."""
        self._ensure_initialized()

        name = branch_name.strip()

        if name not in self.branches:
            raise UnknownBranchError(
                f"Unknown branch: {name}"
            )

        self.current_branch = name
        return self.branches[name]

    def create_commit(self, message: str) -> Commit:
        """현재 HEAD를 부모로 하는 새 커밋을 만든다."""
        self._ensure_initialized()

        commit_message = message.strip()

        if not commit_message:
            raise MiniGitError("Invalid args")

        # 순차 번호를 16진수 문자열로 변환한다.
        # 번호가 계속 증가하므로 세션 안에서 해시가 중복되지 않는다.
        while True:
            commit_hash = f"{self._next_commit_number:012x}"
            self._next_commit_number += 1

            if not self.graph.has_commit(commit_hash):
                break

        parent_hash = self.current_head_hash

        if parent_hash is None:
            parents: tuple[str, ...] = ()
        else:
            parents = (parent_hash,)

        commit = Commit(
            hash=commit_hash,
            message=commit_message,
            author=self.current_user,
            timestamp=time.time(),
            parents=parents,
        )

        # 그래프 → 역색인 → 브랜치 HEAD 순서로 상태를 갱신한다.
        self.graph.add_commit(commit)
        self.index.add_commit(commit)
        self.branches[self.current_branch].head_hash = commit.hash

        return commit

    def list_commits(
        self,
        sort_by: str | None = None,
    ) -> list[Commit]:
        """기본 위상 정렬 로그 또는 지정 기준의 정렬 로그를 반환한다."""
        self._ensure_initialized()

        commits = self.graph.topological_order()

        if sort_by is None:
            return commits

        if sort_by == "date":
            return merge_sort(
                commits,
                key=lambda commit: commit.timestamp,
            )

        if sort_by == "author":
            return merge_sort(
                commits,
                key=lambda commit: commit.author.casefold(),
            )

        raise MiniGitError("Invalid args")

    def search_keyword(self, keyword: str) -> list[Commit]:
        """역색인을 사용하여 메시지 키워드에 해당하는 커밋을 검색한다."""
        self._ensure_initialized()

        commit_hashes = self.index.search_keyword(keyword)
        candidates = [
            self.graph.commits[commit_hash]
            for commit_hash in commit_hashes
        ]

        return merge_sort(
            candidates,
            key=lambda commit: commit.timestamp,
        )

    def search_author(self, author: str) -> list[Commit]:
        """역색인을 사용하여 작성자에 해당하는 커밋을 검색한다."""
        self._ensure_initialized()

        commit_hashes = self.index.search_author(author)
        candidates = [
            self.graph.commits[commit_hash]
            for commit_hash in commit_hashes
        ]

        return merge_sort(
            candidates,
            key=lambda commit: commit.timestamp,
        )

    def find_shortest_path(
        self,
        start_hash: str,
        end_hash: str,
    ) -> list[str] | None:
        """두 커밋 사이의 최단 경로를 검색한다."""
        self._ensure_initialized()

        if not self.graph.has_commit(start_hash):
            raise UnknownCommitError(
                f"Unknown commit: {start_hash}"
            )

        if not self.graph.has_commit(end_hash):
            raise UnknownCommitError(
                f"Unknown commit: {end_hash}"
            )

        return self.graph.shortest_path(
            start_hash,
            end_hash,
        )

    def get_ancestors(self, commit_hash: str) -> list[Commit]:
        """특정 커밋의 모든 조상을 조회한다."""
        self._ensure_initialized()

        if not self.graph.has_commit(commit_hash):
            raise UnknownCommitError(
                f"Unknown commit: {commit_hash}"
            )

        return self.graph.get_ancestors(commit_hash)

    def branch_names_for(self, commit_hash: str) -> list[str]:
        """현재 해당 커밋을 가리키는 브랜치 이름을 반환한다."""
        return [
            branch.name
            for branch in self.branches.values()
            if branch.head_hash == commit_hash
        ]