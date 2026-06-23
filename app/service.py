from app.loader import DictionaryLoader
from app.trie import Trie


DEFAULT_LIMIT = 4


class AutocompleteService:
    def __init__(self, dictionary_path: str = "data/dictionary.txt", limit: int = DEFAULT_LIMIT):
        self.trie = Trie()
        self.limit = limit
        self._build(dictionary_path)

    def _build(self, path: str):
        loader = DictionaryLoader()
        words = loader.load(path)

        for word in words:
            self.trie.insert(word)

    def autocomplete(self, query: str | None) -> list[str]:
        if query is None:
            return []

        query = query.strip()

        if not query:
            return []

        results = self.trie.search(query)
        return results[:self.limit]