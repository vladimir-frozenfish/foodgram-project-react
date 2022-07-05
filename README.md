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
- api/auth/users/me/ - GET <span style="color:red">(надо из пути убрать path)</span>
- api/auth/users/set_password/ - POST <span style="color:red">(надо из пути убрать path)</span>
#### Tags:
- api/tags/ - GET
- api/tags/{id} - GET
- #### Ingredients:
- api/ingredients/ - GET
- api/ingredients/{id} - GET
#### Recipes:
- api/recipes/ - GET, POST <span style="color:red">(при создании рецепта надо добавить ингредиенты и сохранение изображения и выдачу на него ссылки)</span>
- api/recipes/{id} - GET, PATCH, DELETE


