from django.test import TestCase
from django.urls import reverse_lazy
from myappmedicine.forms import *
from myappmedicine.mongoDB_models import *
from myappmedicine.mongoDB_methods import *
from asgiref.sync import async_to_sync


class TestCalls(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        db = get_db()

        async_to_sync(AddUser)("admin", "admin", "address123address123address123")
        async_to_sync(AddUser)("user1", "user1111", "address_user1111_address_user1111")

        async_to_sync(AddProduct)("Парацетамол", "Виробник_1")

    def setUp(self):

        session = self.client.session
        session['user_data'] = {
             'id': "694d257f41c80f1a97a92a2b",
             'role': True,
             'address': "user.address_user.address_user.address",
            }
        
        session.save()
    
    def tearDown(self):

        self.client.session.flush()
    
    @classmethod
    def tearDownClass(cls):
        
        db = get_db()
        db.client.drop_database(db.name)

        super().tearDownClass()



    def test_login_correct(self):

        path = str(reverse_lazy('login_page'))

        form_data = {
            'login': "admin",
            'password': "admin",
        }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 302)

    def test_login_incorrect(self):

        path = str(reverse_lazy('login_page'))

        form_data = {
            'login': "admin",
            'password': "admin_123",
        }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Невірний логін або пароль")

    def test_login_incorrect_2(self):

        path = str(reverse_lazy('login_page'))

        form_data = {
            'login': "loginloginlogin",
            'password': "123456789012345678901234567890",
        }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']

        self.assertEqual(response.context['message'], "Невалідні дані!")
        self.assertFormError(form, "login", 'Максимальна довжина поля 10 символів')
        self.assertFormError(form, "password", 'Максимальна довжина поля 20 символів')



    def test_reg_user_correct(self):

        path = str(reverse_lazy('reg_user'))

        form_data = {
            'login': "user3",
            'password': "user3333",
            'address': "address_user3333_address_user3333",
        }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Користувача зареєстровано!")

    def test_reg_user_duplicate(self):

        path = str(reverse_lazy('reg_user'))

        form_data = {
            'login': "user1",
            'password': "user1111",
            'address': "address_user1111_address_user1111",
        }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Помилка. Вже існує користувач, що належить до вказаної мед. установи.")

    def test_reg_user_incorrect(self):

        path = str(reverse_lazy('reg_user'))

        form_data = {
            'login': "user3_user3_user3",
            'address': "address",
        }

        response = self.client.post(path, form_data)
        form = response.context['form']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Невалідна форма! Будь-ласка, перевірте коректність введених даних.")
        self.assertFormError(form, "login", 'Максимальна довжина поля 10 символів')
        self.assertFormError(form, "password", 'Поле обов\'язкове')
        self.assertFormError(form, "address", 'Мінімальна довжина поля 25 символів')
    


    def test_add_product_correct(self):

        path = str(reverse_lazy('add_product'))

        form_data = {
            'product': "Product_1",
            'manufacturer': "Manufacturer_1",
        }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Новий товар зареєстровано!")

    def test_add_product_duplicate(self):

        path = str(reverse_lazy('add_product'))

        form_data = {
            'product': "Парацетамол",
            'manufacturer': "Виробник_1",
        }

        response = self.client.post(path, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Помилка. Такий продукт вже існує.")

    def test_add_product_incorrect(self):

        path = str(reverse_lazy('add_product'))

        form_data = {
            'product': 'A' * 101,
            'manufacturer': "M1",
        }

        response = self.client.post(path, form_data)
        form = response.context['form']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], "Невалідна форма! Будь-ласка, перевірте коректність введених даних.")
        self.assertFormError(form, "product", 'Максимальна довжина поля 100 символів')
        self.assertFormError(form, "manufacturer", 'Мінімальна довжина поля 3 символи')








    # def test_call_view_fails_incorrect(self):

    #     qr_code_image = SimpleUploadedFile(
    #         name="badfile.pdf",
    #         content="Помилковий файл".encode('utf-8'),
    #         content_type='application/pdf'
    #     )

    #     qr_code_params = {

    #         'qr_code_image': qr_code_image,
    #     }

    #     path = str(reverse_lazy(self.get_info_url))

    #     response = self.client.post(path, qr_code_params)

    #     print(response.context['message'], file = sys.stderr)

    #     self.assertEqual(response.context['message'], "Невалідна форма! Перевірте коректність введених даних.")



    # def test_call_view_succeed(self):

    #     products = GetProducts()

    #     AddBatch(products[0].product_id, "user1", "3пл. * 10т.", datetime.date(2025, 12, 16), datetime.date(2028, 12, 16), 5)
    #     AddBatch(products[1].product_id, "user2", "2пл. * 10т.", datetime.date(2025, 12, 24), datetime.date(2028, 12, 24), 5)
    #     AddBatch(products[2].product_id, "user1", "3пл. * 10т.", datetime.date(2025, 11, 3), datetime.date(2028, 11, 3), 5)

    #     products = GetListProducts("admin", True)

    #     product = products[0]

    #     ChangeStatusForPackage(product["package_id"], product["batch_id"], product["product_id"], product["expiration_date_1"], product["expiration_date_2"], "Expired")

    #     package = Package.objects(status = "Expired").first()

    #     with open(package.qr_code_path, 'rb') as f:
    #          qr_code_image = SimpleUploadedFile(
    #              name=f.name.split('/')[-1],
    #              content=f.read(),
    #              content_type='image/png'
    #         )

    #     qr_code_params = {

    #         'qr_code_image': qr_code_image,
    #     }

    #     path = str(reverse_lazy(self.get_info_url))

    #     response = self.client.post(path, qr_code_params)

    #     self.assertEqual(response.status_code, 200)

    #     self.assertIn('message', response.context)
    #     self.assertEqual(response.context['message'], "QR-код успішно зчитано!")

    #     self.assertIn('package_info', response.context)
    #     self.assertEqual(response.context['package_info']['product_name'], "Парацетамол")
    #     self.assertEqual(response.context['package_info']['manufacturer_name'], "Производитель_1")
    #     self.assertEqual(response.context['package_info']['status'], "Expired")