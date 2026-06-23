"""
Script d'import générique pour tous les formats de dictionnaires EFF.

Formats supportés:
1. eff_large_wordlist.txt : "11111\tabacus" (numéro + tab + mot)
2. gameofthrones_8k-2018.txt : "abacus" (mot seul, 1 par ligne)
3. starwars_8k_2018.txt : "abacus" (mot seul, 1 par ligne)
4. memory-alpha_8k_2018.txt : "abacus" (mot seul, 1 par ligne)
5. harrypotter_8k_3column-txt.txt : "11111\tabacus\t" (numéro + tab + mot + tab)

Usage:
    python scripts/import_eff.py --source data/eff_large_wordlist.txt --target data/dictionary.txt
    python scripts/import_eff.py --source data/gameofthrones_8k-2018.txt --target data/dictionary.txt
    python scripts/import_eff.py --source data/starwars_8k_2018.txt --target data/dictionary.txt
"""

import argparse
import re
from pathlib import Path


def detect_format(lines: list[str]) -> str:
    """Détecte automatiquement le format du fichier EFF."""
    if not lines:
        return "empty"

    sample = lines[:min(10, len(lines))]

    # Format 3 colonnes Harry Potter: "11111\tabacus\t"
    three_col = sum(1 for line in sample if line.count("\t") >= 2)
    if three_col >= 3:
        return "three_column"

    # Format large wordlist: "11111\tabacus"
    tab_separated = sum(1 for line in sample if "\t" in line)
    if tab_separated >= 3:
        return "tab_separated"

    # Format simple: "abacus" (1 mot par ligne)
    simple = sum(1 for line in sample if line.strip() and "\t" not in line)
    if simple >= 3:
        return "simple"

    return "unknown"


def parse_tab_separated(line: str) -> str | None:
    """Parse format: '11111\tabacus' -> 'abacus'"""
    parts = line.strip().split("\t")
    if len(parts) >= 2:
        word = parts[1].strip()
        if word:
            return word
    return None


def parse_three_column(line: str) -> str | None:
    """Parse format: '11111\tabacus\t' -> 'abacus'"""
    parts = line.strip().split("\t")
    if len(parts) >= 2:
        word = parts[1].strip()
        if word:
            return word
    return None


def parse_simple(line: str) -> str | None:
    """Parse format: 'abacus' -> 'abacus'"""
    word = line.strip()
    if word:
        return word
    return None


PARSERS = {
    "tab_separated": parse_tab_separated,
    "three_column": parse_three_column,
    "simple": parse_simple,
}


def import_dictionary(source_path: Path, target_path: Path) -> int:
    """Importe un dictionnaire EFF vers un fichier standardisé."""
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source_path}")

    with source_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # Détection auto du format
    fmt = detect_format(lines)
    print(f"Format détecté: {fmt}")

    if fmt == "empty":
        raise ValueError("Fichier source vide")
    if fmt == "unknown":
        raise ValueError("Format non reconnu")

    parser = PARSERS[fmt]
    words = []
    seen = set()

    for line in lines:
        word = parser(line)
        if word and word not in seen:
            words.append(word)
            seen.add(word)

    # Écriture
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(words))

    print(f"{len(words)} mots importés vers {target_path}")
    return len(words)


def main():
    parser = argparse.ArgumentParser(
        description="Importe un dictionnaire EFF vers un format standardisé."
    )
    parser.add_argument(
        "--source",
        type=str,
        default="data/eff_large_wordlist.txt",
        help="Chemin du fichier source EFF",
    )
    parser.add_argument(
        "--target",
        type=str,
        default="data/dictionary.txt",
        help="Chemin du fichier de sortie",
    )
    args = parser.parse_args()

    source = Path(args.source)
    target = Path(args.target)

    import_dictionary(source, target)


if __name__ == "__main__":
    main()