from app.menu import show_menu, handle_list, handle_search, handle_create, handle_update, handle_delete

_HANDLERS = {
    "1": handle_list,
    "2": handle_search,
    "3": handle_create,
    "4": handle_update,
    "5": handle_delete,
}


def main() -> None:
    while True:
        show_menu()
        choice = input("선택: ").strip()
        if choice == "0":
            print("종료합니다.")
            break
        handler = _HANDLERS.get(choice)
        if handler:
            handler()
        else:
            print("올바른 메뉴를 선택해주세요.")


if __name__ == "__main__":
    main()
