from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_OPTIONS = (
    ("S","STRIPE"),
    ("P","PAYPAL")
)



class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False,)
    shipping_country = CountryField(required=False,blank_label='select country').formfield(widget=CountrySelectWidget(attrs={
        "class":"form-control custom-select d-block W-100"
    }))
    shipping_zip = forms.CharField(required=False)
    same_shipping_address = forms.BooleanField(widget=forms.CheckboxInput(),required=False)
    set_default_shipping = forms.BooleanField()
    save_info = forms.BooleanField(widget=forms.CheckboxInput(),required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect,choices=PAYMENT_OPTIONS)
    

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'Promo Code',
        'aria-label':"Recipient's username",
        'aria-describedby':"basic-addon2"
    }))

class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows':4
    }))
    email = forms.EmailField()