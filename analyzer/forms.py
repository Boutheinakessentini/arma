from django import forms
class XMLUploadForm(forms.Form):
    xml_file = forms.FileField(label='Sélectionnez un fichier XML')