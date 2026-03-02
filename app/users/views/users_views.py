from uuid import UUID

from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.views import APIView

from app.users.serializers.users_serializer import (
    UserCreateUpdateSerializer,
    UserSerializer,
)
from app.users.services.users_service import UserService


class UserCreateView(APIView):
    def post(self, request: HttpRequest):
        serializer = UserCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.create_user(serializer.validated_data)
        return Response(UserSerializer(user).data, status=201)


class UserDetailView(APIView):
    def get(self, request, user_id: UUID):
        user = UserService.get_user(user_id)
        if not user:
            return Response({"detail": "Not found"}, status=404)

        return Response(UserSerializer(user).data)

    def put(self, request: HttpRequest, user_id: UUID):
        serializer = UserCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.update_user(user_id, serializer.validated_data)
        if not user:
            return Response({"detail": "Not found"}, status=404)

        return Response(UserSerializer(user).data)

    def delete(self, request, user_id: UUID):
        deleted = UserService.delete_user(user_id)
        if not deleted:
            return Response({"detail": "Not found"}, status=404)

        return Response(status=204)


class UserSearchView(APIView):
    def get(self, request: HttpRequest):
        keyword = request.GET.get("keyword", None)
        page = int(request.GET.get("page", 1))

        result = UserService.search_users(keyword, page)

        serialized = UserSerializer(result["results"], many=True)

        return Response(
            {
                "results": serialized.data,
                "total": result["total"],
                "pages": result["pages"],
                "current_page": result["current_page"],
            }
        )
