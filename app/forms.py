from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth import password_validation

class RegistrationForm(UserCreationForm):
	def __init__(self, *args, **kwargs):
		super(RegistrationForm, self).__init__(*args, **kwargs)
		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['class'] = 'form-control'
	# username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-label'}))
	email = forms.EmailField(required=True, widget=forms.EmailInput(
		attrs={'class': 'form-control'}))

	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('Email address already exists.')
		return email

	class Meta:
		model = User
		fields = ['username', 'email', 'first_name',
				  'last_name', 'password1', 'password2']
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control'}),
			'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control'}),
			'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
		}


class UserLoginForm(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super(UserLoginForm, self).__init__(*args, **kwargs)

	username = forms.CharField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'Type your Username or Email'}),
		label="Username or Email")

	password = forms.CharField(widget=forms.PasswordInput(
		attrs={'class': 'form-control', 'placeholder': 'Type Your passowrd'}))

	# captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

class MyPasswordChangeForm(PasswordChangeForm):
	old_password = forms.CharField(label = ("Old Password"), strip = False, widget = forms.PasswordInput(attrs={'autocomplete': 'current-password','autofocus':True,'class':'form-control'}))
	new_password1 = forms.CharField(label = ("New Password"), strip = False, widget = forms.PasswordInput(attrs={'autocomplete': 'current-password','autofocus':True,'class':'form-control'}),help_text=password_validation.password_validators_help_text_html())
	new_password2 = forms.CharField(label = ("Confirm New Password"), strip = False, widget = forms.PasswordInput(attrs={'autocomplete': 'current-password','autofocus':True,'class':'form-control'}))