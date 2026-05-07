# Step 1 — models.py (TDD)

## 목표

레코드 딕셔너리를 생성하는 헬퍼 함수를 구현한다.
`id`(uuid4)와 `created_at`(현재 시각)을 자동으로 부여하여
`repository.py`가 직접 uuid/datetime을 다루지 않도록 분리한다.

---

## 구현 대상

### `app/models.py`

```python
def create_record(name: str, email: str, phone: str) -> dict:
    ...
```

| 반환 필드 | 값 | 출처 |
|-----------|-----|------|
| `id` | `str(uuid.uuid4())` | 자동 |
| `name` | 파라미터 그대로 | 사용자 입력 |
| `email` | 파라미터 그대로 | 사용자 입력 |
| `phone` | 파라미터 그대로 | 사용자 입력 |
| `created_at` | `datetime.now().isoformat(timespec="seconds")` | 자동 |

---

## TDD 사이클

### Red — `tests/test_models.py` 작성

구현 없이 테스트만 먼저 작성한다.
`pytest tests/test_models.py` 실행 시 **전부 FAILED** 여야 한다.

#### 테스트 케이스

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_create_record_returns_dict` | 반환값이 `dict` 타입 |
| `test_create_record_has_all_fields` | `id`, `name`, `email`, `phone`, `created_at` 5개 키 존재 |
| `test_create_record_id_is_uuid_string` | `id`가 36자 UUID 형식 문자열 (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`) |
| `test_create_record_name_email_phone_match_input` | 입력한 값이 그대로 저장됨 |
| `test_create_record_created_at_is_iso_string` | `created_at`이 ISO 8601 형식 문자열 |
| `test_create_record_ids_are_unique` | 두 번 호출 시 `id`가 서로 다름 |

#### 테스트 코드 예시

```python
import pytest
from app.models import create_record

def test_create_record_returns_dict():
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    assert isinstance(record, dict)

def test_create_record_has_all_fields():
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    assert set(record.keys()) == {"id", "name", "email", "phone", "created_at"}

def test_create_record_id_is_uuid_string():
    import re
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    assert re.match(uuid_pattern, record["id"])

def test_create_record_name_email_phone_match_input():
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    assert record["name"] == "홍길동"
    assert record["email"] == "hong@example.com"
    assert record["phone"] == "010-1234-5678"

def test_create_record_created_at_is_iso_string():
    from datetime import datetime
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    datetime.fromisoformat(record["created_at"])  # 파싱 성공하면 형식 올바름

def test_create_record_ids_are_unique():
    r1 = create_record("A", "a@a.com", "010-0000-0001")
    r2 = create_record("B", "b@b.com", "010-0000-0002")
    assert r1["id"] != r2["id"]
```

**완료 기준**: `pytest tests/test_models.py` → 6개 전부 **FAILED** (ImportError 포함)

---

### Green — `app/models.py` 구현

테스트를 통과시키는 최소 구현을 작성한다.

```python
# app/models.py
import uuid
from datetime import datetime


def create_record(name: str, email: str, phone: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "phone": phone,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
```

**완료 기준**: `pytest tests/test_models.py` → 6개 전부 **PASSED**

---

### Refactor

- `create_record`가 uuid/datetime 외 외부 상태에 의존하지 않는지 확인
- 재실행 후 Green 유지 확인

---

## 완료 체크리스트

- [ ] `tests/test_models.py` 작성 → Red 확인
- [ ] `app/__init__.py` 빈 파일 생성 (패키지 인식용)
- [ ] `app/models.py` 구현 → Green 확인
- [ ] Refactor → Green 유지 확인
- [ ] `pytest tests/test_models.py -v` 6/6 통과
