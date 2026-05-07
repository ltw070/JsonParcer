# JSON Parser Library — POC Spec

## 개요

JSON 데이터를 파싱하고 JSON 파일을 읽고 저장하는 Python 라이브러리의 POC(Proof of Concept).
표준 라이브러리(`json`) 위에 실용적인 편의 기능을 추가하여 반복 코드를 줄이는 것을 목표로 한다.

---

## 목표

- JSON 문자열 및 파일을 Python 객체로 파싱
- Python 객체를 JSON 파일로 저장
- 스키마 기반 유효성 검사 (선택적)
- 오류 상황에 대한 명확한 예외 처리

---

## 범위 (POC)

| 항목 | 포함 여부 |
|------|-----------|
| JSON 문자열 파싱 | ✅ |
| JSON 파일 읽기 | ✅ |
| JSON 파일 저장 | ✅ |
| 스키마 유효성 검사 | ✅ (기본) |
| 스트리밍 파싱 (대용량) | ❌ (범위 외) |
| 비동기 I/O | ❌ (범위 외) |

---

## API 설계

### 1. 파싱 — 문자열 → Python 객체

```python
def parse(json_str: str) -> dict | list:
    ...
```

- `json_str`: 파싱할 JSON 형식의 문자열
- 반환값: `dict` 또는 `list`
- 예외: `JsonParseError` — 형식이 올바르지 않을 때

**예시**
```python
data = parse('{"name": "Alice", "age": 30}')
# {"name": "Alice", "age": 30}
```

---

### 2. 파일 읽기 — 파일 → Python 객체

```python
def load(file_path: str, encoding: str = "utf-8") -> dict | list:
    ...
```

- `file_path`: 읽을 JSON 파일 경로
- `encoding`: 파일 인코딩 (기본값 `utf-8`)
- 예외:
  - `FileNotFoundError` — 파일이 없을 때
  - `JsonParseError` — 파일 내용이 올바른 JSON이 아닐 때

**예시**
```python
data = load("config.json")
```

---

### 3. 파일 저장 — Python 객체 → 파일

```python
def save(
    data: dict | list,
    file_path: str,
    encoding: str = "utf-8",
    indent: int = 2,
    ensure_ascii: bool = False,
    overwrite: bool = True,
) -> None:
    ...
```

- `data`: 저장할 Python 객체
- `file_path`: 저장할 파일 경로 (중간 디렉토리 없으면 자동 생성)
- `indent`: 들여쓰기 칸 수 (기본값 2)
- `ensure_ascii`: ASCII 외 문자 이스케이프 여부 (기본값 `False` → 한글 그대로 저장)
- `overwrite`: `False`이면 파일이 이미 존재할 때 예외 발생
- 예외:
  - `FileExistsError` — `overwrite=False`이고 파일이 존재할 때
  - `JsonSerializeError` — 직렬화 불가 객체가 포함될 때

**예시**
```python
save({"name": "Alice"}, "output/result.json")
save(data, "output/result.json", overwrite=False)  # 덮어쓰기 방지
```

---

### 4. 스키마 유효성 검사 (선택적)

```python
def validate(data: dict | list, schema: dict) -> None:
    ...
```

- `data`: 검사할 Python 객체
- `schema`: 기대하는 키와 타입을 정의한 딕셔너리
- 예외: `JsonValidationError` — 스키마 불일치 시

**스키마 형식 예시**
```python
schema = {
    "name": str,
    "age": int,
    "scores": list,
}
validate(data, schema)
```

---

## 예외 계층

```
JsonLibraryError          # 최상위 기본 예외
├── JsonParseError        # 파싱 실패
├── JsonSerializeError    # 직렬화 실패
└── JsonValidationError   # 스키마 검증 실패
```

---

## 모듈 구조

```
JsonParcer/
├── json_lib/
│   ├── __init__.py       # parse, load, save, validate 노출
│   ├── parser.py         # parse, load 구현
│   ├── writer.py         # save 구현
│   ├── validator.py      # validate 구현
│   └── exceptions.py     # 예외 클래스 정의
├── tests/
│   ├── test_parser.py
│   ├── test_writer.py
│   └── test_validator.py
├── Spec.md
└── README.md
```

---

## 사용 시나리오 (E2E 예시)

```python
from json_lib import load, save, validate, parse

# 1. 문자열 파싱
raw = '{"user": "Bob", "score": 95}'
data = parse(raw)

# 2. 스키마 검증
schema = {"user": str, "score": int}
validate(data, schema)

# 3. 파일 저장
save(data, "output/result.json")

# 4. 파일 다시 읽기
loaded = load("output/result.json")
print(loaded["user"])  # Bob
```

---

## 성공 기준 (POC 완료 조건)

- [ ] `parse()` — 유효한 JSON 문자열을 Python 객체로 변환한다
- [ ] `parse()` — 잘못된 형식에 `JsonParseError`를 발생시킨다
- [ ] `load()` — JSON 파일을 읽어 Python 객체를 반환한다
- [ ] `load()` — 존재하지 않는 파일에 `FileNotFoundError`를 발생시킨다
- [ ] `save()` — Python 객체를 지정 경로에 JSON 파일로 저장한다
- [ ] `save()` — 중간 디렉토리가 없으면 자동으로 생성한다
- [ ] `save()` — `overwrite=False` 시 기존 파일을 보호한다
- [ ] `validate()` — 스키마 불일치 시 `JsonValidationError`를 발생시킨다
- [ ] 단위 테스트가 모든 성공/실패 경로를 커버한다

---

## 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Python 3.11+ |
| 의존성 | 표준 라이브러리만 (`json`, `pathlib`, `os`) |
| 테스트 | `pytest` |
| 린터 | `ruff` (선택) |
