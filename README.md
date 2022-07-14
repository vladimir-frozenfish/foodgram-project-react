# FOODGRAMM

## Адреса сайта:
- http://51.250.109.6/
- http://51.250.109.6/admin/ (login: admin; password: 12345)
- http://51.250.109.6/api/docs/ 


- http://frozenfish.ddnsking.com/
- http://frozenfish.ddnsking.com/admin/
- http://frozenfish.ddnsking.com/api/docs/

### Приложения бэкенда:
- recipes - описание моделей
- api - взаимодействие с фронтендом

### Модели:
- User(AbstractUser)
- Tag
- Ingredient
- Recipe
- TagRecipe
- IngredientRecipe
- Subscribe
- FavoriteRecipe
- ShoppingCartRecipe

### Эндпоинты API:
#### Users:
- api/users/ - GET, POST
- api/users/{id} - GET, PATCH, DELETE
- api/auth/token/login/ - POST - полуение токена
- api/auth/token/logout/ - POST - удаление токена
- api/users/me/ - GET
- api/auth/set_password/ - POST
#### Subscribe
- api/auth/users/subscriptions/ - GET - список подписок на юзеров
- api/users/{id}/subscribe/ - POST, DELETE - подписка и удаление юзера из пидписок
#### Tags:
- api/tags/ - GET
- api/tags/{id} - GET
#### Ingredients:
- api/ingredients/ - GET
- api/ingredients/{id} - GET
#### Recipes:
- api/recipes/ - GET, POST
- api/recipes/{id} - GET, PATCH, DELETE
#### FavoriteRecipes:
- api/recipes/{id}/favorite - POST, DELETE - добавление текущим пользователем рецепта в избранное, удаление из избранного
#### Shopping_Cart:
- api/recipes/download_shopping_cart - GET - получение текстового файла со списком ингредиентов рецептов, добавленных в корзину
- api/recipes/{id}/shopping_cart - POST, DELETE - добавление текущим пользователем рецепта в корзину, удаление из корзины

#### Notes:
- при выводе рецептов доступна фльтрация по имени тэгов


