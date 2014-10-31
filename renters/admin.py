
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from room_scheduler.renters.models import Renter


admin.site.unregister(User)

class RenterOptionsInline(admin.StackedInline):
    template = 'admin/renters/edit_inline/stacked.html'
    model = Renter
    extra = 1
    fieldsets = (
        ('Personal Information', {'fields': ('first_name', 'last_name')}),
        ('Contact Information', {'fields': ('email', 'home_phone_number', 'mobile_phone_number')} ),
        ('Account Information', {'fields': ('account_expires', 'flexible_renter', 'permitted_rentals_per_month', 'extra_credits', 'can_see_days_ahead', 'contact_info_visible')})
        )

class RenterAdmin(UserAdmin):
    fieldsets = (
        ('Authentication', {'fields': ('username', 'password', 'is_staff', 'is_superuser')}),
        )
    inlines = [RenterOptionsInline]

    
admin.site.register(User, RenterAdmin)

