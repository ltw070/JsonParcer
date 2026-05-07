import app.repository as repo
from app.exceptions import RecordNotFoundError, InvalidFieldError
from json_lib.exceptions import JsonLibraryError

_DIVIDER = "─" * 56


def show_menu() -> None:
    print("\n=============================")
    print("   연락처 관리 (JSON CRUD)")
    print("=============================")
    print("1. 전체 목록 보기")
    print("2. 검색")
    print("3. 새 연락처 추가")
    print("4. 연락처 수정")
    print("5. 연락처 삭제")
    print("0. 종료")
    print(_DIVIDER)


def _print_table(records: list) -> None:
    if not records:
        print("등록된 연락처가 없습니다.")
        return
    print(f"\n{'번호':>4}  {'ID':8}  {'이름':<8}  {'이메일':<22}  {'전화번호'}")
    print(_DIVIDER)
    for i, r in enumerate(records, 1):
        print(f"{i:>4}  {r['id'][:8]}  {r['name']:<8}  {r['email']:<22}  {r['phone']}")
    print(f"총 {len(records)}건")


def _print_detail(record: dict) -> None:
    print(_DIVIDER)
    print(f"  ID       : {record['id']}")
    print(f"  이름     : {record['name']}")
    print(f"  이메일   : {record['email']}")
    print(f"  전화번호 : {record['phone']}")
    print(f"  생성일   : {record['created_at']}")
    print(_DIVIDER)


def _input_required(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        field = prompt.split(":")[0].strip()
        print(f"  [{field}] 항목은 비워둘 수 없습니다.")


def handle_list() -> None:
    _print_table(repo.get_all())


def handle_search() -> None:
    print("\n검색 방식 선택:")
    print("  1) ID로 검색")
    print("  2) 이름으로 검색")
    choice = input("선택: ").strip()

    if choice == "1":
        prefix = input("검색할 ID 앞자리: ").strip()
        record = repo.find_by_id(prefix)
        if record:
            _print_detail(record)
        else:
            print("해당 ID의 연락처를 찾을 수 없습니다.")
    elif choice == "2":
        keyword = input("검색할 이름: ").strip()
        results = repo.find_by_name(keyword)
        if results:
            print(f"→ {len(results)}건 검색됨")
            _print_table(results)
        else:
            print("검색 결과가 없습니다.")
    else:
        print("올바른 검색 방식을 선택해주세요.")


def handle_create() -> None:
    print("\n=== 새 연락처 추가 ===")
    try:
        name = _input_required("이름     : ")
        email = _input_required("이메일   : ")
        phone = _input_required("전화번호 : ")
        record = repo.create(name, email, phone)
        print(f"→ 저장되었습니다. (ID: {record['id']})")
    except (JsonLibraryError, AppError) as e:
        print(f"오류: {e}")


def handle_update() -> None:
    print("\n=== 연락처 수정 ===")
    prefix = input("수정할 ID 앞자리: ").strip()
    try:
        record = repo.find_by_id(prefix)
        if not record:
            print("해당 ID의 연락처를 찾을 수 없습니다.")
            return
        _print_detail(record)
        print("수정할 필드:  1) 이름   2) 이메일   3) 전화번호")
        field_map = {"1": "name", "2": "email", "3": "phone"}
        label_map = {"1": "새 이름", "2": "새 이메일", "3": "새 전화번호"}
        choice = input("선택: ").strip()
        if choice not in field_map:
            print("올바른 항목을 선택해주세요.")
            return
        value = _input_required(f"{label_map[choice]}: ")
        repo.update(prefix, field_map[choice], value)
        print("→ 수정되었습니다.")
    except (RecordNotFoundError, InvalidFieldError) as e:
        print(f"오류: {e}")
    except JsonLibraryError as e:
        print(f"데이터 오류: {e}")


def handle_delete() -> None:
    print("\n=== 연락처 삭제 ===")
    prefix = input("삭제할 ID 앞자리: ").strip()
    try:
        record = repo.find_by_id(prefix)
        if not record:
            print("해당 ID의 연락처를 찾을 수 없습니다.")
            return
        _print_detail(record)
        confirm = input("정말 삭제하시겠습니까? (y/n): ").strip().lower()
        if confirm == "y":
            repo.delete(prefix)
            print("→ 삭제되었습니다.")
        else:
            print("삭제가 취소되었습니다.")
    except RecordNotFoundError as e:
        print(f"오류: {e}")
    except JsonLibraryError as e:
        print(f"데이터 오류: {e}")


# handle_create에서 AppError를 참조하기 위한 import 보완
from app.exceptions import AppError  # noqa: E402
