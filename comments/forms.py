from django.forms import ModelForm
from .models import Kommentar
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage

class KommentarForm(ModelForm):

	def send_email(self):
		author_name = self.cleaned_data.get('author_name')
		author_email = self.cleaned_data.get('author_email')
		comment = self.cleaned_data.get('content')
		message = 'Ein neuer Kommentar wurde angelegt: ' + author_name + ' ' + \
		    author_email + ' (' + comment + ')'
		admin_users = User.objects.filter(is_superuser=True)
                receivers = []
		for user in admin_users:
			receivers.append(user.email)
		email = EmailMessage('Neuer Kommentar', message, settings.EMAIL_FROM, to=list(receivers))
		email.send()

	class Meta:
		model = Kommentar
		fields = ('author_name', 'author_email', 'author_url', 'content')





