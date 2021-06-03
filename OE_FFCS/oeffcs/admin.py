from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Timetable, Entry
from nested_inline.admin import NestedStackedInline, NestedModelAdmin


class EntryInLine(NestedStackedInline):
    model = Entry
    fk_name='level'


class TimetableInline(NestedStackedInline):
    model = Timetable
    fk_name='level'
    inlines=(EntryInLine,)


class ProfileAdmin(NestedModelAdmin):
    model = Profile
    inlines=(TimetableInline,)


class ProfileInLine(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInLine,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin) # This thing doesn't work yet. Might remove later.