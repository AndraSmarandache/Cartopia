from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Product, Order, DeliveryMethod, UserProfile, Review


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
            ),
            Submit('submit', 'Register', css_class='btn btn-primary')
        )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'specifications', 'price', 'stock',
            'category', 'supplier', 'delivery_method', 'image', 'descriptive_pdf', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'specifications': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'delivery_method': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_descriptive_pdf(self):
        value = self.cleaned_data.get('descriptive_pdf')
        if value and not value.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Only PDF files are allowed for the descriptive document.')
        return value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'slug',
            'description',
            'specifications',
            Row(
                Column('price', css_class='form-group col-md-6 mb-0'),
                Column('stock', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column('supplier', css_class='form-group col-md-4 mb-0'),
                Column('delivery_method', css_class='form-group col-md-4 mb-0'),
            ),
            'image',
            'descriptive_pdf',
            'is_active',
            Submit('submit', 'Save', css_class='btn btn-primary')
        )


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'postal_code', 'delivery_method'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('phone', css_class='form-group col-md-6 mb-0'),
            ),
            'address',
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('postal_code', css_class='form-group col-md-6 mb-0'),
            ),
            'delivery_method',
            Submit('submit', 'Complete Order', css_class='btn btn-success btn-lg')
        )


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email")
    date_of_birth = forms.DateField(required=False, label="Date of Birth", widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'phone', 'address', 'city', 'postal_code', 'country', 'date_of_birth']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'profile_picture',
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
            ),
            'email',
            'phone',
            'date_of_birth',
            'address',
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('postal_code', css_class='form-group col-md-4 mb-0'),
                Column('country', css_class='form-group col-md-2 mb-0'),
            ),
            'bio',
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(choices=Review.RATING_CHOICES, attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your review...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'rating',
            'title',
            'comment',
            Submit('submit', 'Submit Review', css_class='btn btn-primary')
        )

