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
    def __init__(self,*args,**kwargs):
        self.project_name = kwargs.pop('project_name')
        self.analysis_code = kwargs.pop('analysis_code')
        self.email = kwargs.pop('email')
        print("@@@@@project_name: ", self.project_name)
        print("@@@@@analysis_code: ", self.analysis_code)
        print("@@@@@email: ", self.email)
        initial = kwargs.get('initial', {})
        initial['title'] = self.project_name + self.analysis_code
        initial['project_name'] = self.project_name
        initial['analysis_code'] = self.analysis_code
        initial['email'] = self.email
        kwargs['initial'] = initial
        print("@@@@@initial: ", initial)
        super(DataForm,self).__init__(*args,**kwargs)
    class Meta:
        model = Data
        fields = ('project_name', 'file',)
