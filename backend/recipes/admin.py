from django.contrib import admin

from .models import Tag, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        # "id"
        "username",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color")
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(User, UserAdmin)
admin.site.register(Tag, TagAdmin)
