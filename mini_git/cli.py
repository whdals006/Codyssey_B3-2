"""Mini Git CLI와 REPL 인터페이스를 구현한다."""

import shlex
from datetime import datetime

from mini_git.models import Commit
from mini_git.repository import MiniGitError, MiniGitRepository


class MiniGitCLI:
    """사용자 명령을 해석하고 저장소 기능을 실행한다."""

    def __init__(self) -> None:
        """명령을 실행할 저장소를 준비한다."""
        self.repository = MiniGitRepository()

    def execute_line(self, line: str) -> bool:
        """사용자 입력 한 줄을 실행한다.

        Returns:
            True이면 REPL을 계속 실행하고, False이면 종료한다.
        """
        try:
            parts = shlex.split(line)
        except ValueError:
            print("Invalid args")
            return True

        if not parts:
            return True

        command = parts[0].upper()
        args = parts[1:]

        try:
            return self._dispatch(command, args, parts[0])
        except MiniGitError as error:
            print(str(error))
            return True

    def _dispatch(
        self,
        command: str,
        args: list[str],
        original_command: str,
    ) -> bool:
        """파싱된 명령어에 따라 저장소 기능을 실행한다."""

        if command in ("EXIT", "QUIT"):
            if args:
                raise MiniGitError("Invalid args")
            return False

        if command == "INIT":
            if len(args) != 1:
                raise MiniGitError("Invalid args")

            created = self.repository.initialize(args[0])

            if not created:
                print("Repository already initialized.")
            else:
                print("Initialized repository.")
                print("Current branch: main")
                print(f"Current user: {self.repository.current_user}")

            return True

        if command == "BRANCH":
            if len(args) != 1:
                raise MiniGitError("Invalid args")

            branch = self.repository.create_branch(args[0])
            print(f"Created branch: {branch.name}")
            return True

        if command == "SWITCH":
            if len(args) != 1:
                raise MiniGitError("Invalid args")

            branch = self.repository.switch_branch(args[0])
            print(f"Switched to branch: {branch.name}")
            return True

        if command == "COMMIT":
            if len(args) != 1:
                raise MiniGitError("Invalid args")

            commit = self.repository.create_commit(args[0])

            print(
                f"[{self.repository.current_branch} "
                f"{commit.hash}] {commit.message}"
            )
            return True

        if command == "LOG":
            sort_by = None

            if args:
                if (
                    len(args) != 1
                    or not args[0].lower().startswith("--sort-by=")
                ):
                    raise MiniGitError("Invalid args")

                sort_by = args[0].split("=", 1)[1].lower()

                if sort_by not in ("date", "author"):
                    raise MiniGitError("Invalid args")

            commits = self.repository.list_commits(
                sort_by=sort_by
            )
            self._print_log(commits)
            return True

        if command == "PATH":
            if len(args) != 2:
                raise MiniGitError("Invalid args")

            path = self.repository.find_shortest_path(
                args[0],
                args[1],
            )

            if path is None:
                print("No path")
            else:
                print(f"Path: {' -> '.join(path)}")

            return True

        if command == "ANCESTORS":
            if len(args) != 1:
                raise MiniGitError("Invalid args")

            ancestors = self.repository.get_ancestors(args[0])

            if not ancestors:
                print("No ancestors.")
                return True

            print(f"Ancestors of {args[0]}:")

            for commit in ancestors:
                print(f"- {commit.hash}: {commit.message}")

            return True

        if command == "SEARCH":
            if len(args) != 1:
                raise MiniGitError("Invalid args")

            query = args[0]

            if query.lower().startswith("--author="):
                author = query.split("=", 1)[1]

                if not author.strip():
                    raise MiniGitError("Invalid args")

                commits = self.repository.search_author(author)

            elif query.startswith("--"):
                raise MiniGitError("Invalid args")

            else:
                if not query.strip():
                    raise MiniGitError("Invalid args")

                commits = self.repository.search_keyword(query)

            self._print_search_results(commits)
            return True

        print(f"Unknown command: {original_command}")
        return True

    @staticmethod
    def _format_timestamp(commit: Commit) -> str:
        """커밋 타임스탬프를 사람이 읽을 수 있는 형태로 바꾼다."""
        return datetime.fromtimestamp(
            commit.timestamp
        ).strftime("%Y-%m-%d %H:%M:%S")

    def _print_log(self, commits: list[Commit]) -> None:
        """커밋 로그를 출력한다."""
        if not commits:
            print("No commits yet.")
            return

        for index, commit in enumerate(commits):
            if index > 0:
                print()

            timestamp = self._format_timestamp(commit)
            branch_names = self.repository.branch_names_for(
                commit.hash
            )

            branch_label = ""

            if branch_names:
                branch_label = f" [{', '.join(branch_names)}]"

            print(
                f"commit {commit.hash} "
                f"({commit.author}, {timestamp}){branch_label}"
            )
            print(commit.message)

    def _print_search_results(
        self,
        commits: list[Commit],
    ) -> None:
        """검색 결과를 출력한다."""
        if not commits:
            print("No commits found.")
            return

        print(f"Found {len(commits)} commit(s):")

        for commit in commits:
            timestamp = self._format_timestamp(commit)

            print(
                f"- {commit.hash}: {commit.message} "
                f"({commit.author}, {timestamp})"
            )


def run_repl() -> None:
    """사용자 입력을 반복해서 받아 실행하는 REPL을 시작한다."""
    cli = MiniGitCLI()

    while True:
        try:
            line = input("mini-git> ")
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nExiting Mini Git.")
            break

        if not cli.execute_line(line):
            break