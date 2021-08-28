from django.contrib import admin

from .models import User, Post, Follower

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "password")

class FollowerAdmin(admin.ModelAdmin):
    list_display = ("follower", "follows")

class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content", "timestamp")

admin.site.register(User, UserAdmin)
admin.site.register(Follower, FollowerAdmin)
admin.site.register(Post, PostAdmin)
