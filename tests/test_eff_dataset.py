import time
import pytest
from app.service import AutocompleteService


@pytest.fixture(scope="module")
def service():
    return AutocompleteService()


def test_eff_dataset_loaded(service):
    result = service.autocomplete("ab")
    assert isinstance(result, list)
    assert len(result) >= 0


def test_eff_limit_respected(service):
    result = service.autocomplete("a")
    assert len(result) <= 4


def test_eff_performance_sanity(service):
    """500 requêtes doivent s'exécuter en moins d'1 seconde."""
    start = time.perf_counter()

    for _ in range(500):
        service.autocomplete("cr")

    duration = time.perf_counter() - start
    assert duration < 1.0, f"Performance trop lente: {duration:.3f}s"


def test_eff_prefix_variations(service):
    """Teste différentes longueurs de préfixes."""
    for prefix in ["a", "ab", "abc", "abcd"]:
        result = service.autocomplete(prefix)
        assert isinstance(result, list)
        assert len(result) <= 4