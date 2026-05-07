# JsonParcer

JSON 파싱·저장 라이브러리(`json_lib`) PoC와, 이를 기반으로 구축한 **연락처 CRUD 콘솔 애플리케이션**을 포함하는 프로젝트입니다.

---

## 프로젝트 구성

| 구성 | 디렉토리 | 설명 |
|------|----------|------|
| PoC 라이브러리 | `json_lib/` | JSON 파싱·저장 경량 라이브러리 |
| CRUD 앱 | `app/` | json_lib 기반 연락처 관리 콘솔 앱 |

---

## 요구 사항

- Python 3.11 이상
- 외부 의존성 없음 (표준 라이브러리만 사용)
- 테스트: `pytest`

---

## 빠른 시작

### CRUD 콘솔 앱 실행

```bash
python -m app.main
```

```
=============================
   연락처 관리 (JSON CRUD)
=============================
1. 전체 목록 보기
2. 검색
3. 새 연락처 추가
4. 연락처 수정
5. 연락처 삭제
0. 종료
────────────────────────────────────────────────────────
선택:
```

데이터는 `data/records.json`에 자동으로 저장됩니다. 파일이 없으면 첫 저장 시 자동 생성됩니다.

---

## CRUD 앱 기능

### 1. 전체 목록 보기

모든 연락처를 표 형태로 출력합니다.

```
번호  ID        이름      이메일                전화번호
────────────────────────────────────────────────────────
   1  a1b2c3d4  홍길동    hong@example.com      010-1234-5678
   2  e5f6g7h8  김철수    kim@example.com       010-9876-5432
총 2건
```

### 2. 검색

- **ID 검색**: ID 앞자리로 특정 연락처를 조회합니다.
- **이름 검색**: 이름에 검색어가 포함된 연락처를 필터링합니다.

### 3. 새 연락처 추가

이름, 이메일, 전화번호를 입력하면 UUID와 생성 시각이 자동으로 부여됩니다.

```
=== 새 연락처 추가 ===
이름     : 홍길동
이메일   : hong@example.com
전화번호 : 010-1234-5678
→ 저장되었습니다. (ID: a1b2c3d4-...)
```

### 4. 연락처 수정

ID 앞자리로 레코드를 선택한 뒤 이름·이메일·전화번호 중 하나를 수정합니다.

```
=== 연락처 수정 ===
수정할 ID 앞자리: a1b2c3d4
수정할 필드:  1) 이름   2) 이메일   3) 전화번호
선택: 2
새 이메일: newhong@example.com
→ 수정되었습니다.
```

### 5. 연락처 삭제

삭제 전 내용을 표시하고 확인(`y/n`)을 받습니다.

```
=== 연락처 삭제 ===
삭제할 ID 앞자리: a1b2c3d4
정말 삭제하시겠습니까? (y/n): y
→ 삭제되었습니다.
```

---

## 데이터 모델

연락처 레코드는 아래 구조로 `data/records.json`에 저장됩니다.

```json
{
  "id":         "a1b2c3d4-xxxx-4xxx-yxxx-xxxxxxxxxxxx",
  "name":       "홍길동",
  "email":      "hong@example.com",
  "phone":      "010-1234-5678",
  "created_at": "2026-05-07T12:00:00"
}
```

---

## 아키텍처

```
main.py            진입점, 메뉴 루프
  └── menu.py      콘솔 입출력, 예외 처리
        └── repository.py   CRUD 비즈니스 로직
              ├── models.py          레코드 생성 (uuid, timestamp 자동)
              └── json_lib/          PoC 라이브러리 (파일 I/O, 검증)
```

### 예외 계층

**앱 레이어**
```
AppError
├── RecordNotFoundError   # ID로 레코드를 찾지 못함
└── InvalidFieldError     # 수정 불가 필드 지정
```

**라이브러리 레이어**
```
JsonLibraryError
├── JsonParseError        # parse(), load() 실패
├── JsonSerializeError    # save() 직렬화 실패
└── JsonValidationError   # validate() 검증 실패
```

---

## json_lib API

PoC에서 검증한 라이브러리로, `app/` 코드에서 수정 없이 import하여 사용합니다.

### `parse(json_str)`

JSON 문자열 → Python 객체

```python
from json_lib import parse

data = parse('{"name": "Alice", "age": 30}')
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

JSON 파일 → Python 객체

```python
from json_lib import load

data = load("config.json")
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

Python 객체 → JSON 파일 (중간 디렉토리 자동 생성)

