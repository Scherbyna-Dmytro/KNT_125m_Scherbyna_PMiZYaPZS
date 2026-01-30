from django import forms

class LoginForm(forms.Form):

    login = forms.CharField(
        widget = forms.TextInput(),
        max_length = 10,
        required = True,
        error_messages = {'required': 'Поле обов\'язкове',
                        'max_length': 'Максимальна довжина поля 10 символів'}
    )

    password = forms.CharField(
        widget = forms.PasswordInput(),
        max_length = 20,
        required = True,
        error_messages = {'required': 'Поле обов\'язкове',
                        'max_length': 'Максимальна довжина поля 20 символів'}
    )



class RegistrationForm(forms.Form):

    login = forms.CharField(
        widget = forms.TextInput(),
        max_length = 10,
        min_length = 4,
        required = True,
        error_messages = {'required': 'Поле обов\'язкове',
                          'min_length': 'Мінімальна довжина поля 4 символи',
                        'max_length': 'Максимальна довжина поля 10 символів',}
    )

    address = forms.CharField(
        widget = forms.TextInput(),
        max_length = 150,
        min_length = 25,
        required = True,
        error_messages = {'required': 'Поле обов\'язкове',
                          'min_length': 'Мінімальна довжина поля 25 символів',
                        'max_length': 'Максимальна довжина поля 150 символів',}
    )

    password = forms.CharField(
        widget = forms.PasswordInput(),
        max_length = 20,
        min_length = 8,
        required = True,
        error_messages = {'required': 'Поле обов\'язкове',
                          'min_length': 'Мінімальна довжина поля 8 символів',
                        'max_length': 'Максимальна довжина поля 20 символів',}
    )



class NewProductForm(forms.Form):

    product = forms.CharField(
        widget = forms.TextInput(),
        min_length = 3,
        max_length = 100,
        required = True,
        error_messages = {'required': 'Поле обов\'язкове',
                        'max_length': 'Максимальна довжина поля 100 символів',
                        'min_length': 'Мінімальна довжина поля 3 символи'}
    )

    manufacturer = forms.CharField(
        widget = forms.TextInput(),
        min_length = 3,
        max_length = 100,
        required = True,
        error_messages = {'required': 'Поле обов\'язкове',
                        'max_length': 'Максимальна довжина поля 100 символів',
                        'min_length': 'Мінімальна довжина поля 3 символи'}
    )



class NewBatchForm(forms.Form):

    product_id = forms.ChoiceField(
        required = True,
        error_messages = {'required': 'Поле обов\'язкове'}
    )

    login = forms.ChoiceField(
        required = True,
        error_messages = {'required': 'Поле обов\'язкове'}
    )

    package_size = forms.CharField(
        widget = forms.TextInput(),
        min_length = 5,
        max_length = 25,
        required = True,
        error_messages = {'required': 'Поле обов\'язкове',
                        'min_length': 'Мінімальна довжина поля 5 символів',
                        'max_length': 'Максимальна довжина поля 25 символів'}
    )

    expiration_date_1 = forms.DateField(
        widget = forms.SelectDateWidget(attrs={'type': 'date'}),
        required = True,
        error_messages = {'required': 'Поле обов\'язкове'}
    )

    expiration_date_2 = forms.DateField(
        widget = forms.SelectDateWidget(attrs={'type': 'date'}),
        required = True,
        error_messages = {'required': 'Поле обов\'язкове'}
    )

    number_of_packages = forms.IntegerField(
        widget = forms.NumberInput(),
        min_value = 1,
        max_value = 10,
        required = True,
        error_messages = {'required': 'Поле обов\'язкове',
                        'max_value': 'Максимальна кількість упаковок - 10',
                        'min_value': 'Мінімальна кількість упаковок - 1'}
    )

    def __init__(self, *args, products = [], users = [], **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['product_id'].choices = [
            (p['id'], f"{p['product_name']} - {p['manufacturer_name']}")
            for p in products
        ]

        self.fields['login'].choices = [
            (u['id'], u['address'])
            for u in users
        ]



class NewStatusForm(forms.Form):

    selected_status = forms.ChoiceField(
        required = True,
        error_messages = {'required': 'Вибір обов\'язковий',
                          'invalid_choice': 'Будь ласка, виберіть дійсний статус'}
    )

    def __init__(self, *args, **kwargs):

        current_status = kwargs.pop('current_status', None)

        super().__init__(*args, **kwargs)

        if current_status:
            if current_status == "Active":

                statuses_collection = ["Active", "Supplied", "Expired", "Withdrawn", "Destroyed"]

                statuses_collection.remove(current_status)

                self.fields['selected_status'].choices = [
                    (item, item)
                    for item in statuses_collection
                ]

            elif current_status == "Supplied":

                statuses_collection = ["Active"]

                self.fields['selected_status'].choices = [
                    (item, item)
                    for item in statuses_collection
                ]