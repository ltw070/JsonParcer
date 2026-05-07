# JSON Parser Library — 구현 Plan (TDD)

## 구현 순서 원칙

**TDD Red → Green → Refactor** 사이클을 모듈 단위로 반복한다.

1. **Red** — 실패하는 테스트를 먼저 작성하고 실행해서 실패를 확인한다.
2. **Green** — 테스트를 통과시키는 최소한의 구현을 작성한다.
3. **Refactor** — 동작을 유지하면서 코드를 정리한다.

> 예외(`exceptions.py`)는 테스트 코드에서 `import`로 참조하므로 사이클 시작 전에 클래스 정의만 먼저 작성한다. 로직이 없으므로 TDD 원칙과 충돌하지 않는다.

---

## Step 1. 프로젝트 골격 생성

**목표**: 디렉토리와 빈 파일을 만들어 import 경로를 확정한다.

```
JsonParcer/
├── json_lib/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── parser.py
│   ├── writer.py
│   └── validator.py
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_writer.py
│   └── test_validator.py
└── plan.md
```

**작업**
- `json_lib/`, `tests/` 디렉토리 생성
- 각 `.py` 파일을 빈 상태(`pass`)로 생성
- `pytest` 설치 확인 (`.venv` 활성화 후 `pip install pytest`)

**완료 기준**: `python -m pytest tests/` 가 "no tests found"로 통과한다.

---

## Step 2. 예외 클래스 정의 (`exceptions.py`)

**목표**: 테스트에서 `import` 할 수 있도록 예외 클래스 뼈대만 작성한다.
로직이 없으므로 테스트 대상이 아니다 — 사이클을 거치지 않는다.

```python
# exceptions.py

class JsonLibraryError(Exception):
    """최상위 기본 예외"""

class JsonParseError(JsonLibraryError):
    """JSON 파싱 실패"""

class JsonSerializeError(JsonLibraryError):
    """JSON 직렬화 실패"""

class JsonValidationError(JsonLibraryError):
    """스키마 검증 실패"""
```

**완료 기준**: `from json_lib.exceptions import JsonParseError` 가 오류 없이 동작한다.

---

## Step 3. Parser — Red → Green → Refactor

### 3-1. Red: `test_parser.py` 작성

구현 없이 테스트만 먼저 작성한다. `pytest tests/test_parser.py` 실행 시 전부 실패해야 한다.

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_parse_dict` | 정상 dict JSON 문자열 → `dict` 반환 |
| `test_parse_list` | 정상 list JSON 문자열 → `list` 반환 |
| `test_parse_invalid_json` | 잘못된 형식 → `JsonParseError` 발생 |
| `test_parse_non_string` | `str`이 아닌 입력 → `JsonParseError` 발생 |
| `test_load_file` | 정상 파일 경로 → `dict` 반환 |
| `test_load_file_not_found` | 없는 파일 경로 → `FileNotFoundError` 발생 |
| `test_load_invalid_content` | 내용이 깨진 파일 → `JsonParseError` 발생 |

**완료 기준**: `pytest tests/test_parser.py` → 7개 전부 **FAILED**.

### 3-2. Green: `parser.py` 구현

테스트를 통과시키는 최소 구현을 작성한다.

| 케이스 | 처리 방식 |
|--------|-----------|
| 정상 JSON 문자열 | `json.loads()` 호출 후 반환 |
| `json.JSONDecodeError` | `JsonParseError`로 감싸 재발생 |
| `str`이 아닌 타입 | `JsonParseError` 발생 |
| 정상 파일 | `Path.read_text()` → `parse()` 위임 |
| 파일 없음 | `FileNotFoundError` 그대로 전파 |

**완료 기준**: `pytest tests/test_parser.py` → 7개 전부 **PASSED**.

### 3-3. Refactor

- `load()`가 파일 읽기만 담당하고 파싱을 `parse()`에 완전히 위임하는지 확인
- 예외 메시지에 원본 오류 정보가 포함되는지 확인
- 테스트 재실행해서 Green 유지 확인

---

## Step 4. Writer — Red → Green → Refactor

### 4-1. Red: `test_writer.py` 작성

`pytest tests/test_writer.py` 실행 시 전부 실패해야 한다.

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_save_creates_file` | 지정 경로에 파일이 생성되는지 확인 |
| `test_save_creates_directories` | 중간 디렉토리가 없어도 자동 생성 |
| `test_save_content_correct` | 저장된 파일을 다시 읽어 내용 동일성 검증 |
| `test_save_overwrite_false` | 기존 파일 존재 + `overwrite=False` → `FileExistsError` |
| `test_save_overwrite_true` | 기존 파일 존재 + `overwrite=True` → 정상 덮어쓰기 |
| `test_save_non_serializable` | 직렬화 불가 객체 → `JsonSerializeError` |
| `test_save_korean` | 한글 값이 이스케이프 없이 저장되는지 확인 |

> 테스트에서 임시 파일/디렉토리는 `pytest`의 `tmp_path` fixture를 활용한다.

**완료 기준**: `pytest tests/test_writer.py` → 7개 전부 **FAILED**.

### 4-2. Green: `writer.py` 구현

