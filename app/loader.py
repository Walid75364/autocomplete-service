from pathlib import Path


class DictionaryLoader:
    def load(self, relative_path: str):
        base_dir = Path(__file__).resolve().parent.parent
        file_path = base_dir / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"Dictionary not found: {file_path}")

        words = []

        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word:
                    words.append(word)

        return words