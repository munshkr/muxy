from django import forms

from events.models import StreamingService


class StreamingServiceForm(forms.ModelForm):
    class Meta:
        model = StreamingService
        fields = '__all__'
        widgets = {
            'key': forms.PasswordInput(),
        }
