import datetime
from django.conf import settings
from django.contrib import admin
from .models import LazyUser


@admin.register(LazyUser)
class LazyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'created',)
    actions = ('cleanup_lazyusers',)

    def cleanup_lazyusers(self, request, queryset):
        delete_before = datetime.datetime.now() - datetime.timedelta(
            seconds=settings.SESSION_COOKIE_AGE)
        old_users = queryset.filter(user__last_login__lt=delete_before)
        count = old_users.count()

        for lazy_user in old_users:
            # iterate so any .delete() methods get called and signals are sent
            lazy_user.user.delete()

        self.message_user(request, "{0} Lazy Users deleted." .format(count))

    cleanup_lazyusers.short_description = (
        'Delete selected lazy users and unconverted users older than {}'.format(
            datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE)
        )
    )
