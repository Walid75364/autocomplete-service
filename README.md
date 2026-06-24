# Système d'Auto-complétion

Service web d'auto-complétion type Google Suggest, implémenté en Python avec FastAPI et une structure de données Trie.

## Fonctionnalités

<img width="1329" height="238" alt="image" src="https://github.com/user-attachments/assets/c9a99d4c-7abf-4096-b8d1-a10a8ddbd778" />


- API REST `GET /autocomplete?query=&lt;prefix&gt;`
- Retourne une liste JSON de max 4 mots triés alphabétiquement
- Insensible à la casse
- Supporte n'importe quel dictionnaire EFF (détection auto du format)

## Architecture

<img width="590" height="365" alt="image" src="https://github.com/user-attachments/assets/20bbe060-6980-430c-aa33-b9772a5fa275" />


## Choix de conception

### Structure de données : Trie

Le Trie (arbre de préfixes) est optimal pour l'auto-complétion :

| Critère               | Trie            | Liste triée  | Hash Map              |
| --------------------- | --------------- | ------------ | --------------------- |
| Recherche par préfixe | **O(m)**        | O(log n + k) | impossible nativement |
| Insertion             | O(n)            | O(n)         | O(1)                  |
| Espace                | O(n × alphabet) | O(n)         | O(n)                  |
| Partage de préfixes   | ✅ Oui          | ❌ Non      | ❌ Non                |

*m = longueur du préfixe, n = nombre de mots, k = résultats*

**Pourquoi pas une liste triée ?** Recherche binaire rapide mais scan linéaire des résultats coûteux.
**Pourquoi pas un Hash Map ?** Pas de recherche par préfixe native.

### Détection auto du format EFF

Le script `import_eff.py` détecte automatiquement 3 formats :
- `tab_separated` : `"11111\tabacus"` (eff_large_wordlist)
- `three_column` : `"11111\tabacus\t"` (harrypotter)
- `simple` : `"abacus"` (gameofthrones, starwars, memory-alpha)

## Installation

```bash
# 1. Cloner le projet
git clone <repo>
cd autocomplete-service

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Télécharger un dictionnaire EFF
# Exemple : https://eff.org/files/2016/07/18/eff_large_wordlist.txt
# Sauvegarder dans data/eff_large_wordlist.txt

# 4. Importer le dictionnaire
python scripts/import_eff.py --source data/eff_large_wordlist.txt --target data/dictionary.txt

# 5. Lancer le serveur
uvicorn app.main:app --reload

# 6. Tester
curl "http://localhost:8000/autocomplete?query=crypt"

Tests
pytest tests/ -v
Résultat attendu : 20 tests passed, 0 failed.

Docker
voir fichier Dockerfile
docker build -t autocomplete .
docker run -p 8000:8000 autocomplete

Extensions d'architecture, voir fichier ARCHITECTURE.md

Tests de non-régression :
def test_unicode_normalization():
    # "é" précomposé == "é" décomposé
    result1 = service.autocomplete("café")  # U+00E9
    result2 = service.autocomplete("café")    # U+0065 U+0301
    assert result1 == result2

---
# 7. Test final complet
    # 1. Vérifier que tout est là
        ls -la

    # 2. Relancer les tests
        pytest tests/ -v

    # 3. Tester l'API
        uvicorn app.main:app --reload
        # Dans un autre terminal :
        curl "http://localhost:8000/autocomplete?query=crypt"

    # 4. Tester Docker (si installé)
        docker build -t autocomplete .
        docker run -p 8000:8000 autocomplete
