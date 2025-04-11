from django.urls import path
from .views import FileEncryptView, FileDecryptView

urlpatterns = [
    path('encrypt/', FileEncryptView.as_view(), name='file-encrypt'),
    path('decrypt/', FileDecryptView.as_view(), name='file-decrypt'),
]
