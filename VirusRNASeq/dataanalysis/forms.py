from django import forms
from .models import Photo
from dataanalysis.models import Document, PairedEnd, SingleEnd

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', )


class PairedEndForm(forms.ModelForm):
    class Meta:
        model = PairedEnd
        fields = ('file1', 'file2',)

class SingleEndForm(forms.ModelForm):
    class Meta:
        model = SingleEnd
        fields = ('file1',)


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('file', )
