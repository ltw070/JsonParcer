# Step 4 — 통합 E2E 검증

## 목표

Step 1~3에서 구현한 모든 레이어가 함께 동작하는지 검증한다.
`AppDevPlan.md`의 성공 기준 체크리스트를 항목 단위로 확인한다.

---

## 검증 방법

| 대상 | 방법 |
|------|------|
| `models.py` | `pytest tests/test_models.py -v` |
| `repository.py` | `pytest tests/test_repository.py -v` |
| PoC `json_lib` | `pytest tests/test_parser.py tests/test_writer.py tests/test_validator.py -v` |
| 전체 단위 테스트 | `pytest tests/ -v` |
| 콘솔 앱 | `python -m app.main` 직접 실행 + 시나리오 수동 검증 |

---

## E2E 시나리오

아래 시나리오를 순서대로 실행하여 각 항목의 성공/실패를 기록한다.

### 시나리오 A — 빈 상태에서 시작

```
조건: data/records.json 없음 (또는 삭제 후 실행)
```

1. 앱 실행: `python -m app.main`
2. `1` 선택 → `"등록된 연락처가 없습니다."` 출력 확인

**기대 결과**: 파일 없어도 앱이 오류 없이 동작한다.

---

### 시나리오 B — Create × 3건

레코드 3건을 순서대로 입력한다.

| 순서 | 이름 | 이메일 | 전화번호 |
|------|------|--------|----------|
| 1 | 홍길동 | hong@example.com | 010-1234-5678 |
| 2 | 김철수 | kim@example.com | 010-9876-5432 |
| 3 | 이영희 | lee@example.com | 010-5555-1234 |

**검증 항목**
- [ ] 각 저장 후 ID가 출력된다
- [ ] `data/records.json` 파일이 생성된다
- [ ] 파일을 열면 3건의 레코드가 올바른 형식으로 저장되어 있다

---

### 시나리오 C — Read (전체 목록)

```
1 선택
```

**검증 항목**
- [ ] 3건이 표 형태로 출력된다
- [ ] ID는 앞 8자리만 표시된다
- [ ] `총 3건` 문구가 출력된다

---

### 시나리오 D — Read (검색)

**ID 검색**
```
2 → 1 → 홍길동의 ID 앞 8자리 입력
```
- [ ] 홍길동 레코드 상세 출력 확인

**이름 검색**
```
2 → 2 → "이" 입력
```
- [ ] 이영희 1건만 출력 확인

**존재하지 않는 검색**
```
2 → 2 → "없는이름" 입력
```
- [ ] `"검색 결과가 없습니다."` 출력, 앱 종료 안 됨

---

### 시나리오 E — Update

```
4 → 홍길동 ID 앞자리 → 2(이메일) → newhong@example.com
```

**검증 항목**
- [ ] `"수정되었습니다."` 출력
- [ ] `1` 선택 후 홍길동 이메일이 `newhong@example.com`으로 변경된 것 확인
- [ ] `data/records.json` 파일에도 반영 확인

---

### 시나리오 F — Delete

```
5 → 김철수 ID 앞자리 → y
```

**검증 항목**
- [ ] `"삭제되었습니다."` 출력
- [ ] `1` 선택 후 김철수 레코드 없음 확인 (`총 2건`)
- [ ] `data/records.json` 파일에도 반영 확인

---

### 시나리오 G — 오류 처리

| 동작 | 기대 결과 |
|------|-----------|
| `4` → 없는 ID 입력 | `"해당 ID의 연락처를 찾을 수 없습니다."` 출력, 메뉴 복귀 |
| `5` → 없는 ID 입력 | `"해당 ID의 연락처를 찾을 수 없습니다."` 출력, 메뉴 복귀 |
| `3` → 이름 빈 값 | `"이름 항목은 비워둘 수 없습니다."` 출력, 재입력 |
| `3` → `n` 입력(잘못된 메뉴) | `"올바른 메뉴를 선택해주세요."` 출력 |
| `5` → ID 입력 → `n` 선택 | `"삭제가 취소되었습니다."` 출력, 메뉴 복귀 |

