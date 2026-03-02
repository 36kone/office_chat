from app.users.repositories.users_repository import UserRepository


class UserService:

    @staticmethod
    def create_user(data: dict):
        return UserRepository.create(data)

    @staticmethod
    def get_user(user_id: int):
        return UserRepository.get_by_id(user_id)

    @staticmethod
    def search_users(search: str, page: int):
        return UserRepository.search(search, page)

    @staticmethod
    def update_user(user_id: int, data: dict):
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None
        return UserRepository.update(user, data)

    @staticmethod
    def delete_user(user_id: int):
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False
        UserRepository.delete(user)
        return True