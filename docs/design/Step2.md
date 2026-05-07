# Step 2 — repository.py (TDD)

## 목표

CRUD 비즈니스 로직 전체를 구현한다.
`json_lib`(`load`, `save`, `validate`)를 호출하고,
`models.py`(`create_record`)를 사용한다.
UI 레이어(`menu.py`)와 완전히 분리되어 단위 테스트가 가능해야 한다.

---

## 구현 대상

### `app/repository.py`

```python
DATA_FILE = "data/records.json"
SCHEMA = {"id": str, "name": str, "email": str, "phone": str, "created_at": str}

def get_all() -> list[dict]
def find_by_id(id_prefix: str) -> dict | None
def find_by_name(keyword: str) -> list[dict]
def create(name: str, email: str, phone: str) -> dict
def update(id_prefix: str, field: str, value: str) -> dict
def delete(id_prefix: str) -> dict
```

#### 함수별 책임

| 함수 | 책임 |
|------|------|
| `get_all()` | 파일 읽어 전체 목록 반환. 파일 없으면 `[]` 반환 |
| `find_by_id(id_prefix)` | `id.startswith(id_prefix)` 매칭. 없으면 `None` |
| `find_by_name(keyword)` | `keyword in name` 필터링. 없으면 `[]` |
| `create(name, email, phone)` | 레코드 생성 → validate → 파일에 추가 저장 |
| `update(id_prefix, field, value)` | 대상 조회 → 필드 수정 → validate → 저장 |
| `delete(id_prefix)` | 대상 조회 → 목록에서 제거 → 저장 |

#### 예외 정의 (`app/exceptions.py`)

```python
class AppError(Exception):
    """앱 레이어 최상위 예외"""

class RecordNotFoundError(AppError):
    """ID로 레코드를 찾지 못함"""

class InvalidFieldError(AppError):
    """수정 불가 필드 지정"""
```

---

## TDD 사이클

### Red — `tests/test_repository.py` 작성

구현 없이 테스트만 먼저 작성한다.
`pytest tests/test_repository.py` 실행 시 **전부 FAILED** 여야 한다.

> 파일 I/O가 있으므로 `pytest`의 `tmp_path` fixture로 격리한다.
> `monkeypatch`로 `DATA_FILE` 경로를 임시 디렉토리로 교체한다.

#### 테스트 케이스

**get_all**

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_get_all_empty_when_no_file` | 파일 없을 때 빈 리스트 반환 |
| `test_get_all_returns_all_records` | 저장된 레코드 수만큼 반환 |

**find_by_id**

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_find_by_id_found` | 앞자리 일치 시 레코드 반환 |
| `test_find_by_id_not_found` | 없는 ID → `None` 반환 |

**find_by_name**

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_find_by_name_found` | 이름 포함 검색 결과 반환 |
| `test_find_by_name_not_found` | 없는 이름 → `[]` 반환 |

**create**

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_create_adds_record` | 생성 후 `get_all()` 길이 1 증가 |
| `test_create_returns_new_record` | 반환값에 id, name, email, phone, created_at 포함 |
| `test_create_persists_to_file` | 파일을 직접 읽어도 레코드 존재 |

**update**

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_update_name` | name 필드 수정 후 `find_by_id`로 확인 |
| `test_update_email` | email 필드 수정 후 확인 |
| `test_update_phone` | phone 필드 수정 후 확인 |
| `test_update_not_found` | 없는 ID → `RecordNotFoundError` |
| `test_update_invalid_field` | id/created_at 수정 시도 → `InvalidFieldError` |

**delete**

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_delete_removes_record` | 삭제 후 `get_all()` 길이 1 감소 |
| `test_delete_returns_deleted_record` | 반환값이 삭제된 레코드 |
| `test_delete_not_found` | 없는 ID → `RecordNotFoundError` |

#### 테스트 픽스처 패턴

```python
import pytest
import repository_module as repo  # monkeypatch로 DATA_FILE 교체

@pytest.fixture
def data_file(tmp_path, monkeypatch):
    path = tmp_path / "records.json"
    monkeypatch.setattr("app.repository.DATA_FILE", str(path))
    return path

def test_get_all_empty_when_no_file(data_file):
    result = repo.get_all()
    assert result == []

def test_create_adds_record(data_file):
    before = len(repo.get_all())
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert len(repo.get_all()) == before + 1
```

**완료 기준**: `pytest tests/test_repository.py` → 17개 전부 **FAILED**

---

### Green — `app/repository.py` 구현

```python
# app/repository.py
from pathlib import Path
from json_lib import load, save, validate
from app.models import create_record
from app.exceptions import RecordNotFoundError, InvalidFieldError

DATA_FILE = "data/records.json"
SCHEMA = {"id": str, "name": str, "email": str, "phone": str, "created_at": str}
UPDATABLE_FIELDS = {"name", "email", "phone"}


def get_all() -> list[dict]:
    if not Path(DATA_FILE).exists():
        return []
    return load(DATA_FILE)


def find_by_id(id_prefix: str) -> dict | None:
    return next(
        (r for r in get_all() if r["id"].startswith(id_prefix)), None
    )


def find_by_name(keyword: str) -> list[dict]:
    return [r for r in get_all() if keyword in r["name"]]


def create(name: str, email: str, phone: str) -> dict:
    record = create_record(name, email, phone)
    validate(record, SCHEMA)
    records = get_all()
    records.append(record)
    save(records, DATA_FILE)
    return record


def update(id_prefix: str, field: str, value: str) -> dict:
    if field not in UPDATABLE_FIELDS:
        raise InvalidFieldError(f"수정할 수 없는 필드입니다: {field}")
    records = get_all()
    for record in records:
        if record["id"].startswith(id_prefix):
            record[field] = value
            validate(record, SCHEMA)
            save(records, DATA_FILE)
            return record
    raise RecordNotFoundError(f"ID를 찾을 수 없습니다: {id_prefix}")


def delete(id_prefix: str) -> dict:
    records = get_all()
    for i, record in enumerate(records):
        if record["id"].startswith(id_prefix):
            removed = records.pop(i)
            save(records, DATA_FILE)
            return removed
    raise RecordNotFoundError(f"ID를 찾을 수 없습니다: {id_prefix}")
```

**완료 기준**: `pytest tests/test_repository.py` → 17개 전부 **PASSED**

---

### Refactor

- `find_by_id`가 `get_all()` 결과를 순회만 하는지 확인 (파일 중복 로드 없음)
- `update`와 `delete`에서 레코드 탐색 로직 중복 없는지 확인
- 재실행 후 Green 유지 확인

---

## 완료 체크리스트

- [ ] `app/exceptions.py` 작성 (`RecordNotFoundError`, `InvalidFieldError`)
- [ ] `tests/test_repository.py` 작성 → Red 확인
- [ ] `app/repository.py` 구현 → Green 확인
- [ ] Refactor → Green 유지 확인
- [ ] `pytest tests/test_repository.py -v` 17/17 통과
- [ ] `pytest tests/ -v` 전체(PoC 포함) 통과 확인
