import shutil
from django.test import TestCase
from django.urls import reverse_lazy
from qrcodeapp.forms import QRCodeForm
from qrcodeapp.mongoDB_models import *
from qrcodeapp.mongoDB_methods import *
import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from asgiref.sync import async_to_sync

def tearDownModule():
        
    db = get_db()
    db.client.drop_database(db.name)
        
    folder = FOLDER_FOR_CODES
    if os.path.exists(folder):
        shutil.rmtree(folder)
        os.makedirs(folder, exist_ok = True)

class TestCalls(TestCase):

    def test_call_view_loads(self):

        path = str(reverse_lazy('index'))

        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, '{}.html'.format('index'))
        

        path = str(reverse_lazy('get_qr_info'))

        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)

    def test_call_view_fails_blank(self):

        form = QRCodeForm(data={}, files={})

        self.assertFalse(form.is_valid())
        self.assertIn('qr_code_image', form.errors)
        self.assertEqual(
            form.errors['qr_code_image'][0],
            "QR-code є обов'язковим"
        )

    def test_call_view_fails_incorrect(self):

        qr_code_image = SimpleUploadedFile(
            name="badfile.pdf",
            content="Помилковий файл".encode('utf-8'),
            content_type='application/pdf'
        )

        qr_code_params = {

            'qr_code_image': qr_code_image,
        }

        path = str(reverse_lazy('get_qr_info'))

        response = self.client.post(path, qr_code_params)

        self.assertEqual(response.context['message'], "Невалідна форма! Перевірте коректність введених даних.")

    def test_call_view_succeed(self):

        db = get_db()

        async_to_sync(AddUser)("admin", "admin", "address123address123address123")
        async_to_sync(AddUser)("user1", "user1111", "address_user1111_address_user1111")

        async_to_sync(AddProduct)("Парацетамол", "Виробник_1")
        async_to_sync(AddProduct)("Пертусин", "Виробник_2")
        async_to_sync(AddProduct)("Аспирин", "Виробник_3")

        products = async_to_sync(GetProducts)()
        user = async_to_sync(SignIn)("admin", "admin")

        async_to_sync(AddBatch)(products[0].id, user.id, "3 * 10", datetime.date(2025, 12, 16), datetime.date(2028, 12, 16), 5)
        async_to_sync(AddBatch)(products[1].id, user.id, "2 * 10", datetime.date(2025, 12, 24), datetime.date(2028, 12, 24), 5)
        async_to_sync(AddBatch)(products[2].id, user.id, "3 * 10", datetime.date(2025, 11, 3), datetime.date(2028, 11, 3), 5)

        products = async_to_sync(GetListProducts)(user.id, True)
        product = products[0]

        async_to_sync(ChangeStatusForPackage)(product["package_id"], product["batch_id"], product["product_id"], product["expiration_date_1"], product["expiration_date_2"], "Expired")

        package = async_to_sync(TestFindPackage)("Expired")

        with open(package.qr_code_path, 'rb') as f:
             qr_code_image = SimpleUploadedFile(
                 name=f.name.split('/')[-1],
                 content=f.read(),
                 content_type='image/png'
            )

        qr_code_params = { 'qr_code_image': qr_code_image,}

        path = str(reverse_lazy('get_qr_info'))

        response = self.client.post(path, qr_code_params)

        self.assertEqual(response.status_code, 200)
        
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], "QR-код успішно зчитано!")

        self.assertIn('package_info', response.context)
        self.assertEqual(response.context['package_info']['product_name'], "Парацетамол")
        self.assertEqual(response.context['package_info']['manufacturer_name'], "Виробник_1")
        self.assertEqual(response.context['package_info']['status'], "Expired")