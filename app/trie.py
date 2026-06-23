class TrieNode:
    """Nœud du Trie (arbre de préfixes).

    Chaque nœud représente un caractère et pointe vers ses enfants.
    Un nœud marqué `is_end_of_word = True` signifie qu'un mot complet
    se termine à cette position.
    """
    def __init__(self):
        self.children = {}      # Mapping char -> TrieNode
        self.is_end_of_word = False
        self.word = None        # Mot complet (forme originale), stocké une seule fois


class Trie:
    """Structure de données Trie (arbre de préfixes) pour l'auto-complétion.

    Complexités:
    - Insertion: O(n) où n = longueur du mot
    - Recherche: O(m + k log k) où m = longueur du préfixe, k = nombre de résultats
    - Espace: O(n * alphabet) en pire cas, optimisé par partage des préfixes

    Pourquoi le Trie et pas une liste triée ou un hash map?
    - Liste triée: recherche O(log N + k) mais insertion O(N), pas de partage de préfixes
    - Hash map: recherche O(1) mais impossible de faire du préfixe natif
    - Trie: recherche O(m) indépendante de la taille du dictionnaire, partage naturel des préfixes
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """Insère un mot dans le Trie.

        La casse est normalisée en minuscules pour la navigation,
        mais le mot original est conservé pour l'affichage.
        """
        if not word:
            return

        word = word.strip()
        if not word:
            return

        node = self.root
        normalized = word.lower()

        for char in normalized:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        # Marque la fin du mot et stocke la forme originale
        node.is_end_of_word = True
        node.word = word

    def search(self, prefix: str) -> list[str]:
        """Retourne tous les mots commençant par le préfixe, triés alphabétiquement.

        Args:
            prefix: Suite de caractères à rechercher (insensible à la casse)

        Returns:
            Liste des mots complets triés alphabétiquement
        """
        if not prefix:
            return []

        prefix = prefix.strip().lower()
        if not prefix:
            return []

        # Navigation jusqu'au nœud correspondant au dernier caractère du préfixe
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []  # Préfixe inexistant
            node = node.children[char]

        # Collecte récursive de tous les mots dans le sous-arbre
        results = []
        self._collect_words(node, results)

        # Tri alphabétique insensible à la casse
        results.sort(key=str.lower)
        return results

    def _collect_words(self, node: TrieNode, results: list[str]) -> None:
        """Parcours en profondeur (DFS) pour collecter tous les mots d'un sous-arbre.

        Le parcours suit l'ordre alphabétique des caractères pour garantir
        un pré-tri qui minimise le travail de `sort()` final.
        """
        if node.is_end_of_word:
            results.append(node.word)

        # Parcours ordonné pour un pré-tri naturel
        for char in sorted(node.children.keys()):
            self._collect_words(node.children[char], results)