```python
from json_lib import save

save({"name": "Alice"}, "output/result.json")
save(data, "output/result.json", overwrite=False)  # 덮어쓰기 방지
save({"이름": "홍길동"}, "output/korean.json")      # 한글 그대로 저장
```

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `data` | `dict \| list` | — | 저장할 Python 객체 |
| `file_path` | `str` | — | 저장할 파일 경로 |
| `encoding` | `str` | `"utf-8"` | 파일 인코딩 |
| `indent` | `int` | `2` | 들여쓰기 칸 수 |
| `ensure_ascii` | `bool` | `False` | `True`이면 ASCII 외 문자를 `\uXXXX`로 이스케이프 |
| `overwrite` | `bool` | `True` | `False`이면 기존 파일이 있을 때 예외 발생 |

---

### `validate(data, schema)`

키 존재 여부 및 타입 검증

```python
from json_lib import validate

schema = {"name": str, "age": int}
validate({"name": "Alice", "age": 30}, schema)  # 통과
```

| 예외 | 발생 조건 |
|------|-----------|
| `JsonValidationError` | 필수 키가 없거나 값의 타입이 다를 때 |

---

## 프로젝트 구조

```
JsonParcer/
├── json_lib/              # PoC 라이브러리 (수정 금지)
│   ├── __init__.py
│   ├── exceptions.py
│   ├── parser.py
│   ├── writer.py
│   └── validator.py
├── app/                   # CRUD 콘솔 앱
│   ├── __init__.py
│   ├── main.py
│   ├── menu.py
│   ├── repository.py
│   ├── models.py
│   └── exceptions.py
├── data/
│   └── records.json       # 런타임 자동 생성
├── tests/
│   ├── test_models.py
│   ├── test_repository.py
│   ├── test_parser.py
│   ├── test_writer.py
│   └── test_validator.py
├── docs/
│   └── design/
│       ├── Step1.md
│       ├── Step2.md
│       ├── Step3.md
│       └── Step4.md
├── CLAUDE.md
├── AppDevPlan.md
├── Spec.md
├── plan.md
└── README.md
```

---

## 테스트 실행

```bash
pip install pytest
pytest tests/ -v
```

```
tests/test_models.py::test_create_record_returns_dict               PASSED
tests/test_models.py::test_create_record_has_all_fields             PASSED
tests/test_models.py::test_create_record_id_is_uuid_string          PASSED
tests/test_models.py::test_create_record_name_email_phone_match_input PASSED
tests/test_models.py::test_create_record_created_at_is_iso_string   PASSED
tests/test_models.py::test_create_record_ids_are_unique             PASSED
tests/test_parser.py::test_parse_dict                               PASSED
tests/test_parser.py::test_parse_list                               PASSED
tests/test_parser.py::test_parse_invalid_json                       PASSED
tests/test_parser.py::test_parse_non_string                         PASSED
tests/test_parser.py::test_load_file                                PASSED
tests/test_parser.py::test_load_file_not_found                      PASSED
tests/test_parser.py::test_load_invalid_content                     PASSED
tests/test_repository.py::test_get_all_empty_when_no_file           PASSED
tests/test_repository.py::test_get_all_returns_all_records          PASSED
tests/test_repository.py::test_find_by_id_found                     PASSED
tests/test_repository.py::test_find_by_id_not_found                 PASSED
tests/test_repository.py::test_find_by_name_found                   PASSED
tests/test_repository.py::test_find_by_name_not_found              PASSED
tests/test_repository.py::test_create_adds_record                   PASSED
tests/test_repository.py::test_create_returns_new_record            PASSED
tests/test_repository.py::test_create_persists_to_file              PASSED
tests/test_repository.py::test_update_name                          PASSED
tests/test_repository.py::test_update_email                         PASSED
tests/test_repository.py::test_update_phone                         PASSED
tests/test_repository.py::test_update_not_found                     PASSED
tests/test_repository.py::test_update_invalid_field                 PASSED
tests/test_repository.py::test_delete_removes_record                PASSED
tests/test_repository.py::test_delete_returns_deleted_record        PASSED
tests/test_repository.py::test_delete_not_found                     PASSED
tests/test_validator.py::test_validate_success                      PASSED
tests/test_validator.py::test_validate_missing_key                  PASSED
tests/test_validator.py::test_validate_wrong_type                   PASSED
tests/test_validator.py::test_validate_error_message_key            PASSED
tests/test_validator.py::test_validate_error_message_type           PASSED
tests/test_writer.py::test_save_creates_file                        PASSED
tests/test_writer.py::test_save_creates_directories                 PASSED
tests/test_writer.py::test_save_content_correct                     PASSED
tests/test_writer.py::test_save_overwrite_false                     PASSED
tests/test_writer.py::test_save_overwrite_true                      PASSED
tests/test_writer.py::test_save_non_serializable                    PASSED
tests/test_writer.py::test_save_korean                              PASSED

42 passed
```
