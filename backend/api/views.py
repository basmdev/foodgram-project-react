from io import BytesIO

from django.db.models import Count, Exists, OuterRef
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from api.filters import CustomRecipeFilter
from api.pagination import CustomPaginator
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (
    CreateRecipeSerializer,
    ShowRecipeSerializer,
    ShowSubscriptionsSerializer,
    UserSerializer,
)
from users.models import Follow, User
from recipes.models import Favorite, IngredientRecipe, Recipe, ShoppingCart


class UserViewSet(UserViewSet):
    """Вьюсет модели User."""

    serializer_class = UserSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, id=self.request.user.id)
        is_subscribed = Follow.objects.filter(user=user, author=OuterRef("id"))
        return User.objects.annotate(is_subscribed=Exists(is_subscribed))

    @action(detail=True, methods=["POST", "DELETE"])
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=author_id)

        if request.method == "POST":
            serializer = ShowSubscriptionsSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            subscription = get_object_or_404(Follow, user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user).prefetch_related(
            "recipes"
        )
        pages = self.paginate_queryset(queryset)
        serializer = ShowSubscriptionsSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""

    serializer_class = CreateRecipeSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly or IsAdminOrReadOnly,
    ]
    pagination_class = CustomPaginator
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = CustomRecipeFilter

    def get_queryset(self):
        user = self.request.user
        if not user.is_anonymous:
            is_favorited = Favorite.objects.filter(
                user=user, recipe=OuterRef("id")
            )
            is_in_shopping_cart = ShoppingCart.objects.filter(
                user=user, recipe=OuterRef("id")
            )
            return (
                Recipe.objects.select_related("author", "tags")
                .prefetch_related("ingredients")
                .annotate(
                    is_favorited=Exists(is_favorited),
                    is_in_shopping_cart=Exists(is_in_shopping_cart),
                    recipes_count=Count("author__recipes"),
                )
            )
        return Recipe.objects.select_related(
            "author", "tags"
        ).prefetch_related("ingredients")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ShowRecipeSerializer
        return CreateRecipeSerializer

    @action(
        detail=False, methods=["GET"], permission_classes=[IsAuthenticated]
    )
    def generate_shopping_list_pdf(self, recipe):
        final_list = {}
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_list__user=self.request.user,
            recipe=recipe,
        ).values_list(
            "ingredient__name", "ingredient__measurement_unit", "amount"
        )
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    "measurement_unit": item[1],
                    "amount": item[2],
                }
            else:
                final_list[name]["amount"] += item[2]
        return final_list

    def create_shopping_list_pdf(self, recipe):
        final_list = self.generate_shopping_list_pdf(recipe)
        buffer = BytesIO()
        page = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont("FreeSans", "../fonts/FreeSans.ttf"))
        page.setFont("FreeSans", 20)
        page.drawString(200, 800, "Список покупок")
        page.setFont("FreeSans", 16)
        height = 700
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(
                75,
                height,
                (
                    f'{i}. {name} - {data["amount"]} '
                    f'{data["measurement_unit"]}'
                ),
            )
            height -= 25
        page.showPage()
        page.save()
        buffer.seek(0)
        return buffer

    @action(
        detail=False, methods=["GET"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        try:
            recipe_id = request.query_params.get("recipe_id", None)
            if recipe_id:
                recipe = Recipe.objects.get(pk=recipe_id)
            else:
                recipe = Recipe.objects.filter(author=request.user).first()
        except ObjectDoesNotExist:
            return HttpResponse("Recipe not found.", status=404)

        buffer = self.create_shopping_list_pdf(recipe)

        response = HttpResponse(
            buffer.getvalue(), content_type="application/pdf"
        )
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_list.pdf"'
        return response
