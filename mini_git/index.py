"""커밋 검색을 위한 역색인을 구현한다."""

from mini_git.models import Commit


class InvertedIndex:
    """키워드와 작성자별로 관련 커밋 해시를 저장한다."""

    def __init__(self) -> None:
        """검색에 사용할 두 종류의 인덱스를 초기화한다."""
        self.keyword_to_hashes: dict[str, list[str]] = {}
        self.author_to_hashes: dict[str, list[str]] = {}

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

        # 작성자 이름도 정규화하여 대소문자를 구분하지 않고 검색한다.
        author_key = commit.author.casefold()

        self.author_to_hashes.setdefault(
            author_key, []
        ).append(commit.hash)

    def search_keyword(self, keyword: str) -> list[str]:
        """모든 검색 토큰을 포함한 커밋 해시를 반환한다.

        여러 토큰이 입력되면 각 토큰의 검색 결과에 모두 포함된
        커밋만 반환한다. 결과는 첫 번째 토큰의 인덱스 등록 순서를 따른다.
        """
        tokens = [
            token.lower()
            for token in keyword.split()
            if token
        ]

        if not tokens:
            return []

        # 각 키워드에 해당하는 게시 목록을 먼저 확인한다.
        postings: list[set[str]] = []

        for token in tokens:
            commit_hashes = self.keyword_to_hashes.get(token)

            if not commit_hashes:
                return []

            postings.append(set(commit_hashes))

        # 모든 토큰의 검색 결과에 공통으로 있는 커밋만 남긴다.
        matched_hashes = postings[0].copy()

        for posting in postings[1:]:
            matched_hashes.intersection_update(posting)

        first_token_hashes = self.keyword_to_hashes[tokens[0]]

        return [
            commit_hash
            for commit_hash in first_token_hashes
            if commit_hash in matched_hashes
        ]

    def search_author(self, author: str) -> list[str]:
        """작성자 이름으로 커밋 해시 목록을 검색한다."""
        author_key = author.casefold()

        return list(self.author_to_hashes.get(author_key, []))