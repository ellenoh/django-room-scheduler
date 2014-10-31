
from django.contrib import admin

from room_scheduler.timeslots.models import TimeSlot, TimeSlotHistory


class TimeSlotOptions(admin.ModelAdmin):
    ordering = ('date', 'start_time')

    def save_model(self, request, instance, form, change):
        try: 
            instance_before_change = TimeSlot.objects.get(pk=instance.pk)

            if not (instance_before_change.renter or instance.renter):
                super(TimeSlotOptions, self).save_model(request, instance, form, change)

            else:
                if instance.renter:
                    saved_for = instance.renter
                    reserved = True

                else:
                    saved_for = instance_before_change.renter
                    reserved = False

                history = TimeSlotHistory(saver=request.user.get_profile(),
                                  saved_for = saved_for,
                                  time_slot = instance,
                                  reserved = reserved,
                                  )
                history.save()
                super(TimeSlotOptions, self).save_model(request, instance, form, change)
            
        except:
            super(TimeSlotOptions, self).save_model(request, instance, form, change)

admin.site.register(TimeSlot, TimeSlotOptions)

