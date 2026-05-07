# CLAUDE.md — 프로젝트 가이드

## 프로젝트 개요

JSON 파일을 영구 저장소로 사용하는 **CRUD 콘솔 애플리케이션** 개발 프로젝트.
PoC(`json_lib`)에서 검증한 라이브러리를 그대로 재사용하며, 수정 없이 import만으로 활용한다.

---

## 핵심 규칙

- `json_lib/` 코드는 **절대 수정하지 않는다.** import만 허용.
- 모든 비즈니스 로직은 `app/repository.py`에 집중한다.
- 구현 순서는 항상 **TDD(Red → Green → Refactor)** 를 따른다.
- 외부 의존성을 추가하지 않는다. 표준 라이브러리만 사용.

---

## 문서 구조

| 문서 | 위치 | 설명 |
|------|------|------|
| 전체 개발 계획 | [`AppDevPlan.md`](AppDevPlan.md) | 아키텍처, CRUD 명세, 성공 기준 |
| PoC 라이브러리 명세 | [`Spec.md`](Spec.md) | json_lib API 상세 |
| PoC 구현 계획 | [`plan.md`](plan.md) | PoC TDD 단계별 계획 |
| Step 1 상세 | [`docs/design/Step1.md`](docs/design/Step1.md) | models.py TDD |
| Step 2 상세 | [`docs/design/Step2.md`](docs/design/Step2.md) | repository.py TDD |
| Step 3 상세 | [`docs/design/Step3.md`](docs/design/Step3.md) | menu.py + main.py |
| Step 4 상세 | [`docs/design/Step4.md`](docs/design/Step4.md) | 통합 E2E 검증 |

---

## 디렉토리 구조

```
JsonParcer/
├── json_lib/              # PoC 라이브러리 (수정 금지)
│   ├── __init__.py        # parse, load, save, validate 공개
│   ├── exceptions.py      # JsonLibraryError 계층
│   ├── parser.py          # parse(), load()
│   ├── writer.py          # save()
│   └── validator.py       # validate()
├── app/                   # CRUD 앱 (이번 개발 대상)
│   ├── main.py            # 진입점, 메뉴 루프
│   ├── menu.py            # 콘솔 입출력
│   ├── repository.py      # CRUD 로직
│   └── models.py          # 레코드 생성 헬퍼
├── data/
│   └── records.json       # 런타임 자동 생성
├── tests/
│   ├── test_parser.py     # PoC 테스트 (유지)
│   ├── test_writer.py
│   ├── test_validator.py
│   ├── test_models.py     # 신규
│   └── test_repository.py # 신규
├── docs/
│   └── design/
│       ├── Step1.md       # models.py 상세 계획
│       ├── Step2.md       # repository.py 상세 계획
│       ├── Step3.md       # menu.py + main.py 상세 계획
│       └── Step4.md       # 통합 E2E 검증 계획
├── CLAUDE.md              # 이 파일
├── AppDevPlan.md          # 전체 개발 계획
├── Spec.md                # PoC 명세
├── plan.md                # PoC 구현 계획
└── README.md              # 사용 방법
```

---

## 데이터 모델

```python
# 레코드 구조
{
    "id":         str,   # uuid4, 자동 생성
    "name":       str,   # 사용자 입력
    "email":      str,   # 사용자 입력
    "phone":      str,   # 사용자 입력
    "created_at": str,   # ISO 8601, 자동 생성
}

# validate() 스키마
SCHEMA = {"id": str, "name": str, "email": str, "phone": str, "created_at": str}
```

---

## 레이어 의존 방향

```
main.py
  └── menu.py          (입출력 처리)
        └── repository.py  (CRUD 로직)
              ├── models.py      (레코드 생성)
              └── json_lib       (파일 I/O, 검증)
```

---

## 앱 예외 계층

```
AppError                    # 앱 레이어 최상위 예외
├── RecordNotFoundError     # ID로 레코드를 찾지 못함
└── InvalidFieldError       # 수정 불가 필드 지정 (id, created_at)
```

`json_lib` 예외(`JsonLibraryError`)는 `menu.py`에서 별도로 잡아 처리한다.

---

## CRUD 앱 실행

```bash
# 프로젝트 루트에서 실행
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

---

## 테스트 실행

```bash
# 전체 테스트 (PoC + App)
pytest tests/ -v

# 모듈별 실행
pytest tests/test_models.py -v       # Step 1 — 6개
pytest tests/test_repository.py -v  # Step 2 — 17개
pytest tests/test_parser.py tests/test_writer.py tests/test_validator.py -v  # PoC — 19개
```

**전체 테스트 커버리지**

| 파일 | 테스트 수 | 대상 |
|------|-----------|------|
| `test_models.py` | 6 | `app/models.py` |
| `test_repository.py` | 17 | `app/repository.py` |
| `test_parser.py` | 7 | `json_lib/parser.py` |
| `test_writer.py` | 7 | `json_lib/writer.py` |
| `test_validator.py` | 5 | `json_lib/validator.py` |
| **합계** | **42** | |

---

## 새 기능 추가 가이드

1. `app/exceptions.py` — 필요한 예외 추가
2. `tests/test_repository.py` — 실패 테스트 먼저 작성 (Red)
3. `app/repository.py` — 최소 구현 (Green)
4. `app/menu.py` — UI 핸들러 추가
5. `app/main.py` — 메뉴 항목 등록
6. `pytest tests/ -v` — 전체 회귀 확인

---

## 구현 진행 상태

| Step | 내용 | 테스트 | 상태 |
|------|------|--------|------|
| PoC | json_lib 라이브러리 | 19/19 | ✅ 완료 |
| Step 1 | models.py | 6/6 | ✅ 완료 |
| Step 2 | repository.py | 17/17 | ✅ 완료 |
| Step 3 | menu.py + main.py | 27/27 (시나리오) | ✅ 완료 |
| Step 4 | 통합 E2E 검증 | 42/42 | ✅ 완료 |
