"""커밋 DAG와 그래프 탐색 알고리즘을 구현한다."""

from mini_git.models import Commit
from mini_git.sorting import merge_sort


class CommitGraph:
    """커밋과 커밋 간 부모·자식 관계를 관리한다."""

    def __init__(self) -> None:
        """커밋 저장소와 자식 관계를 초기화한다."""
        self.commits: dict[str, Commit] = {}
        self.children: dict[str, list[str]] = {}

    def has_commit(self, commit_hash: str) -> bool:
        """주어진 해시의 커밋이 존재하는지 확인한다."""
        return commit_hash in self.commits

    def add_commit(self, commit: Commit) -> None:
        """새 커밋을 등록하고 부모의 자식 목록을 갱신한다.

        부모 커밋은 이미 존재해야 한다. 기존 커밋만 부모로
        지정할 수 있기 때문에 새로운 커밋으로 사이클이 생기지 않는다.
        """
        if commit.hash in self.commits:
            raise ValueError(
                f"Duplicate commit hash: {commit.hash}"
            )

        for parent_hash in commit.parents:
            if parent_hash not in self.commits:
                raise ValueError(
                    f"Unknown parent commit: {parent_hash}"
                )

        self.commits[commit.hash] = commit
        self.children[commit.hash] = []

        # 부모에서 자식으로 이동하는 간선을 기록한다.
        for parent_hash in commit.parents:
            self.children[parent_hash].append(commit.hash)

    def topological_order(self) -> list[Commit]:
        """부모 커밋이 자식 커밋보다 먼저 나오도록 정렬한다.

        Kahn 알고리즘을 사용한다. 현재 커밋의 부모 개수를
        진입 차수로 사용하고, 부모가 모두 처리된 커밋을 추가한다.
        """
        indegree: dict[str, int] = {
            commit_hash: len(commit.parents)
            for commit_hash, commit in self.commits.items()
        }

        # 부모가 없는 커밋부터 처리한다.
        ready = [
            commit_hash
            for commit_hash, degree in indegree.items()
            if degree == 0
        ]

        result: list[Commit] = []
        queue_index = 0

        while queue_index < len(ready):
            current_hash = ready[queue_index]
            queue_index += 1

            result.append(self.commits[current_hash])

            for child_hash in self.children[current_hash]:
                indegree[child_hash] -= 1

                if indegree[child_hash] == 0:
                    ready.append(child_hash)

        if len(result) != len(self.commits):
            raise RuntimeError("Commit graph contains a cycle.")

        return result

    def get_ancestors(self, commit_hash: str) -> list[Commit]:
        """특정 커밋에서 도달 가능한 모든 조상을 반환한다.

        대상 커밋 자신은 결과에 포함하지 않는다.
        중복 방문을 방지하고, 결과는 부모 우선 순서로 반환한다.
        """
        if commit_hash not in self.commits:
            raise KeyError(commit_hash)

        ancestor_hashes: set[str] = set()
        stack = list(self.commits[commit_hash].parents)

        # 스택을 사용한 깊이 우선 탐색(DFS)을 수행한다.
        while stack:
            current_hash = stack.pop()

            if current_hash in ancestor_hashes:
                continue

            ancestor_hashes.add(current_hash)

            stack.extend(
                self.commits[current_hash].parents
            )

        return [
            commit
            for commit in self.topological_order()
            if commit.hash in ancestor_hashes
        ]

    def shortest_path(
        self,
        start_hash: str,
        end_hash: str,
    ) -> list[str] | None:
        """부모·자식 연결을 무방향으로 보았을 때의 최단 경로를 찾는다.

        BFS를 이용한다. 같은 길이의 경로가 여러 개라면 이웃을
        해시 사전순으로 탐색하여 사전순으로 가장 작은 경로를 선택한다.

        반환값은 경로의 해시 목록이며, 경로가 없으면 None이다.
        """
        if (
            start_hash not in self.commits
            or end_hash not in self.commits
        ):
            return None

        if start_hash == end_hash:
            return [start_hash]

        # 이전 노드를 기록하면 최단 경로를 복원할 수 있다.
        previous: dict[str, str | None] = {
            start_hash: None
        }

        queue = [start_hash]
        queue_index = 0

        while queue_index < len(queue):
            current_hash = queue[queue_index]
            queue_index += 1

            # PATH에서는 부모와 자식 모두 이웃으로 취급한다.
            neighbors = list(
                self.commits[current_hash].parents
            )
            neighbors.extend(self.children[current_hash])

            # 내장 정렬 API 대신 직접 구현한 정렬을 사용한다.
            neighbors = merge_sort(
                neighbors,
                key=lambda value: value,
            )

            for neighbor_hash in neighbors:
                if neighbor_hash in previous:
                    continue

                previous[neighbor_hash] = current_hash

                # BFS에서 처음 발견된 경로가 최단 경로다.
                if neighbor_hash == end_hash:
                    return self._restore_path(
                        previous,
                        end_hash,
                    )

                queue.append(neighbor_hash)

        return None

    @staticmethod
    def _restore_path(
        previous: dict[str, str | None],
        end_hash: str,
    ) -> list[str]:
        """이전 노드 기록을 이용해 시작점부터 도착점까지 복원한다."""
        path: list[str] = []
        current_hash: str | None = end_hash

        while current_hash is not None:
            path.append(current_hash)
            current_hash = previous[current_hash]

        return path[::-1]