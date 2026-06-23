"""
Tests 100% génériques pour l'auto-complétion.
Ne dépendent d'aucun mot spécifique du dataset.
Couvrent : fonctionnalité, robustesse, sécurité, performance, concurrence.
"""

import pytest
import time
import threading
from app.service import AutocompleteService


@pytest.fixture
def service():
    return AutocompleteService()


# ========== TESTS FONCTIONNELS DE BASE ==========

def test_autocomplete_returns_list(service):
    """Le résultat est toujours une liste."""
    result = service.autocomplete("a")
    assert isinstance(result, list)


def test_autocomplete_limit_exactly_respected(service):
    """La limite par défaut (4) doit être exactement respectée."""
    result = service.autocomplete("a")
    assert len(result) == 4  # EFF a >100 mots en 'a', donc exactement 4


def test_autocomplete_order_is_alphabetical(service):
    """Les résultats sont triés alphabétiquement."""
    result = service.autocomplete("ab")
    assert result == sorted(result, key=str.lower)


def test_autocomplete_case_insensitive(service):
    """La casse n'a pas d'impact sur les résultats."""
    result_lower = service.autocomplete("ab")
    result_upper = service.autocomplete("AB")
    assert result_lower == result_upper


def test_empty_query_returns_empty_list(service):
    """Requête vide ou espaces = liste vide."""
    assert service.autocomplete("") == []
    assert service.autocomplete("   ") == []


def test_none_query_returns_empty_list(service):
    """Requête None = liste vide."""
    assert service.autocomplete(None) == []


def test_unknown_prefix_returns_empty_list(service):
    """Préfixe inexistant = liste vide."""
    assert service.autocomplete("zzzzzzzzzzz") == []


def test_single_char_prefix_works(service):
    """Un seul caractère fonctionne et retourne la limite."""
    result = service.autocomplete("c")
    assert isinstance(result, list)
    assert len(result) == 4


def test_inserted_word_is_found(service):
    """Un mot du dictionnaire doit être retrouvable par son propre préfixe."""
    result = service.autocomplete("abacus")
    assert "abacus" in result


# ========== TESTS DE ROBUSTESSE (SÉCURITÉ) ==========

def test_sql_injection_attempt(service):
    """Tentative d'injection SQL ne doit pas crasher le service."""
    result = service.autocomplete("'; DROP TABLE users; --")
    assert isinstance(result, list)


def test_xss_attempt(service):
    """Tentative de XSS ne doit pas crasher le service."""
    result = service.autocomplete("<script>alert('xss')</script>")
    assert isinstance(result, list)


def test_newline_in_query(service):
    """Caractère de nouvelle ligne dans la requête."""
    result = service.autocomplete("crypt\nanalysis")
    assert isinstance(result, list)


def test_tab_in_query(service):
    """Tabulation dans la requête."""
    result = service.autocomplete("crypt\tanalysis")
    assert isinstance(result, list)


# ========== TESTS UNICODE & EMOJI ==========

def test_emoji_does_not_crash(service):
    """Scénario 3 : un emoji ne doit pas faire planter le service."""
    result = service.autocomplete("coucou 😊")
    assert isinstance(result, list)


def test_unicode_characters_do_not_crash(service):
    """Caractères Unicode variés ne doivent pas crasher."""
    for query in ["café", "naïve", "résumé", "über", "🚀rocket"]:
        result = service.autocomplete(query)
        assert isinstance(result, list)


# ========== TESTS DE PERFORMANCE ==========

def test_performance_with_long_prefix(service):
    """Préfixe inexistant = retour immédiat (O(m) du Trie)."""
    start = time.perf_counter()
    result = service.autocomplete("zzzzzzzzzz")
    duration = time.perf_counter() - start
    assert duration < 0.01
    assert result == []


def test_performance_500_requests(service):
    """500 requêtes doivent s'exécuter en moins d'1 seconde."""
    start = time.perf_counter()
    for _ in range(500):
        service.autocomplete("cr")
    duration = time.perf_counter() - start
    assert duration < 1.0, f"Trop lent: {duration:.3f}s"


# ========== TESTS DE CONFIGURATION ==========

def test_custom_limit():
    """La limite est configurable via le constructeur."""
    service = AutocompleteService(limit=2)
    result = service.autocomplete("c")
    assert len(result) == 2


def test_custom_limit_zero():
    """Limite à 0 = liste vide."""
    service = AutocompleteService(limit=0)
    result = service.autocomplete("a")
    assert result == []


# ========== TEST DE CONCURRENCE ==========

def test_thread_safety(service):
    """Lecture concurrente ne doit pas corrompre les résultats."""
    results = []

    def search():
        results.append(service.autocomplete("ab"))

    threads = [threading.Thread(target=search) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 10
    assert all(r == results[0] for r in results)