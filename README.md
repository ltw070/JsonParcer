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

## 앱 실행 방법

### 1단계 — 저장소 클론

```bash
git clone https://github.com/ltw070/JsonParcer.git
cd JsonParcer
```

### 2단계 — 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv .venv

# 활성화 (Windows)
.venv\Scripts\activate

# 활성화 (macOS / Linux)
source .venv/bin/activate
```

### 3단계 — 의존성 설치

테스트 실행이 필요한 경우에만 설치합니다. 앱 자체는 표준 라이브러리만 사용합니다.

```bash
pip install pytest
```

### 4단계 — 앱 실행

```bash
python -m app.main
```

실행하면 아래 메뉴가 나타납니다.

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

### 5단계 — 전체 테스트 실행 (선택)

```bash
pytest tests/ -v
```

> **참고** — 프로젝트 루트(`JsonParcer/`)에서 실행해야 `app`, `json_lib` 패키지를 올바르게 찾습니다.

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
│   ├── test_models.py        # Unit — models
│   ├── test_repository.py    # Unit — repository
│   ├── test_parser.py        # Unit — json_lib parser
│   ├── test_writer.py        # Unit — json_lib writer
│   ├── test_validator.py     # Unit — json_lib validator
│   ├── test_regression.py    # Regression — CRUD 정상 흐름
│   └── test_safety.py        # Safety — 비정상 입력·경계값
├── docs/
│   └── design/
│       ├── Step1.md
│       ├── Step2.md
│       ├── Step3.md
│       └── Step4.md
├── CLAUDE.md
├── AppDevPlan.md
├── Test.md                    # Regression / Safety 테스트 계획
├── Spec.md
├── plan.md
└── README.md
```

---

## 테스트

### 테스트 구성

| 파일 | 종류 | 수 | 내용 |
|------|------|----|------|
| `test_models.py` | Unit | 6 | 레코드 생성 헬퍼 |
| `test_repository.py` | Unit | 17 | CRUD 비즈니스 로직 |
| `test_parser.py` | Unit | 7 | JSON 파싱 |
| `test_writer.py` | Unit | 7 | JSON 저장 |
| `test_validator.py` | Unit | 5 | 스키마 검증 |
| `test_regression.py` | Regression | 25 | CRUD 정상 흐름 전체 |
| `test_safety.py` | Safety | 23 | 비정상 입력·경계값·파일 손상 |
| **합계** | | **90** | |

### 실행

```bash
# 전체
pytest tests/ -v

# Regression / Safety만
pytest tests/test_regression.py tests/test_safety.py -v
```

---

## Regression & Safety Test

> 상세 계획: [`Test.md`](Test.md)

### 목적

| 구분 | 목적 |
|------|------|
| **Regression** | 기능 변경 후에도 기존 CRUD 동작이 깨지지 않음을 보장 |
| **Safety** | 비정상 입력·손상 파일·경계값에서 앱이 안전하게 동작함을 보장 |

### Regression 테스트 목록 (`test_regression.py` — 25개)

**R-Create**

| ID | 검증 내용 |
|----|-----------|
| R-C1 | 반환 레코드에 5개 필드 모두 포함 |
| R-C2 | 저장 후 파일을 직접 읽어도 동일 레코드 존재 |
| R-C3 | 여러 건 생성 시 누적 저장 (덮어쓰기 안 됨) |
| R-C4 | 연속 생성 시 ID가 항상 다름 |

**R-Read**

| ID | 검증 내용 |
|----|-----------|
| R-R1 | 파일 없을 때 `[]` 반환 |
| R-R2 | 생성 후 `get_all` 개수 일치 |
| R-R3 | 전체 ID로 검색 성공 |
| R-R4 | ID 앞자리 8자로 검색 성공 |
| R-R5 | 없는 ID → `None` |
| R-R6 | 정확한 이름 검색 |
| R-R7 | 부분 이름 검색 (포함 여부) |
| R-R8 | 없는 이름 → `[]` |

