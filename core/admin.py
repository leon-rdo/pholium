from django.contrib import admin
from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "language", "created_at", "updated_at")
    search_fields = ("name", "slug", "language")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
