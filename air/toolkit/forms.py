from django import forms

class CategoryCreateForm(forms.Form):
    category_id = forms.IntegerField(min_value=1,
                                  widget=forms.TextInput(attrs={'class':'idField'}))
    startvalue = forms.FloatField(initial=.6,min_value=0.0,max_value=1.0,
                                  widget=forms.TextInput(attrs={'class':'floatField',
                                                                'maxlength':5,
                                                                'size':3}))
    threshold = forms.FloatField(initial=.4,min_value=0.0,max_value=1.0,
                                  widget=forms.TextInput(attrs={'class':'floatField',
                                                                'maxlength':5,
                                                                'size':3}))
    decayrate = forms.FloatField(initial=.3,min_value=0.0,max_value=1.0,
                                  widget=forms.TextInput(attrs={'class':'floatField',
                                                                'maxlength':5,
                                                                'size':3}))
