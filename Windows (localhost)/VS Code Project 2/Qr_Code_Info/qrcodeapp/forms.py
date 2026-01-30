from django import forms

class QRCodeForm(forms.Form):
    qr_code_image = forms.ImageField(
        required = True,
        error_messages = {'required': "QR-code є обов'язковим",}
    )