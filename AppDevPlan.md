# CRUD 콘솔 애플리케이션 개발 계획

## 개요

PoC에서 검증한 `json_lib` 라이브러리(`parse`, `load`, `save`, `validate`)를 그대로 활용하여,
JSON 파일을 영구 저장소로 사용하는 CRUD 콘솔 애플리케이션을 개발한다.

---

## PoC와 App의 관계

```
[PoC — json_lib]                  [App — 이번 개발 대상]
─────────────────                 ──────────────────────────────
parse()   ──────────────────────→ Repository 레이어에서 파일 읽기
load()    ──────────────────────→ 시작 시 데이터 로드
save()    ──────────────────────→ CRUD 작업 후 파일 저장
validate()──────────────────────→ Create/Update 입력값 검증
exceptions──────────────────────→ App 레이어 예외 처리에 활용
```

- `json_lib/` 코드는 **수정하지 않는다.** App은 라이브러리를 import해서 사용한다.
- 데이터 파일: `data/records.json` (App 실행 디렉토리 기준)

---

## 데이터 모델

관리 대상 레코드를 **"연락처(Contact)"** 로 정의한다.
(필드는 단순하면서 CRUD 전 기능을 명확하게 보여줄 수 있는 수준으로 설계)

```json
{
  "id": "uuid4 문자열",
  "name": "홍길동",
  "email": "hong@example.com",
  "phone": "010-1234-5678",
  "created_at": "2026-05-07T12:00:00"
}
```

**스키마 (validate에 사용)**
```python
SCHEMA = {
    "id": str,
    "name": str,
    "email": str,
    "phone": str,
    "created_at": str,
}
```

**파일 구조** (`data/records.json`)
```json
[
  { "id": "...", "name": "...", "email": "...", "phone": "...", "created_at": "..." },
  { "id": "...", "name": "...", "email": "...", "phone": "...", "created_at": "..." }
]
```

---

## 아키텍처

```
app/
├── main.py           # 진입점: 메뉴 루프
├── menu.py           # 콘솔 메뉴 출력 및 입력 처리
├── repository.py     # CRUD 로직 + json_lib 호출
└── models.py         # 레코드 생성 헬퍼 (uuid, timestamp)
```

### 레이어 책임

| 레이어 | 파일 | 책임 |
|--------|------|------|
| 진입점 | `main.py` | 앱 시작, 메뉴 루프 실행 |
| UI | `menu.py` | 사용자 입력/출력, 메뉴 렌더링 |
| 비즈니스 | `repository.py` | CRUD 구현, `json_lib` 호출 |
| 모델 | `models.py` | 레코드 딕셔너리 생성 (id, timestamp 자동 부여) |

---

## CRUD 기능 명세

### Create — 새 연락처 추가

**흐름**
1. 사용자에게 `name`, `email`, `phone` 입력 받기
2. `models.py`에서 `id`(uuid4), `created_at`(현재 시각) 자동 생성
3. `validate(record, SCHEMA)` 로 유효성 검사
4. 기존 목록 `load()` → 새 레코드 append → `save()`

**입력 예시**
```
이름: 홍길동
이메일: hong@example.com
전화번호: 010-1234-5678
→ 저장되었습니다. (ID: a1b2c3d4-...)
```

---

### Read — 목록 조회 / 검색

**흐름 — 전체 목록**
1. `load()` 로 전체 레코드 읽기
2. 번호, ID(앞 8자리), 이름, 이메일, 전화번호 표 형태로 출력

**흐름 — ID 검색**
1. 검색할 ID 앞자리(또는 전체) 입력
2. `startswith` 매칭으로 해당 레코드 출력

**흐름 — 이름 검색**
1. 검색어 입력
2. `name` 필드에 검색어 포함 여부(`in` 연산자)로 필터링 후 출력

