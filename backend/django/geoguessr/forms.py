from django import forms
from .models import RecognitionRequest, Photo

class RecognitionRequestForm(forms.ModelForm):
    photos = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
        label="Завантажити фото"
    )

    class Meta:
        model = RecognitionRequest
        fields = ['description', 'estimated_date', 'estimated_location', 'is_visible']

    def save(self, commit=True, provider=None):
        recognition_request = super().save(commit=False)
        if provider:
            recognition_request.provider = provider
        if commit:
            recognition_request.save()
            photos = self.files.getlist('photos')
            for photo_file in photos:
                Photo.objects.create(request=recognition_request, image=photo_file)
        return recognition_request
