from django.test import TestCase
from django.urls import reverse_lazy
from myappmedicine.forms import *
from myappmedicine.mongoDB_models import *
from myappmedicine.mongoDB_methods import *
import datetime

class TestCalls_Forms(TestCase):

    def test_call_view_loads(self):

        session = self.client.session

        session['user_data'] = {
             'id': "694d257f41c80f1a97a92a2b",
             'role': True,
             'address': "user.address_user.address_user.address",
            }
        
        session.save()

        self.templates_url = ['index', 'list_of_medicines', 'change_status', 'new_batch', 'reg', 'new_product']

        self.views_url = ['login_page', 'add_product', 'reg_user', 'add_batch_preview', 'add_batch', 'list_view', 'change_status_preview', 'change_status_view']

        for url in self.templates_url:

            path = str(reverse_lazy(url))

            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, '{}.html'.format(url))

            #print("Templates:", response.status_code, file=sys.stderr)

        for url in self.views_url:

            path = str(reverse_lazy(url))

            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)

           # print("Views:", response.status_code, file=sys.stderr)
        

        path = str(reverse_lazy('logout'))

        response = self.client.get(path)
        self.assertEqual(response.status_code, 302)

        #print("Logout:", response.status_code, file=sys.stderr)

        self.client.session.flush()

        self.views_url.remove('login_page')

        for url in self.views_url:

            path = str(reverse_lazy(url))

            response = self.client.get(path)
            self.assertEqual(response.status_code, 302)

            #print("Views_without_session:", response.status_code, file=sys.stderr)
    


    def test_login_form(self):

        form = LoginForm(data = {'login': 'A' * 11, 'password': 'A' * 21})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "login", 'Максимальна довжина поля 10 символів')
        self.assertFormError(form, "password", 'Максимальна довжина поля 20 символів')
    
    def test_login_form_2(self):

        form = LoginForm(data = {})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "login", 'Поле обов\'язкове')
        self.assertFormError(form, "password", 'Поле обов\'язкове')


    
    def test_reg_form(self):

        form = RegistrationForm(data = {'login': 'A' * 11, 'address': 'A' * 151,  'password': 'A' * 21})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "login", 'Максимальна довжина поля 10 символів')
        self.assertFormError(form, "address", 'Максимальна довжина поля 150 символів')
        self.assertFormError(form, "password", 'Максимальна довжина поля 20 символів')
    
    def test_reg_form_2(self):

        form = RegistrationForm(data = {'login': 'A' * 3, 'address': 'A' * 24,  'password': 'A' * 7})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "login", 'Мінімальна довжина поля 4 символи')
        self.assertFormError(form, "address", 'Мінімальна довжина поля 25 символів')
        self.assertFormError(form, "password", 'Мінімальна довжина поля 8 символів')

    def test_reg_form_3(self):

        form = RegistrationForm(data = {})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "login", 'Поле обов\'язкове')
        self.assertFormError(form, "address", 'Поле обов\'язкове')
        self.assertFormError(form, "password", 'Поле обов\'язкове')
    


    def test_new_product_form(self):

        form = NewProductForm(data = {'product': 'A' * 101, 'manufacturer': 'A' * 101})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "product", 'Максимальна довжина поля 100 символів')
        self.assertFormError(form, "manufacturer", 'Максимальна довжина поля 100 символів')
    
    def test_new_product_form_2(self):

        form = NewProductForm(data = {'product': 'A' * 2, 'manufacturer': 'A' * 2})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "product", 'Мінімальна довжина поля 3 символи')
        self.assertFormError(form, "manufacturer", 'Мінімальна довжина поля 3 символи')

    def test_new_product_form_3(self):

        form = NewProductForm(data = {})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "product", 'Поле обов\'язкове')
        self.assertFormError(form, "manufacturer", 'Поле обов\'язкове')
    
    
    
    async def test_new_batch_form(self):

        products = await GetProducts()
        users = await GetUsers() 

        form = NewBatchForm(products = products, users = users, data = {'product_id': 'A' * 101, 'login': 'A' * 101, 'package_size': 'A' * 26, 
                                      'expiration_date_1': datetime.date(2025, 12, 16), 'expiration_date_2': datetime.date(2025, 12, 16),
                                        'number_of_packages': 11,})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "package_size", 'Максимальна довжина поля 25 символів')
        self.assertFormError(form, "number_of_packages", 'Максимальна кількість упаковок - 10')
    
    async def test_new_batch_form_2(self):

        products = await GetProducts()
        users = await GetUsers() 

        form = NewBatchForm(products = products, users = users, data = {})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "product_id", 'Поле обов\'язкове')
        self.assertFormError(form, "login", 'Поле обов\'язкове')
        self.assertFormError(form, "package_size", 'Поле обов\'язкове')
        self.assertFormError(form, "expiration_date_1", 'Поле обов\'язкове')
        self.assertFormError(form, "expiration_date_2", 'Поле обов\'язкове')
        self.assertFormError(form, "number_of_packages", 'Поле обов\'язкове')
    


    def test_new_status_form(self):

        form = NewStatusForm(data = {})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "selected_status", 'Вибір обов\'язковий')
   
    def test_new_status_form_2(self):

        form = NewStatusForm(data = {'selected_status': 'A' * 10})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "selected_status", 'Будь ласка, виберіть дійсний статус')