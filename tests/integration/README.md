# Integration Tests

Ce répertoire contient les tests d'intégration qui vérifient les interactions entre l'API Flask et les services externes (Guardian, etc.).

## Structure

```
tests/integration/
├── conftest.py                        # Fixtures pour tests d'intégration
├── test_basic_integration.py          # Tests de base sans services externes
├── test_check_access_integration.py   # Tests avec Guardian service
└── README.md                          # Ce fichier
```

## Exécution des tests

### Avec le script (recommandé)

```bash
# Exécuter tous les tests d'intégration (sans Guardian)
./scripts/run-integration-tests.sh

# Afficher l'aide
./scripts/run-integration-tests.sh --help
```

### Directement avec pytest

```bash
# Exécuter tous les tests marqués comme "integration"
pytest -m integration -v

# Exécuter un fichier spécifique
pytest tests/integration/test_basic_integration.py -v
```

## Configuration

Le fichier `scripts/integration.conf` contrôle quels services sont démarrés :

```bash
# Activer/désactiver Guardian service
WITH_GUARDIAN=false

# Chemin vers le service Guardian (si disponible)
GUARDIAN_SERVICE_PATH=../guardian_service
```

## Types de tests

### Tests de base (`test_basic_integration.py`)

Tests qui ne nécessitent **aucun service externe** :
- Endpoints avec Guardian désactivé
- Health checks
- Validation de l'authentification

Ces tests s'exécutent toujours, même sans Docker.

### Tests avec Guardian (`test_check_access_integration.py`)

Tests qui nécessitent le **service Guardian** :
- Vérification d'accès avec Guardian réel
- Tests de timeout et erreurs réseau
- Intégration complète du décorateur `check_access_required`

Ces tests sont **automatiquement skippés** si :
- `USE_GUARDIAN_SERVICE=false`
- Guardian service n'est pas disponible

## Ajouter de nouveaux tests

### Test sans service externe

```python
import pytest

@pytest.mark.integration
class TestMyFeature:
    def test_something(self, client):
        response = client.get("/my-endpoint")
        assert response.status_code == 200
```

### Test avec Guardian

```python
import pytest
import os

@pytest.mark.integration
class TestMyFeatureWithGuardian:
    @pytest.fixture(autouse=True)
    def check_guardian(self):
        use_guardian = os.environ.get("USE_GUARDIAN_SERVICE", "false").lower() in ("true", "yes", "1")
        if not use_guardian:
            pytest.skip("Guardian service disabled")
    
    def test_with_guardian(self, client):
        # Ce test ne s'exécute que si Guardian est actif
        response = client.get("/protected-endpoint")
        assert response.status_code in [200, 403]
```

## Variables d'environnement

Les variables suivantes sont définies par le script :

- `USE_GUARDIAN_SERVICE`: `true` ou `false`
- `GUARDIAN_SERVICE_URL`: URL du service Guardian (si actif)
- `JWT_SECRET`: Clé secrète pour les tests
- `DATABASE_URL`: Base de données en mémoire
- `FLASK_ENV`: `testing`

## Docker Compose

Le fichier `docker-compose.test.yml` définit les services pour l'intégration :

```yaml
services:
  guardian-service:
    # Configuration du service Guardian
```

Pour démarrer manuellement les services :

```bash
docker compose -f docker-compose.test.yml --profile guardian up -d
```

Pour les arrêter :

```bash
docker compose -f docker-compose.test.yml --profile guardian down -v
```
