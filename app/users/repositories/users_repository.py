from django.core.paginator import Paginator
from app.users.models import User


class UserRepository:

    @staticmethod
    def create(data: dict) -> User:
        return User.objects.create(**data)

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        return User.objects.filter(id=user_id).first()

    @staticmethod
    def search(search: str | None, page: int, page_size: int = 10):
        queryset = User.objects.all().order_by("-created_at")

        if search:
            queryset = queryset.filter(name__icontains=search)

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        return {
            "results": list(page_obj),
            "total": paginator.count,
            "pages": paginator.num_pages,
            "current_page": page_obj.number,
        }

    @staticmethod
    def update(user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        return user

    @staticmethod
    def delete(user: User):
        user.delete()