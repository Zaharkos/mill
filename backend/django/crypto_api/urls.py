from django.urls import path
from .views import FileGenerateKeyView, FileEncryptView, FileDecryptView

urlpatterns = [
    path('gen-key/', FileGenerateKeyView.as_view(), name='file-generate-key'),
    path('encrypt/', FileEncryptView.as_view(), name='file-encrypt'),
    path('decrypt/', FileDecryptView.as_view(), name='file-decrypt')
]