**검증 항목**
- [ ] 모든 오류 상황에서 앱이 종료되지 않는다

---

## 전체 테스트 실행 결과 확인

```bash
pytest tests/ -v
```

**기대 출력**
```
tests/test_parser.py::test_parse_dict              PASSED
tests/test_parser.py::test_parse_list              PASSED
tests/test_parser.py::test_parse_invalid_json      PASSED
tests/test_parser.py::test_parse_non_string        PASSED
tests/test_parser.py::test_load_file               PASSED
tests/test_parser.py::test_load_file_not_found     PASSED
tests/test_parser.py::test_load_invalid_content    PASSED
tests/test_validator.py::test_validate_success           PASSED
tests/test_validator.py::test_validate_missing_key       PASSED
tests/test_validator.py::test_validate_wrong_type        PASSED
tests/test_validator.py::test_validate_error_message_key PASSED
tests/test_validator.py::test_validate_error_message_type PASSED
tests/test_writer.py::test_save_creates_file             PASSED
tests/test_writer.py::test_save_creates_directories      PASSED
tests/test_writer.py::test_save_content_correct          PASSED
tests/test_writer.py::test_save_overwrite_false          PASSED
tests/test_writer.py::test_save_overwrite_true           PASSED
tests/test_writer.py::test_save_non_serializable         PASSED
tests/test_writer.py::test_save_korean                   PASSED
tests/test_models.py::test_create_record_returns_dict           PASSED
tests/test_models.py::test_create_record_has_all_fields         PASSED
tests/test_models.py::test_create_record_id_is_uuid_string      PASSED
tests/test_models.py::test_create_record_name_email_phone_match_input PASSED
tests/test_models.py::test_create_record_created_at_is_iso_string    PASSED
tests/test_models.py::test_create_record_ids_are_unique              PASSED
tests/test_repository.py::test_get_all_empty_when_no_file    PASSED
tests/test_repository.py::test_get_all_returns_all_records   PASSED
tests/test_repository.py::test_find_by_id_found              PASSED
tests/test_repository.py::test_find_by_id_not_found          PASSED
tests/test_repository.py::test_find_by_name_found            PASSED
tests/test_repository.py::test_find_by_name_not_found        PASSED
tests/test_repository.py::test_create_adds_record            PASSED
tests/test_repository.py::test_create_returns_new_record     PASSED
tests/test_repository.py::test_create_persists_to_file       PASSED
tests/test_repository.py::test_update_name                   PASSED
tests/test_repository.py::test_update_email                  PASSED
tests/test_repository.py::test_update_phone                  PASSED
tests/test_repository.py::test_update_not_found              PASSED
tests/test_repository.py::test_update_invalid_field          PASSED
tests/test_repository.py::test_delete_removes_record         PASSED
tests/test_repository.py::test_delete_returns_deleted_record  PASSED
tests/test_repository.py::test_delete_not_found              PASSED

42 passed
```

---

## AppDevPlan.md 성공 기준 최종 체크

```
- [ ] Create  — 입력한 데이터가 records.json에 저장된다
- [ ] Read    — 전체 목록이 표 형태로 출력된다
- [ ] Read    — ID 앞자리 또는 이름으로 검색이 동작한다
- [ ] Update  — 선택한 필드가 수정되고 파일에 반영된다
- [ ] Delete  — 확인 후 레코드가 삭제되고 파일에 반영된다
- [ ] json_lib 코드를 수정하지 않고 import만으로 재사용한다
- [ ] repository.py 단위 테스트가 모두 통과한다
- [ ] 잘못된 입력에 대해 오류 메시지를 출력하고 앱이 종료되지 않는다
```

---

## 완료 체크리스트

- [ ] `pytest tests/ -v` — 42개 전부 PASSED
- [ ] E2E 시나리오 A~G 모두 확인
- [ ] `AppDevPlan.md` 성공 기준 전 항목 체크
- [ ] `CLAUDE.md` 구현 진행 상태 표 Step 1~4 모두 ✅ 완료로 업데이트
