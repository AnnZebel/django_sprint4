from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_editable = (
        'category',
        'is_published'
    )
    search_fields = ('title',)
    ordering = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'is_published',
    )
    search_fields = ('title',)
    ordering = ('title',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
    )
    search_fields = ('name',)
    ordering = ('name',)
    list_display_links = ('name',)
