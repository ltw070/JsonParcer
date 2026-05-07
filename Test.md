# Regression & Safety Test 계획

## 목적

| 구분 | 목적 |
|------|------|
| **Regression Test** | 기능 변경 후에도 기존 CRUD 동작이 깨지지 않음을 보장 |
| **Safety Test** | 비정상 입력·손상 파일·경계값에서 앱이 안전하게 동작함을 보장 |

---

## 테스트 파일 구조

```
tests/
├── test_regression.py   # 회귀 테스트 — 정상 흐름 전체 커버
└── test_safety.py       # 안전성 테스트 — 비정상 입력 및 경계값
```

---

## Regression Test 목록

> 파일: `tests/test_regression.py`

### R-Create

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| R-C1 | `test_create_returns_complete_record` | 반환 레코드에 5개 필드 모두 포함 |
| R-C2 | `test_create_persists_to_file` | 저장 후 파일을 직접 읽어도 동일 레코드 존재 |
| R-C3 | `test_create_multiple_records` | 여러 건 생성 시 누적 저장 (덮어쓰기 안 됨) |
| R-C4 | `test_create_id_is_unique` | 연속 생성 시 ID가 항상 다름 |

### R-Read

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| R-R1 | `test_get_all_no_file` | 파일 없을 때 `[]` 반환 |
| R-R2 | `test_get_all_after_create` | 생성 후 `get_all` 개수 일치 |
| R-R3 | `test_find_by_id_full` | 전체 ID로 검색 성공 |
| R-R4 | `test_find_by_id_prefix` | ID 앞자리 8자로 검색 성공 |
| R-R5 | `test_find_by_id_missing` | 없는 ID → `None` |
| R-R6 | `test_find_by_name_exact` | 정확한 이름 검색 |
| R-R7 | `test_find_by_name_partial` | 부분 이름 검색 (포함 여부) |
| R-R8 | `test_find_by_name_missing` | 없는 이름 → `[]` |

### R-Update

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| R-U1 | `test_update_name` | name 수정 후 find_by_id로 재확인 |
| R-U2 | `test_update_email` | email 수정 후 재확인 |
| R-U3 | `test_update_phone` | phone 수정 후 재확인 |
| R-U4 | `test_update_persists_to_file` | 수정 후 파일을 직접 읽어도 반영됨 |
| R-U5 | `test_update_other_records_unchanged` | 수정 대상 외 레코드는 변경 없음 |

### R-Delete

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| R-D1 | `test_delete_removes_from_list` | 삭제 후 `get_all` 개수 감소 |
| R-D2 | `test_delete_returns_record` | 삭제된 레코드 반환 |
| R-D3 | `test_delete_persists_to_file` | 삭제 후 파일에도 반영 |
| R-D4 | `test_delete_other_records_unchanged` | 삭제 대상 외 레코드는 유지 |

### R-Menu (UI 레이어)

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| R-M1 | `test_handle_list_empty` | 빈 목록 시 안내 문구 출력 |
| R-M2 | `test_handle_list_with_records` | 목록 출력 시 레코드 수 표시 |
| R-M3 | `test_handle_create_success` | 정상 입력 시 저장 완료 메시지 |
| R-M4 | `test_handle_delete_cancel` | `n` 입력 시 삭제 취소 메시지 |

---

## Safety Test 목록

> 파일: `tests/test_safety.py`

### S-Input (입력값 경계)

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| S-I1 | `test_create_with_special_chars` | 특수문자 포함 이름 저장·복원 정확성 |
| S-I2 | `test_create_with_emoji` | 이모지 포함 이름 저장·복원 정확성 |
| S-I3 | `test_create_with_very_long_strings` | 1000자 문자열 저장·복원 정확성 |
| S-I4 | `test_create_with_script_tag` | `<script>` 포함 이름 — 이스케이프 없이 저장, 그대로 복원 |
| S-I5 | `test_create_with_quotes_and_backslash` | `"`, `\`, `'` 포함 — JSON 직렬화 안전성 |
| S-I6 | `test_create_with_newline_in_field` | 개행 문자 포함 — 직렬화·역직렬화 안전성 |

### S-NotFound (없는 대상 접근)

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| S-N1 | `test_update_nonexistent_id` | 없는 ID 수정 → `RecordNotFoundError` |
| S-N2 | `test_delete_nonexistent_id` | 없는 ID 삭제 → `RecordNotFoundError` |
| S-N3 | `test_find_by_id_empty_prefix` | 빈 문자열 prefix → 모든 레코드 앞자리와 일치 (첫 번째 반환) |

### S-InvalidField (수정 불가 필드)

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| S-F1 | `test_update_id_field` | `id` 필드 수정 → `InvalidFieldError` |
| S-F2 | `test_update_created_at_field` | `created_at` 필드 수정 → `InvalidFieldError` |
| S-F3 | `test_update_unknown_field` | 존재하지 않는 필드 수정 → `InvalidFieldError` |

### S-FileCorrupt (파일 손상)

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| S-FC1 | `test_load_corrupted_json` | 손상된 JSON 파일 → `JsonParseError`, 앱 비정상 종료 없음 |
| S-FC2 | `test_load_empty_file` | 빈 파일 → `JsonParseError` |
| S-FC3 | `test_load_json_object_not_list` | 배열이 아닌 JSON 객체 파일 → 타입 오류 안전 처리 |

### S-Boundary (경계값)

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| S-B1 | `test_delete_last_record` | 마지막 남은 레코드 삭제 → 파일이 빈 배열 `[]`로 저장 |
| S-B2 | `test_create_100_records` | 100건 연속 생성 후 `get_all` 개수 정확성 |
| S-B3 | `test_duplicate_name` | 동일 이름 중복 생성 허용 여부 확인 |
| S-B4 | `test_id_prefix_ambiguity` | 여러 레코드의 ID가 동일 접두사로 시작 → 첫 번째 레코드 반환 |

### S-Menu (UI 안전성)

| ID | 테스트 이름 | 검증 내용 |
|----|-------------|-----------|
| S-M1 | `test_handle_update_not_found` | 없는 ID → 오류 메시지 출력, 예외 전파 없음 |
| S-M2 | `test_handle_delete_not_found` | 없는 ID → 오류 메시지 출력, 예외 전파 없음 |
| S-M3 | `test_handle_search_no_result` | 검색 결과 없음 → 안내 메시지 출력 |
| S-M4 | `test_handle_update_invalid_field_choice` | 수정 필드 선택에서 잘못된 번호 → 안내 메시지 출력 |

---

## 성공 기준

| 구분 | 기준 |
|------|------|
| Regression | 22개 테스트 전부 PASSED |
| Safety | 22개 테스트 전부 PASSED |
| 합계 | **44개 전부 PASSED** |
| 기존 테스트 | 기존 42개 회귀 없음 (총 86개 PASSED) |

---

## 실행 방법

```bash
# 전체 실행
pytest tests/test_regression.py tests/test_safety.py -v

# 기존 테스트 포함 전체
pytest tests/ -v
```
