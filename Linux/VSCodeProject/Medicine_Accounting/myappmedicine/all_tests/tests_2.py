from django.test import TestCase
import shutil
from django.urls import reverse_lazy
from myappmedicine.forms import *
from myappmedicine.mongoDB_models import *
from myappmedicine.mongoDB_methods import *
import datetime
from asgiref.sync import async_to_sync
import os

class TestCalls_Statuses(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        folder = FOLDER_FOR_CODES
        if os.path.exists(folder):
            shutil.rmtree(folder)
            os.makedirs(folder, exist_ok = True)

    def setUp(self):

        db = get_db()

        async_to_sync(AddUser)("admin", "admin", "address123address123address123")
        async_to_sync(AddUser)("user1", "user1111", "address_user1111_address_user1111")
        async_to_sync(AddProduct)("Парацетамол", "Виробник_1")

        user = async_to_sync(SignIn)("user1", "user1111")
        products =  async_to_sync(GetProducts)()

        async_to_sync(AddBatch)(products[0].id, user.id, "500мл", datetime.date(2025, 12, 16), datetime.date(2028, 12, 16), 5)

        session = self.client.session
        session['user_data'] = {
             'id': str(user.id),
             'role': True,
             'address': "address123address123address123",
            }
        
        session.save()

    def tearDown(self):

        self.client.session.flush()

        db = get_db()
        db.client.drop_database(db.name)
    
    @classmethod
    def tearDownClass(cls):

        db = get_db()
        db.client.drop_database(db.name)

        super().tearDownClass()
    
    
    
    
    def test_add_batch_correct(self):

        path = str(reverse_lazy('add_batch'))

        products = async_to_sync(GetProducts)()

        users = async_to_sync(GetUsers)()

        form_data = {
            'product_id': products[0].id,
            'login': users[0].id,
            'package_size': "3пл. * 10т.",
            'expiration_date_1': datetime.date(2025, 12, 16),
            'expiration_date_2': datetime.date(2028, 12, 16),
            'number_of_packages': 5,
        }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Партію ліків додано!")

    def test_add_batch_incorrect(self):

        path = str(reverse_lazy('add_batch'))

        form_data = {
            'package_size': 'A' * 26,
            'number_of_packages': 15,
        }

        response = self.client.post(path, form_data)
        form = response.context['form']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Невалідна форма! Будь-ласка, перевірте коректність введених даних.")
        self.assertFormError(form, "product_id", 'Поле обов\'язкове')
        self.assertFormError(form, "login", 'Поле обов\'язкове')
        self.assertFormError(form, "package_size", 'Максимальна довжина поля 25 символів')
        self.assertFormError(form, "expiration_date_1", 'Поле обов\'язкове')
        self.assertFormError(form, "expiration_date_2", 'Поле обов\'язкове')
        self.assertFormError(form, "number_of_packages", 'Максимальна кількість упаковок - 10')



    def test_list_view_correct(self):

        path = str(reverse_lazy('list_view'))

        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        products_list = response.context['products_list']
        path = str(reverse_lazy('change_status_preview'))

        response = self.client.get(path, {'selected': products_list[0]['package_id']})
        self.assertEqual(response.status_code, 200)

        selected_id = response.context['selected_product']['package_id']

        self.assertEqual(selected_id, products_list[0]['package_id'])

    def test_list_view_incorrect(self):

        self.client.session.clear()
        session = self.client.session
        session['user_data'] = {
            'id': "694d257f41c80f1a97a92c3d",
            'role': False,
            'address': "admin.address_admin.address_admin.address",
        }  
        session.save()

        path = str(reverse_lazy('list_view'))
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        products_list = response.context['products_list']
        self.assertEqual(products_list, [])
        self.assertEqual(response.context['message'], "Помилка при обробці даних. Дані відсутні.")

        path = str(reverse_lazy('change_status_preview'))

        response = self.client.get(path, {'selected': "None"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_product'], None)
        self.assertEqual(response.context['message'], "Помилка при завантаженні сторінки.")



    def test_change_status_for_package_correct(self):

        path = str(reverse_lazy('list_view'))

        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        products_list = response.context['products_list']
        path = str(reverse_lazy('change_status_preview'))

        response = self.client.get(path, {'selected': products_list[0]['package_id']})
        self.assertEqual(response.status_code, 200)

        path = str(reverse_lazy('change_status_view'))
        form_data = {
            'selected_status': "Expired",
            'action': "package",
            }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['message'], "Статус упаковки успішно змінено!")

    def test_change_status_for_package_incorrect(self):

        path = str(reverse_lazy('list_view'))
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        products_list = response.context['products_list']

        path = str(reverse_lazy('change_status_preview'))
        response = self.client.get(path, {'selected': products_list[0]['package_id']})
        self.assertEqual(response.status_code, 200)

        path = str(reverse_lazy('change_status_view'))
        form_data = {
            'selected_status': "Expired",
            'action': "package",
            }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Статус упаковки успішно змінено!")

        form_data = {
            'selected_status': "Destroyed",
            'action': "package",
            }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Невалідні дані!")

    def test_change_status_for_package_incorrect_2(self):

        path = str(reverse_lazy('list_view'))
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        user_data = session.get('user_data', {})
        user_data['selected_product'] = {
            'package_id': '1111111',
            'batch_id': '1111111',
            'product_id': '1111111',
            'package_size': '1479283792',
            'expiration_date_1': '8192479127',
            'expiration_date_2': '16784268174',
            'status': "Active",
            'address': "iqwyriqwryi",
            'product_name': "yuiwfhiwfihi",
            'manufacturer_name': "fhaaqhfh32yr19",
        }
        session['user_data'] = user_data
        session.save()

        path = str(reverse_lazy('change_status_view'))
        form_data = {
            'selected_status': "Supplied",
            'action': "package",
            }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "При зміні статусу упаковки виникла помилка.")

        self.client.session.flush()



    def test_change_status_for_batch_correct(self):

        path = str(reverse_lazy('list_view'))

        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        products_list = response.context['products_list']
        path = str(reverse_lazy('change_status_preview'))

        response = self.client.get(path, {'selected': products_list[0]['package_id']})
        self.assertEqual(response.status_code, 200)

        path = str(reverse_lazy('change_status_view'))
        form_data = {
            'selected_status': "Expired",
            'action': "batch",
            }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['message'], "Статуси упаковок в партії успішно змінено!")

    def test_change_status_for_batch_incorrect(self):

        path = str(reverse_lazy('list_view'))

        self.client.session.clear()
        session = self.client.session
        session['user_data'] = {
            'login': "user0121",
            'role': False,
            'address': "admin.address_admin.address_admin.address",
        }  
        session.save()

        response = self.client.get(path)
        products_list = response.context['products_list']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(products_list, [])
        self.assertEqual(response.context['message'], "Помилка при обробці даних. Дані відсутні.")

    def test_change_status_for_batch_incorrect_2(self):

        path = str(reverse_lazy('list_view'))

        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        products_list = response.context['products_list']
        
        # user_data = self.client.session.get('user_data', {})
        # id = user_data.get('id') 
        # user_id = ObjectId(id)
        # role = user_data.get('role')

        #print(f"ID: {id}, User_id: {user_id}, Role: {role}", file=sys.stderr)

        path = str(reverse_lazy('change_status_preview'))
        response = self.client.get(path, {'selected': products_list[0]['package_id']})
        self.assertEqual(response.status_code, 200)


        path = str(reverse_lazy('change_status_view'))
        form_data = {
            'selected_status': "Supplied",
            'action': "package",
            }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Статус упаковки успішно змінено!")


        path = str(reverse_lazy('change_status_preview'))

        response = self.client.get(path, {'selected': products_list[1]['package_id']})
        self.assertEqual(response.status_code, 200)

        path = str(reverse_lazy('change_status_view'))
        form_data = {
             'selected_status': "Destroyed",
             'action': "batch",
            }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Для зміни статусу для упаковок усієї партії треба, щоб упаковки мали однаковий статус!")
    
    def test_change_status_for_batch_incorrect_3(self):

        path = str(reverse_lazy('list_view'))
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        user_data = session.get('user_data', {})
        user_data['selected_product'] = {
            'package_id': '1111111',
            'batch_id': '1111111',
            'product_id': '1111111',
            'package_size': '1479283792',
            'expiration_date_1': '8192479127',
            'expiration_date_2': '16784268174',
            'status': "Active",
            'address': "iqwyriqwryi",
            'product_name': "yuiwfhiwfihi",
            'manufacturer_name': "fhaaqhfh32yr19",
        }
        session['user_data'] = user_data
        session.save()

        path = str(reverse_lazy('change_status_view'))
        form_data = {
             'selected_status': "Destroyed",
             'action': "batch",
             }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "При зміні статусів упаковок в партії виникла помилка.")