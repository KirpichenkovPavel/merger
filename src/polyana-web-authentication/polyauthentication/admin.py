from django import forms
from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Permission
from polyauthentication.models import PolyUser

from django.utils.translation import ugettext as _


class PolyUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    error_messages = {
        'duplicate_username': _(u"Пользователь с указанным именем уже зарегистрирован в системе"),
        'duplicate_email': _(u"Пользователь с указанным адресом электронной почты уже зарегистрирован в системе"),
        'password_mismatch': _(u"Пароль не совпадает с подтверждением"),
    }

    password1 = forms.CharField(label=_(u'Пароль'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_(u'Подтверждение пароля'), widget=forms.PasswordInput)

    class Meta:
        model = PolyUser
        fields = ('username', 'password', 'first_name', 'middle_name', 'last_name',
                  'email', 'is_active')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'])
        return password2

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            PolyUser.objects.get(username=username)
        except PolyUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            PolyUser.objects.get(email=email)
        except PolyUser.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(PolyUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PolyUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = PolyUser
        fields = ('username', 'password', 'first_name', 'middle_name', 'last_name',
                  'email', 'is_active')

    def __init__(self, *args, **kwargs):
        super(PolyUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class PolyUserAdmin(UserAdmin):
    # The forms to add and change experts user instances
    form = PolyUserChangeForm
    add_form = PolyUserCreationForm

    # The fields to be used in displaying the ExpertsUser model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'first_name', 'middle_name', 'last_name', 'email', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'middle_name', 'last_name', 'email',)}),
        (_('Permissions'), {'fields': ('is_superuser', 'groups', 'user_permissions')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'middle_name', 'last_name',
                       'email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Now register the ExpertsUserAdmin...
admin.site.register(PolyUser, PolyUserAdmin)
