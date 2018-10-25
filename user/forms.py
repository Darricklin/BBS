from django import forms

from user.models import User


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'password', 'age', 'sex', 'icon']

    password2 = forms.CharField(max_length=128)

    def clean_password2(self):
        '''检查两次输入的密码是否一致'''
        cleaned_data = super().clean()
        if cleaned_data['password'] != cleaned_data['password2']:
            raise forms.ValidationError('两次输入的密码不一致')
