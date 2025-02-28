def is_registered(user_id) -> bool:
    with open("user.txt", "r") as f:
        f_str = f.read()
    return str(user_id) in f_str