from django.shortcuts import render
from .forms import QRCodeForm
from PIL import Image
from pyzbar.pyzbar import decode
from .mongoDB_methods import *


async def get_qr_info(request):
    
    qr_data = None
    message = None
    qr_code_image = None

    try:
        if request.method == 'POST':

            form = QRCodeForm(request.POST, request.FILES)

            if form.is_valid():

                qr_code_image = await sync_to_async(Image.open)(form.cleaned_data['qr_code_image'])
                decoded_objects = await sync_to_async(decode)(qr_code_image)

                if decoded_objects:
                    qr_data = await sync_to_async(decoded_objects[0].data.decode)('utf-8')

                    parts = qr_data.split('|')
                    
                    qr_fields = {
                        'products_id': parts[0],
                        'batch_id': parts[1],
                        'package_id': parts[2],
                        'expiration_date_1': parts[3],
                        'expiration_date_2': parts[4],
                        'status': parts[5],
                    }

                    products_id = qr_fields['products_id']
                    batch_id = qr_fields['batch_id']
                    package_id = qr_fields['package_id']
                    expiration_date_1 = qr_fields['expiration_date_1']
                    expiration_date_2 = qr_fields['expiration_date_2']
                    status = qr_fields['status']
              
                    package_info = []
                    package_info = await GetPackageInfo(products_id, batch_id, package_id, expiration_date_1, expiration_date_2, status)
                
                    message = "QR-код успішно зчитано!"
                    return await sync_to_async(render)(request, 'index.html', {'form': form, 'message': message, 'package_info': package_info})

                else:
                    message = "Помилка при зчитуванні QR-коду."
                    return await sync_to_async(render)(request, 'index.html', {'form': form, 'message': message})
            else:
                message = f"Невалідна форма! Перевірте коректність введених даних."
                return await sync_to_async(render)(request, 'index.html', {'form': form, 'message': message})

        else:
            form = QRCodeForm()
            message = "При обробці запиту виникла помилка."
            return await sync_to_async(render)(request, 'index.html', {'form': form, 'message': message})

    except Exception as e:
        message = e
        return await sync_to_async(render)(request, 'index.html', {'form': form, 'message': message})