**R-Update**

| ID | 검증 내용 |
|----|-----------|
| R-U1 | name 수정 후 재확인 |
| R-U2 | email 수정 후 재확인 |
| R-U3 | phone 수정 후 재확인 |
| R-U4 | 수정 후 파일에도 반영됨 |
| R-U5 | 수정 대상 외 레코드는 변경 없음 |

**R-Delete**

| ID | 검증 내용 |
|----|-----------|
| R-D1 | 삭제 후 `get_all` 개수 감소 |
| R-D2 | 삭제된 레코드 반환 |
| R-D3 | 삭제 후 파일에도 반영 |
| R-D4 | 삭제 대상 외 레코드는 유지 |

**R-Menu (UI 레이어)**

| ID | 검증 내용 |
|----|-----------|
| R-M1 | 빈 목록 시 안내 문구 출력 |
| R-M2 | 목록 출력 시 레코드 수 표시 |
| R-M3 | 정상 입력 시 저장 완료 메시지 |
| R-M4 | `n` 입력 시 삭제 취소 메시지 |

---

### Safety 테스트 목록 (`test_safety.py` — 23개)

**S-Input (입력값 경계)**

| ID | 검증 내용 |
|----|-----------|
| S-I1 | 특수문자 포함 이름 저장·복원 정확성 |
| S-I2 | 이모지 포함 이름 저장·복원 정확성 |
| S-I3 | 1000자 문자열 저장·복원 정확성 |
| S-I4 | `<script>` 포함 이름 — 이스케이프 없이 저장, 그대로 복원 |
| S-I5 | `"`, `\`, `'` 포함 — JSON 직렬화 안전성 |
| S-I6 | 개행 문자 포함 — 직렬화·역직렬화 안전성 |

**S-NotFound (없는 대상 접근)**

| ID | 검증 내용 |
|----|-----------|
| S-N1 | 없는 ID 수정 → `RecordNotFoundError` |
| S-N2 | 없는 ID 삭제 → `RecordNotFoundError` |
| S-N3 | 빈 문자열 prefix → 첫 번째 레코드 반환 |

**S-InvalidField (수정 불가 필드)**

| ID | 검증 내용 |
|----|-----------|
| S-F1 | `id` 필드 수정 → `InvalidFieldError` |
| S-F2 | `created_at` 필드 수정 → `InvalidFieldError` |
| S-F3 | 존재하지 않는 필드 수정 → `InvalidFieldError` |

**S-FileCorrupt (파일 손상)**

| ID | 검증 내용 |
|----|-----------|
| S-FC1 | 손상된 JSON 파일 → `JsonParseError`, 앱 비정상 종료 없음 |
| S-FC2 | 빈 파일 → `JsonParseError` |
| S-FC3 | 배열이 아닌 JSON 객체 파일 → 타입 오류 안전 처리 |

**S-Boundary (경계값)**

| ID | 검증 내용 |
|----|-----------|
| S-B1 | 마지막 레코드 삭제 → 파일이 빈 배열 `[]`로 저장 |
| S-B2 | 100건 연속 생성 후 `get_all` 개수 정확성 |
| S-B3 | 동일 이름 중복 생성 허용 여부 확인 |
| S-B4 | ID 접두사 중복 → 첫 번째 레코드 반환 |

**S-Menu (UI 안전성)**

| ID | 검증 내용 |
|----|-----------|
| S-M1 | 없는 ID 수정 → 오류 메시지 출력, 예외 전파 없음 |
| S-M2 | 없는 ID 삭제 → 오류 메시지 출력, 예외 전파 없음 |
| S-M3 | 검색 결과 없음 → 안내 메시지 출력 |
| S-M4 | 수정 필드 잘못된 번호 → 안내 메시지 출력 |

---

### 전체 테스트 결과

```
90 passed
```
