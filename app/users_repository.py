from attrs import define


@define
class User:
    email: str
    name: str
    lastname: str
    password: str
    profile_photo: str
    id: int = 0


class UsersRepository:
    users: list[User]

    def __init__(self):
        self.users = []
        self.carts = [{
            "user_id": None, "cart": None}]

    def save_user(self, user):
        user.id = len(self.users) + 1
        self.users.append(user)

    def email_exists(self, email):
        for u in self.users:
            if u.email == email:
                return True
        return False

    def get_user_by_email(self, email) -> User:
        for user in self.users:
            if user.email == email:
                return user
        return None

    def get_user_by_id(self, id) -> User:
        for user in self.users:
            if user.id == id:
                return user
        return None

    def update_profile(self, user_id, user):
        for i, u in enumerate(self.users):
            if u.id == user_id:
                user.id = u.id
                user.email = u.email
                self.users[i] = user
                break

    def is_authenticated(self, user_id):
        for u in self.users:
            if u.id == user_id:
                return True
        return False

    def save_cart(self, user_id, cart):
        self.carts.append({"user_id":user_id,"cart":cart})

    def get_all_cart_by_id(self, user_id):
        for i, с in enumerate(self.carts):
            if с["user_id"] == user_id:
                return с

