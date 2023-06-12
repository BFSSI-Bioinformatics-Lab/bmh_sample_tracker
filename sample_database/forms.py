from django import forms


class UploadForm(forms.Form):
    excel_file = forms.FileField(label="Excel File")
