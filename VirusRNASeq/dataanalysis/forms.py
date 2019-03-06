from django import forms
from .models import Data
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


class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ('file', )
