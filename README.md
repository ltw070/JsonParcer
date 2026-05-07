# json_lib

JSON 문자열·파일을 파싱하고, Python 객체를 JSON 파일로 저장하는 경량 라이브러리입니다.
표준 라이브러리(`json`, `pathlib`)만 사용하며 외부 의존성이 없습니다.

---

## 요구 사항

- Python 3.11 이상

---

## 설치

별도 패키지 설치 없이 `json_lib/` 디렉토리를 프로젝트 루트에 두면 바로 사용할 수 있습니다.

```
your_project/
├── json_lib/   ← 이 디렉토리를 복사
└── your_code.py
```

---

## 빠른 시작

```python
from json_lib import parse, load, save, validate

# 1. 문자열 파싱
data = parse('{"user": "Bob", "score": 95}')

# 2. 스키마 검증
validate(data, {"user": str, "score": int})

# 3. 파일 저장
save(data, "output/result.json")

# 4. 파일 읽기
loaded = load("output/result.json")
print(loaded["user"])  # Bob
```

---

## API

### `parse(json_str)`

JSON 형식의 문자열을 Python 객체(`dict` 또는 `list`)로 변환합니다.

```python
from json_lib import parse

# dict 파싱
data = parse('{"name": "Alice", "age": 30}')
print(data["name"])  # Alice

# list 파싱
scores = parse('[10, 20, 30]')
print(scores[0])     # 10
```

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `json_str` | `str` | 파싱할 JSON 문자열 |

| 예외 | 발생 조건 |
|------|-----------|
| `JsonParseError` | 올바른 JSON 형식이 아닐 때 |
| `JsonParseError` | `str`이 아닌 타입을 전달했을 때 |

---

### `load(file_path, encoding="utf-8")`

JSON 파일을 읽어 Python 객체(`dict` 또는 `list`)로 반환합니다.

```python
from json_lib import load

data = load("config.json")
print(data["host"])  # localhost

# 인코딩 지정
data = load("data.json", encoding="utf-8")
```

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `file_path` | `str` | — | 읽을 파일 경로 |
| `encoding` | `str` | `"utf-8"` | 파일 인코딩 |

| 예외 | 발생 조건 |
|------|-----------|
| `FileNotFoundError` | 파일이 존재하지 않을 때 |
| `JsonParseError` | 파일 내용이 올바른 JSON이 아닐 때 |

---

### `save(data, file_path, ...)`

Python 객체를 JSON 파일로 저장합니다. 중간 디렉토리가 없으면 자동으로 생성합니다.

```python
from json_lib import save

# 기본 저장
save({"name": "Alice"}, "output/result.json")

# 덮어쓰기 방지
save(data, "output/result.json", overwrite=False)

# 들여쓰기 4칸
save(data, "output/result.json", indent=4)

# 한글 저장 (이스케이프 없이)
save({"이름": "홍길동"}, "output/korean.json")
# → 파일에 "홍길동" 그대로 저장됨
```

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `data` | `dict \| list` | — | 저장할 Python 객체 |
| `file_path` | `str` | — | 저장할 파일 경로 |
| `encoding` | `str` | `"utf-8"` | 파일 인코딩 |
| `indent` | `int` | `2` | 들여쓰기 칸 수 |
| `ensure_ascii` | `bool` | `False` | `True`이면 ASCII 외 문자를 `\uXXXX`로 이스케이프 |
| `overwrite` | `bool` | `True` | `False`이면 기존 파일이 있을 때 예외 발생 |

| 예외 | 발생 조건 |
|------|-----------|
| `FileExistsError` | `overwrite=False`이고 파일이 이미 존재할 때 |
| `JsonSerializeError` | `datetime`, 사용자 정의 객체 등 직렬화 불가 타입이 포함될 때 |

---

### `validate(data, schema)`

`data`의 키 존재 여부와 값의 타입을 `schema`와 비교해 검증합니다.
검증에 통과하면 아무것도 반환하지 않습니다.

```python
from json_lib import validate
from json_lib.exceptions import JsonValidationError

data = {"name": "Alice", "age": 30, "scores": [90, 95]}

schema = {
    "name": str,
    "age": int,
    "scores": list,
}

validate(data, schema)  # 통과

# 타입 불일치 예시
bad_data = {"name": "Alice", "age": "thirty"}
try:
    validate(bad_data, schema)
except JsonValidationError as e:
    print(e)
# 키 'age' 의 값이 <class 'int'> 이어야 하지만 <class 'str'> 입니다.

# 키 누락 예시
missing_data = {"name": "Alice"}
try:
    validate(missing_data, schema)
except JsonValidationError as e:
    print(e)
# 필수 키 'age' 이 데이터에 없습니다.
```

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `data` | `dict` | 검증할 Python 딕셔너리 |
| `schema` | `dict` | `{키: 타입}` 형태의 스키마 |

| 예외 | 발생 조건 |
|------|-----------|
| `JsonValidationError` | 필수 키가 없거나 값의 타입이 다를 때 |

---

## 예외 계층

모든 예외는 `JsonLibraryError`를 상속하므로 한 번에 잡을 수 있습니다.

```
JsonLibraryError
├── JsonParseError        # parse(), load() 실패
├── JsonSerializeError    # save() 직렬화 실패
└── JsonValidationError   # validate() 검증 실패
```

```python
from json_lib.exceptions import JsonLibraryError

try:
    data = parse("not json")
except JsonLibraryError as e:
    print(f"json_lib 오류: {e}")
```

---

## 프로젝트 구조

```
json_lib/
├── __init__.py     # parse, load, save, validate 공개
├── exceptions.py   # 예외 클래스
├── parser.py       # parse(), load()
├── writer.py       # save()
└── validator.py    # validate()
tests/
├── test_parser.py
├── test_writer.py
└── test_validator.py
```

---

## 테스트 실행

```bash
pip install pytest
pytest tests/ -v
```

```
tests/test_parser.py::test_parse_dict              PASSED
tests/test_parser.py::test_parse_list              PASSED
tests/test_parser.py::test_parse_invalid_json      PASSED
tests/test_parser.py::test_parse_non_string        PASSED
tests/test_parser.py::test_load_file               PASSED
tests/test_parser.py::test_load_file_not_found     PASSED
tests/test_parser.py::test_load_invalid_content    PASSED
tests/test_validator.py::test_validate_success          PASSED
tests/test_validator.py::test_validate_missing_key      PASSED
tests/test_validator.py::test_validate_wrong_type       PASSED
tests/test_validator.py::test_validate_error_message_key  PASSED
tests/test_validator.py::test_validate_error_message_type PASSED
tests/test_writer.py::test_save_creates_file            PASSED
tests/test_writer.py::test_save_creates_directories     PASSED
tests/test_writer.py::test_save_content_correct         PASSED
tests/test_writer.py::test_save_overwrite_false         PASSED
tests/test_writer.py::test_save_overwrite_true          PASSED
tests/test_writer.py::test_save_non_serializable        PASSED
tests/test_writer.py::test_save_korean                  PASSED

19 passed
```
