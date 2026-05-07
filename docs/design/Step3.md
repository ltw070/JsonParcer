# Step 3 — menu.py + main.py

## 목표

`repository.py`를 호출하는 콘솔 UI 레이어를 구현한다.
I/O 레이어이므로 단위 테스트 대신 **직접 실행을 통한 수동 검증**으로 완료를 판단한다.

---

## 구현 대상

### `app/menu.py`

사용자 입출력과 메뉴 렌더링을 담당한다.
`repository.py` 함수를 직접 호출하며, 예외를 잡아 오류 메시지를 출력하고 앱을 종료시키지 않는다.

```python
def show_menu() -> None          # 메뉴 출력
def handle_list() -> None        # 전체 목록 출력
def handle_search() -> None      # 검색 (ID / 이름 선택)
def handle_create() -> None      # 새 연락처 입력 및 저장
def handle_update() -> None      # 수정할 레코드 선택 및 필드 수정
def handle_delete() -> None      # 삭제할 레코드 선택 및 확인
```

### `app/main.py`

앱 진입점. 메뉴 루프를 실행한다.

```python
def main() -> None               # 메뉴 루프
```

---

## 상세 구현 명세

### `show_menu()`

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

### `handle_list()`

`repository.get_all()` 호출 후 표 형태로 출력한다.

```
번호  ID        이름      이메일                전화번호
─────────────────────────────────────────────────────────
  1   a1b2c3d4  홍길동    hong@example.com      010-1234-5678
  2   e5f6g7h8  김철수    kim@example.com       010-9876-5432
총 2건
```

- ID는 `id[:8]` (앞 8자리)만 표시한다.
- 레코드가 없으면 `"등록된 연락처가 없습니다."` 출력.

---

### `handle_search()`

검색 방식을 선택 받는다.

```
검색 방식 선택:
1) ID로 검색
2) 이름으로 검색
선택:
```

**ID 검색**
```
검색할 ID 앞자리: a1b2c3d4
─────────────────────────────
ID       : a1b2c3d4-xxxx-...
이름     : 홍길동
이메일   : hong@example.com
전화번호 : 010-1234-5678
생성일   : 2026-05-07T12:00:00
```
- 결과 없으면 `"해당 ID의 연락처를 찾을 수 없습니다."` 출력.

**이름 검색**
```
검색할 이름: 홍
→ 1건 검색됨
  1   a1b2c3d4  홍길동    hong@example.com      010-1234-5678
```

---

### `handle_create()`

```
=== 새 연락처 추가 ===
이름     : 홍길동
이메일   : hong@example.com
전화번호 : 010-1234-5678
→ 저장되었습니다. (ID: a1b2c3d4-...)
```

- 빈 값 입력 시: `"[이름] 항목은 비워둘 수 없습니다."` 출력 후 재입력 요구.

---

### `handle_update()`

```
=== 연락처 수정 ===
수정할 ID 앞자리: a1b2c3d4

현재 정보:
  이름     : 홍길동
  이메일   : hong@example.com
  전화번호 : 010-1234-5678

수정할 필드:
1) 이름   2) 이메일   3) 전화번호
선택: 2
새 이메일: newhong@example.com
→ 수정되었습니다.
```

- 없는 ID 입력 시: `"해당 ID의 연락처를 찾을 수 없습니다."` 출력 후 메뉴로 복귀.
- 빈 값 입력 시: `"값을 비워둘 수 없습니다."` 출력 후 재입력 요구.

---

### `handle_delete()`

```
=== 연락처 삭제 ===
삭제할 ID 앞자리: a1b2c3d4

삭제 대상:
  이름     : 홍길동
  이메일   : hong@example.com
  전화번호 : 010-1234-5678

정말 삭제하시겠습니까? (y/n): y
→ 삭제되었습니다.
```

- `n` 입력 시: `"삭제가 취소되었습니다."` 출력 후 메뉴로 복귀.
- 없는 ID 입력 시: `"해당 ID의 연락처를 찾을 수 없습니다."` 출력.

---

### `main()`

```python
def main():
    while True:
        show_menu()
        choice = input("선택: ").strip()
        if choice == "1":
            handle_list()
        elif choice == "2":
            handle_search()
        elif choice == "3":
            handle_create()
        elif choice == "4":
            handle_update()
        elif choice == "5":
            handle_delete()
        elif choice == "0":
            print("종료합니다.")
            break
        else:
            print("올바른 메뉴를 선택해주세요.")
```

---

## 예외 처리 원칙

`menu.py`의 모든 `handle_*` 함수는 예외를 직접 잡아 처리하고 앱을 종료시키지 않는다.

```python
from app.exceptions import RecordNotFoundError, InvalidFieldError
from json_lib.exceptions import JsonLibraryError

try:
    ...
except RecordNotFoundError as e:
    print(f"오류: {e}")
except InvalidFieldError as e:
    print(f"오류: {e}")
except JsonLibraryError as e:
    print(f"데이터 오류: {e}")
```

---

## 수동 검증 시나리오

### 시나리오 1 — Create 후 목록 확인

1. `3` 선택 → 이름/이메일/전화번호 입력
2. `1` 선택 → 목록에 추가된 레코드 확인
3. `data/records.json` 파일 직접 열어 내용 확인

### 시나리오 2 — 검색

1. `2` 선택 → `1`(ID 검색) → 앞 8자리 입력 → 레코드 출력 확인
2. `2` 선택 → `2`(이름 검색) → 일부 이름 입력 → 필터 결과 확인

### 시나리오 3 — Update

1. `4` 선택 → ID 입력 → 이메일 수정
2. `1` 선택 → 목록에서 이메일 변경 확인

### 시나리오 4 — Delete

1. `5` 선택 → ID 입력 → `y` 확인
2. `1` 선택 → 목록에서 레코드 제거 확인

### 시나리오 5 — 오류 처리

1. `4` 선택 → 없는 ID 입력 → 오류 메시지 출력 후 메뉴 복귀 확인
2. `3` 선택 → 이름 빈 값 → 재입력 요구 확인
3. `9` 선택 → `"올바른 메뉴를 선택해주세요."` 출력 확인

---

## 완료 체크리스트

- [ ] `app/menu.py` 구현 (`show_menu`, `handle_list`, `handle_search`, `handle_create`, `handle_update`, `handle_delete`)
- [ ] `app/main.py` 구현 (`main` 함수, `if __name__ == "__main__"` 진입점)
- [ ] `python -m app.main` 실행 성공
- [ ] 수동 시나리오 1~5 모두 예상대로 동작 확인
- [ ] `pytest tests/ -v` 전체 통과 유지 확인 (기존 테스트 회귀 없음)
