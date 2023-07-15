from attrs import define


@define
class User:
    email: str
    full_name: str
    password: str
    profile_photo: str
    id: int = 0


class UsersRepository:
    users: list[User]

    def __init__(self):
        self.users = []

    def save_user(self, user):
        user.id = len(self.users) + 1
        self.users.append(user)

    def email_exists(self, email):
        for u in self.users:
            if u.email == email:
                return True
        return False

    @staticmethod
    def password_is_valid(password):
        if len(password) < 8:
            return False
        return True

    def get_user_by_email(self, email) -> User:
        for user in self.users:
            if user.email == email:
                return user
        return None

    def get_user_by_id(self, id) -> User:
        for user in self.users:
            if  user.id == id:
                return user
        return None

    def update_password(self, email, password):
        user = self.get_user_by_email(email)
        if user:
            user.password = password
            return True
        else:
            return False

    def update_profile(self,user_id,user):
        for i,u in enumerate(self.users):
            if u.id == user_id:
                user.id = u.id
                user.email = u.email
                self.users[i] = user
                break


