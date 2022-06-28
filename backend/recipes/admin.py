from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        # "id"
        "username",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = ('username',)
    # list_editable = ('username',)
    # list_filter = ('username',)
    # list_display_links = ('id', 'name')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
