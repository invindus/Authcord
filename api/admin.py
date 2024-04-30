from django import forms
from django.contrib import admin

from . import models


class AuthorAdminForm(forms.ModelForm):
    class Meta:
        model = models.Author
        fields = "__all__"
    


class ServerAdmin(admin.ModelAdmin):
    form = AuthorAdminForm
    list_display = ["user", "is_approved"]
    list_filter = ["is_approved"]
    actions = ["approve_authors", "delete_authors"]

    @staticmethod
    def approve_authors(self, request, queryset):
        queryset.update(is_approved=True)

        # Override get_actions to replace the 'delete_selected' action

    def get_actions(self, request):
        # Get the default actions
        actions = super().get_actions(request)
        # Remove the 'delete_selected' action from the list of actions
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    @staticmethod
    def delete_authors(self, request, queryset):
        # Custom delete logic
        for obj in queryset:
            # This will delete the User and, because of the CASCADE, the Author too
            obj.user.delete()


admin.site.register(models.Author, ServerAdmin)
admin.site.register(models.Comment)
admin.site.register(models.Like)
admin.site.register(models.Node)
admin.site.register(models.Notification)
admin.site.register(models.Post)
