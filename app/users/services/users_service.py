from uuid import UUID

from app.users.repositories.users_repository import UserRepository


class UserService:
    @staticmethod
    def create_user(data: dict):
        return UserRepository.create(data)

    @staticmethod
    def get_user(user_id: UUID):
        return UserRepository.get_by_id(user_id)

    @staticmethod
    def search_users(keyword: str | None, page: int):
        return UserRepository.search(keyword, page)

    @staticmethod
    def update_user(user_id: UUID, data: dict):
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None
        return UserRepository.update(user, data)

    @staticmethod
    def delete_user(user_id: UUID):
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False
        UserRepository.delete(user)
        return True
