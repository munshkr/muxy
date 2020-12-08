from django import forms
from django.core.exceptions import ValidationError

from events.models import Stream


class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        starts_at = cleaned_data.get("starts_at")
        ends_at = cleaned_data.get("ends_at")
        event = cleaned_data.get("event")

        if event:
            if starts_at < event.starts_at:
                raise ValidationError(
                    "Stream starts earlier than event itself")
            if ends_at > event.ends_at:
                raise ValidationError("Stream ends later than event itself")
