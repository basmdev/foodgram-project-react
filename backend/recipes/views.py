from django.db.models import Exists, OuterRef
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import CustomIngredientFilter, CustomRecipeFilter
from api.pagination import CustomPaginator
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer, FavoriteSerializer,
                             IngredientSerializer, ShoppingCartSerializer,
                             ShowRecipeSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет модели Ingredient."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [
        CustomIngredientFilter,
    ]
    search_fields = [
        "^name",
    ]


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
            is_favorited = Favorite.objects.filter(user=user, recipe=OuterRef("id"))
            is_in_shopping_cart = ShoppingCart.objects.filter(
                user=user, recipe=OuterRef("id")
            )
            return Recipe.objects.prefetch_related("ingredients").annotate(
                is_favorited=Exists(is_favorited),
                is_in_shopping_cart=Exists(is_in_shopping_cart),
            )
        return Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ShowRecipeSerializer
        return CreateRecipeSerializer

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Загрузка списка покупок в PDF."""
        final_list = {}
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).values_list("ingredient__name", "ingredient__measurement_unit", "amount")
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    "measurement_unit": item[1],
                    "amount": item[2],
                }
            else:
                final_list[name]["amount"] += item[2]
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="shopping_list.pdf"'
        page = canvas.Canvas(response)
        page.setFont("Helvetica", size=20)
        page.drawString(200, 800, "Список покупок")
        page.setFont("Helvetica", size=16)
        height = 700
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(
                75,
                height,
                (f'{i}. {name} - {data["amount"]} ' f'{data["measurement_unit"]}'),
            )
            height -= 25
        page.showPage()
        page.save()
        return response


class FavoritesShoppingCartBasicViewSet(viewsets.ModelViewSet):
    """Вьюсет для избранного и списка покупок."""

    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data_my = {"user": request.user.id, "recipe": kwargs.get("id")}
        serializer = self.get_serializer(data=data_my)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(serializer.validated_data)

    def delete(self, request, *args, **kwargs):
        favorite = kwargs.get("id")
        self.model.objects.filter(user=request.user.id, recipe=favorite).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(FavoritesShoppingCartBasicViewSet):
    """Вьюсет модели избранного."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    model = Favorite


class ShoppingCartViewSet(FavoritesShoppingCartBasicViewSet):
    """Вьюсет списка покупок."""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    model = ShoppingCart
