# FOODGRAMM


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
- api/users/{id}/subscribe/ - GET, DELETE - подписка и удаление юзера из пидписок
#### Tags:
- api/tags/ - GET
- api/tags/{id} - GET
- #### Ingredients:
- api/ingredients/ - GET
- api/ingredients/{id} - GET
#### Recipes:
- api/recipes/ - GET, POST
- api/recipes/{id} - GET, PATCH, DELETE
  


