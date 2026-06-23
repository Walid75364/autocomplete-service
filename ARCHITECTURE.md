## Scénario 1 : Ajouter un front-end

**Techno :** React + TypeScript avec Vite

**Pourquoi :**
- Écosystème mature, grande communauté
- Composants réutilisables pour la liste de suggestions
- Typage fort réduit les bugs

**À quoi penser :**
- **Debounce** : attendre 300ms après la dernière frappe avant d'envoyer la requête
- **Navigation clavier** : flèches haut/bas, Entrée pour sélectionner, Échap pour fermer
- **Cache client** : ne pas requêter plusieurs fois le même préfixe
- **CORS** : configurer FastAPI (`allow_origins=["http://localhost:5173"]`)
- **Loading states** : spinner pendant la recherche
- **Accessibilité** : ARIA labels, focus management
- **Mobile-first** : gérer le clavier virtuel

## Scénario 2 : Sauvegarder les recherches

**Techno :**
- **Court terme** : fichier de logs structurés (JSON Lines) + parsing périodique
- **Long terme** : PostgreSQL + TimescaleDB (extension time-series)

**Pourquoi :**
- Les recherches sont des **événements temporels** → time-series adapté
- PostgreSQL robuste, bien connu de l'équipe
- TimescaleDB optimise les agrégations (`COUNT`, `GROUP BY` sur le temps)

**À quoi penser / faire attention :**

| Risque | Mitigation |
|--------|-----------|
| **RGPD** | Anonymiser les IPs, hash des queries sensibles, droit à l'oubli |
| **Volume** | Batch d'insertions (pas d'écriture synchrone par requête API) |
| **Performance** | File d'attente async (Redis/RabbitMQ) entre API et worker |
| **Rétention** | Policy de suppression automatique après X mois |
| **Pii** | Audit des accès, chiffrement au repos |

**Architecture proposée :**
[Client] → [API FastAPI] → [Réponse rapide]
↓
[File d'attente Redis] → [Worker Celery] → [PostgreSQL/TimescaleDB]


## Scénario 3 : Bug "coucou (sourire)" → Erreur 500

**Diagnostic :**

1. **Reproduire** : `curl "http://localhost:8000/autocomplete?query=coucou%20%F0%9F%98%8A"`
2. **Analyser les logs** : traceback exact de l'erreur 500

**Hypothèses probables :**
- **Encodage UTF-8** : l'emoji 😊 (U+1F60A, 4 bytes) mal géré par un `split()` ou `strip()`
- **Normalisation Unicode** : "é" précomposé (U+00E9) vs décomposé (U+0065 U+0301)

**Code de défense déjà en place :**
- `encoding="utf-8"` partout dans le loader
- Tests `test_emoji_does_not_crash` et `test_unicode_characters_do_not_crash`

**Amélioration possible :**
```python
import unicodedata

def normalize_query(query: str) -> str:
    return unicodedata.normalize("NFC", query.strip())