**출력 예시 (전체 목록)**
```
번호  ID        이름      이메일                전화번호
─────────────────────────────────────────────────────────
  1   a1b2c3d4  홍길동    hong@example.com      010-1234-5678
  2   e5f6g7h8  김철수    kim@example.com       010-9876-5432
총 2건
```

---

### Update — 특정 필드 수정

**흐름**
1. 수정할 레코드의 ID(앞자리) 입력
2. 해당 레코드 출력 후 수정할 필드 선택 (`name` / `email` / `phone`)
3. 새 값 입력
4. `validate()` 검사 후 `save()`

**입력 예시**
```
수정할 ID: a1b2c3d4
수정할 필드 선택: 1) 이름  2) 이메일  3) 전화번호
선택: 2
새 이메일: newhong@example.com
→ 수정되었습니다.
```

---

### Delete — 특정 레코드 삭제

**흐름**
1. 삭제할 레코드의 ID(앞자리) 입력
2. 해당 레코드 내용 출력 및 삭제 확인 (`y/n`)
3. 확인 시 목록에서 제거 후 `save()`

**입력 예시**
```
삭제할 ID: a1b2c3d4
[홍길동 / hong@example.com / 010-1234-5678]
정말 삭제하시겠습니까? (y/n): y
→ 삭제되었습니다.
```

---

## 콘솔 메뉴 구조

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
──────────────────────────────
선택:
```

---

## 디렉토리 최종 구조

```
JsonParcer/
├── json_lib/             ← PoC 라이브러리 (수정 없음)
│   ├── __init__.py
│   ├── exceptions.py
│   ├── parser.py
│   ├── writer.py
│   └── validator.py
├── app/                  ← 이번 개발 대상
│   ├── main.py
│   ├── menu.py
│   ├── repository.py
│   └── models.py
├── data/
│   └── records.json      ← 런타임에 자동 생성
├── tests/
│   ├── test_parser.py    ← PoC 테스트 (유지)
│   ├── test_writer.py
│   ├── test_validator.py
│   ├── test_repository.py ← 신규 (TDD)
│   └── test_models.py    ← 신규 (TDD)
├── AppDevPlan.md
├── Spec.md
├── plan.md
└── README.md
```

---

## 구현 순서 (TDD 적용)

PoC와 동일하게 **Red → Green → Refactor** 사이클을 유지한다.

```
Step 1  models.py
        [Red]   test_models.py 작성 (레코드 생성, id/timestamp 자동 부여)
        [Green] models.py 구현
        [Refactor]

Step 2  repository.py
        [Red]   test_repository.py 작성 (CRUD 각 함수 단위 테스트)
        [Green] repository.py 구현 (json_lib 활용)
        [Refactor]

Step 3  menu.py + main.py
        단위 테스트 없음 (I/O 레이어)
        직접 실행하여 수동 검증

Step 4  통합 검증
        시나리오 기반 수동 E2E 테스트
```

---

## 성공 기준

- [ ] `Create` — 입력한 데이터가 `records.json`에 저장된다
- [ ] `Read` — 전체 목록이 표 형태로 출력된다
- [ ] `Read` — ID 앞자리 또는 이름으로 검색이 동작한다
- [ ] `Update` — 선택한 필드가 수정되고 파일에 반영된다
- [ ] `Delete` — 확인 후 레코드가 삭제되고 파일에 반영된다
- [ ] `json_lib` 코드를 수정하지 않고 import만으로 재사용한다
- [ ] `repository.py` 단위 테스트가 모두 통과한다
- [ ] 잘못된 입력(빈 값, 없는 ID)에 대해 오류 메시지를 출력하고 앱이 종료되지 않는다

---

## 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Python 3.11+ |
| 데이터 저장 | JSON 파일 (`data/records.json`) |
| PoC 재사용 | `json_lib` (parse, load, save, validate) |
| ID 생성 | `uuid` (표준 라이브러리) |
| 시각 | `datetime` (표준 라이브러리) |
| 테스트 | `pytest` |
| 외부 의존성 | 없음 |