| 케이스 | 처리 방식 |
|--------|-----------|
| 정상 저장 | `Path.parent.mkdir(parents=True, exist_ok=True)` 후 파일 쓰기 |
| `overwrite=False` + 파일 존재 | `FileExistsError` 발생 |
| 직렬화 불가 객체 | `json.dumps()`의 `TypeError` → `JsonSerializeError` |

**구현 포인트**
- `overwrite` 체크는 디렉토리 생성 **전**에 수행한다.
- `ensure_ascii=False`가 기본값이므로 한글이 이스케이프 없이 저장된다.

**완료 기준**: `pytest tests/test_writer.py` → 7개 전부 **PASSED**.

### 4-3. Refactor

- `overwrite` 체크 위치가 디렉토리 생성보다 앞인지 확인
- 테스트 재실행해서 Green 유지 확인

---

## Step 5. Validator — Red → Green → Refactor

### 5-1. Red: `test_validator.py` 작성

`pytest tests/test_validator.py` 실행 시 전부 실패해야 한다.

| 테스트 이름 | 검증 내용 |
|-------------|-----------|
| `test_validate_success` | 스키마 일치 → 예외 없이 통과 |
| `test_validate_missing_key` | 필수 키 누락 → `JsonValidationError` 발생 |
| `test_validate_wrong_type` | 타입 불일치 → `JsonValidationError` 발생 |
| `test_validate_error_message_key` | 오류 메시지에 누락된 키 이름 포함 |
| `test_validate_error_message_type` | 오류 메시지에 기대 타입/실제 타입 포함 |

**완료 기준**: `pytest tests/test_validator.py` → 5개 전부 **FAILED**.

### 5-2. Green: `validator.py` 구현

**검사 규칙**

- `schema`에 정의된 키가 `data`에 존재하는지 확인
- 각 키의 값 타입이 `schema`에서 지정한 타입과 일치하는지 확인

**오류 메시지 형식**
```
필수 키 'name' 이 데이터에 없습니다.
키 'age' 의 값이 <class 'str'> 이어야 하지만 <class 'int'> 입니다.
```

**완료 기준**: `pytest tests/test_validator.py` → 5개 전부 **PASSED**.

### 5-3. Refactor

- 오류 메시지에 키 이름과 타입 정보가 명확히 포함되는지 확인
- 테스트 재실행해서 Green 유지 확인

---

## Step 6. 패키지 진입점 구성 (`__init__.py`)

**목표**: 외부에서 `from json_lib import parse, load, save, validate`로 임포트 가능하게 한다.

```python
# __init__.py
from .parser import parse, load
from .writer import save
from .validator import validate

__all__ = ["parse", "load", "save", "validate"]
```

**완료 기준**: 아래 E2E 시나리오가 오류 없이 실행된다.

```python
from json_lib import parse, load, save, validate

data = parse('{"user": "Bob", "score": 95}')
validate(data, {"user": str, "score": int})
save(data, "output/result.json")
loaded = load("output/result.json")
assert loaded["user"] == "Bob"
```

---

## Step 7. 전체 테스트 실행 및 POC 완료 확인

```bash
pytest tests/ -v
```

Spec.md의 성공 기준 체크리스트를 순서대로 검토한다.

```
- [ ] parse() — 유효한 JSON 문자열을 Python 객체로 변환한다
- [ ] parse() — 잘못된 형식에 JsonParseError를 발생시킨다
- [ ] load() — JSON 파일을 읽어 Python 객체를 반환한다
- [ ] load() — 존재하지 않는 파일에 FileNotFoundError를 발생시킨다
- [ ] save() — Python 객체를 지정 경로에 JSON 파일로 저장한다
- [ ] save() — 중간 디렉토리가 없으면 자동으로 생성한다
- [ ] save() — overwrite=False 시 기존 파일을 보호한다
- [ ] validate() — 스키마 불일치 시 JsonValidationError를 발생시킨다
- [ ] 단위 테스트가 모든 성공/실패 경로를 커버한다
```

---

## 구현 순서 요약

```
Step 1  프로젝트 골격 생성
  ↓
Step 2  exceptions.py 뼈대 (테스트 import 전제 조건)
  ↓
Step 3  [Red] test_parser.py 작성 → 실패 확인
        [Green] parser.py 구현 → 통과 확인
        [Refactor] 정리
  ↓
Step 4  [Red] test_writer.py 작성 → 실패 확인
        [Green] writer.py 구현 → 통과 확인
        [Refactor] 정리
  ↓
Step 5  [Red] test_validator.py 작성 → 실패 확인
        [Green] validator.py 구현 → 통과 확인
        [Refactor] 정리
  ↓
Step 6  __init__.py 구성 + E2E 검증
  ↓
Step 7  pytest tests/ -v 전체 통과 확인
```

---

## 예상 소요 시간

| Step | 작업 | 예상 시간 |
|------|------|-----------|
| 1 | 골격 생성 | 5분 |
| 2 | exceptions.py | 5분 |
| 3 | Parser Red→Green→Refactor | 25분 |
| 4 | Writer Red→Green→Refactor | 25분 |
| 5 | Validator Red→Green→Refactor | 25분 |
| 6 | __init__.py + E2E | 10분 |
| 7 | 전체 테스트 확인 | 10분 |
| **합계** | | **~105분** |
