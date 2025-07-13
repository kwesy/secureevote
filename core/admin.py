from django.contrib import admin
from .models.user import User
from .models.event import Event
from .models.candidate import Candidate

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'organization_name', 'is_active', 'is_staff')
    search_fields = ('email', 'organization_name')
    list_filter = ('is_active', 'is_staff')
    ordering = ('email',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'shortcode', 'user', 'amount_per_vote', 'is_active', 'is_blocked')
    search_fields = ('name', 'shortcode')
    list_filter = ('is_active', 'is_blocked')
    raw_id_fields = ('user',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'gender', 'vote_count', 'is_blocked')
    list_filter = ('gender', 'is_blocked')
    search_fields = ('name',)
    raw_id_fields = ('event',)
