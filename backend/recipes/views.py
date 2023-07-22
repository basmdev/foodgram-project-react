from rest_framework import status, viewsets
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from api.filters import CustomIngredientFilter
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    ShoppingCart,
    Tag,
)


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
        self.model.objects.filter(
            user=request.user.id, recipe=favorite
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(FavoritesShoppingCartBasicViewSet):
    """Вьюсет модели избранного."""

    queryset = Favorite.objects.select_related("author", "recipes")
    serializer_class = FavoriteSerializer
    model = Favorite


class ShoppingCartViewSet(FavoritesShoppingCartBasicViewSet):
    """Вьюсет списка покупок."""

    queryset = ShoppingCart.objects.select_related("author", "recipes")
    serializer_class = ShoppingCartSerializer
    model = ShoppingCart
