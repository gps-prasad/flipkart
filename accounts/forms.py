from django import forms
from .models import Account, UserProfile

class Registrationform(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password',
        'class':'form-control',
        }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm password',
        'class':'form-control',
        }))
    class Meta:
        model = Account
        fields = ('first_name','last_name','email','phone_number','password')
        
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
            
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']
        if password!=confirm_password:
            raise forms.ValidationError(
                "password doesn't matched",
            )

class UserForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] ='form-control'
    class Meta:
        model = Account
        fields = ('first_name','last_name','phone_number')

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid':{'image files only!'}},widget=forms.FileInput)
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] ='form-control'
            
    class Meta:
        model = UserProfile
        fields = ('address_line_1','address_line_2','city','state','country')
