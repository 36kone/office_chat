from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.users.services.users_service import UserService
from app.users.serializers.users_serializer import (
    UserSerializer,
    UserCreateUpdateSerializer
)


class UserCreateView(APIView):

    def post(self, request):
        serializer = UserCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.create_user(serializer.validated_data)
        return Response(UserSerializer(user).data, status=201)


class UserDetailView(APIView):

    def get(self, request, user_id: int):
        user = UserService.get_user(user_id)
        if not user:
            return Response({"detail": "Not found"}, status=404)

        return Response(UserSerializer(user).data)

    def put(self, request, user_id: int):
        serializer = UserCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.update_user(user_id, serializer.validated_data)
        if not user:
            return Response({"detail": "Not found"}, status=404)

        return Response(UserSerializer(user).data)

    def delete(self, request, user_id: int):
        deleted = UserService.delete_user(user_id)
        if not deleted:
            return Response({"detail": "Not found"}, status=404)

        return Response(status=204)


class UserSearchView(APIView):

    def get(self, request):
        search = request.GET.get("search")
        page = int(request.GET.get("page", 1))

        result = UserService.search_users(search, page)

        serialized = UserSerializer(result["results"], many=True)

        return Response({
            "results": serialized.data,
            "total": result["total"],
            "pages": result["pages"],
            "current_page": result["current_page"],
        })