import asyncio
import copy
from bson import ObjectId
from django.shortcuts import render, redirect
from .management.commands.mqtt_publish import *
from .forms import *
from .mongoDB_methods import *
from functools import wraps
from datetime import date, datetime, time

async def login_view(request):

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            login = form.cleaned_data['login']
            password = form.cleaned_data['password']

            user = await SignIn(login, password)

            if user:

                await sync_to_async(request.session.flush)()
                request.session['user_data'] = {
                    'id': str(user.id),
                    'role': user.isAdmin,
                    'address': user.address,
                }

                return await sync_to_async(redirect)('list_view')
            
            else:
                message = f"Невірний логін або пароль"

                return await sync_to_async(render)(request, 'index.html', {'form': form, 'message': message})
        else:
            message = "Невалідні дані!"

            return await sync_to_async(render)(request, "index.html", {"form": form, 'message': message})
    else:
        form = LoginForm()

    return await sync_to_async(render)(request, 'index.html', {'form': form})


def session_login_required(view_func):

    @wraps(view_func)
    async def async_wrapper(request, *args, **kwargs):
        user_data_exists = await sync_to_async(lambda: 'user_data' in request.session)()
        
        if not user_data_exists:
            return redirect('/login/')
            
        if asyncio.iscoroutinefunction(view_func):
            return await view_func(request, *args, **kwargs)
        else:
            return view_func(request, *args, **kwargs)

    def sync_wrapper(request, *args, **kwargs):
        if 'user_data' not in request.session:
            return redirect('/login/')
        return view_func(request, *args, **kwargs)

    if asyncio.iscoroutinefunction(view_func):
        return async_wrapper
    return sync_wrapper
    

@session_login_required
async def log_out_view(request):

    await sync_to_async(request.session.flush)()

    return await sync_to_async(redirect)('index')


@session_login_required
async def add_product_view(request):

    if request.method == 'POST':

        form = NewProductForm(request.POST)

        if form.is_valid():

            try:

                product = form.cleaned_data['product']
                manufacturer = form.cleaned_data['manufacturer']

                result = await publish_new_product(product, manufacturer)

                #if await AddProduct(product, manufacturer):
                if result == True:
            
                    message = "Новий товар зареєстровано!"
                    return await sync_to_async(render)(request, "new_product.html", {'form': form, "message": message})
                
                elif result == False:
                    
                    message = "Помилка. Такий продукт вже існує."
                    return await sync_to_async(render)(request, 'new_product.html', {'form': form, "message": message})
                
                else:
                    message = "Вичерпано час очікування відповіді від запиту."
                    return await sync_to_async(render)(request, "new_product.html", {'form': form, "message": message})

            except Exception as e:
                message = "Помилка при реєстрації товару. Будь-ласка, спробуйте ще раз."
                return await sync_to_async(render)(request, "new_product.html", {'form': form, "message": message})
            
        else:
            message = "Невалідна форма! Будь-ласка, перевірте коректність введених даних."
            return await sync_to_async(render)(request, "new_product.html", {'form': form, "message": message})

    else:
        form = NewProductForm()
        return await sync_to_async(render)(request, 'new_product.html', {'form': form})


@session_login_required
async def reg_user_view(request):

    if request.method == 'POST':

        form = RegistrationForm(request.POST)

        if form.is_valid():

            try:

                login = form.cleaned_data['login']
                password = form.cleaned_data['password']
                address = form.cleaned_data['address']

                result = await publish_new_user(login, password, address)

                #if await AddUser(login, password, address):
                if result == True:
            
                    message = "Користувача зареєстровано!"
                    return await sync_to_async(render)(request, "reg.html", {'form': form, "message": message})
                
                elif result == False:
                    
                    message = "Помилка. Вже існує користувач, що належить до вказаної мед. установи."
                    return await sync_to_async(render)(request, 'reg.html', {'form': form, "message": message})
                
                else:

                    message = "Вичерпано час очікування відповіді від запиту."
                    return await sync_to_async(render)(request, "reg.html", {'form': form, "message": message})  

            except:
                message = "Помилка при реєстрації користувача. Будь-ласка, спробуйте ще раз."
                return await sync_to_async(render)(request, "reg.html", {'form': form, "message": message})  
        
        else:
            message = "Невалідна форма! Будь-ласка, перевірте коректність введених даних."
            return await sync_to_async(render)(request, "reg.html", {'form': form, "message": message})

    else:
        form = RegistrationForm()
        return await sync_to_async(render)(request, 'reg.html', {'form': form})


@session_login_required
async def add_batch_preview(request):
    
    try:
        
        products = await GetProducts()
        users = await GetUsers()

        form = NewBatchForm(products = products, users = users) 
        
        return await sync_to_async(render)(request, "new_batch.html", {'form': form})
        
    except:
        message = "Помилка при завантаженні сторінки."
        return await sync_to_async(render)(request, "new_batch.html", {"message": message})


@session_login_required
async def add_batch_view(request):

    if request.method == 'POST':

        products = await GetProducts()
        users = await GetUsers()

        form = NewBatchForm(request.POST, products = products, users = users)

        if form.is_valid():

            try:

                product_id = form.cleaned_data['product_id']
                user_id = form.cleaned_data['login']
                package_size = form.cleaned_data['package_size']
                expiration_date_1 = form.cleaned_data['expiration_date_1']
                expiration_date_2 = form.cleaned_data['expiration_date_2']
                number_of_packages = form.cleaned_data['number_of_packages']



                result = await publish_new_batch(product_id, user_id, package_size, expiration_date_1.isoformat(), expiration_date_2.isoformat(), number_of_packages)
                #if await AddBatch(product_id, user_id, package_size, expiration_date_1, expiration_date_2, number_of_packages):

                if result == True:
            
                    message = "Партію ліків додано!"
                    return await sync_to_async(render)(request, "new_batch.html", {'form': form, "message": message})
                
                elif result == False:
                    
                    message = "При реєстрації партії виникла помилка."
                    return await sync_to_async(render)(request, 'new_batch.html', {'form': form, "message": message})
                
                else:

                    message = "Вичерпано час очікування відповіді від запиту."
                    return await sync_to_async(render)(request, 'new_batch.html', {'form': form, "message": message}) 
                
            except Exception as e:
                message = e#"Помилка. Будь-ласка, спробуйте ще раз."
                return await sync_to_async(render)(request, "new_batch.html", {'form': form, "message": message})
            
        else:
            message = "Невалідна форма! Будь-ласка, перевірте коректність введених даних."
            return await sync_to_async(render)(request, "new_batch.html", {'form': form, "message": message})

    else:
        form = NewBatchForm()

    return await sync_to_async(render)(request, 'new_batch.html', {'form': form})


@session_login_required
async def list_view(request):

    products_list = []

    try:
        
        user_data = request.session.get('user_data', {})
        id = user_data.get('id') 
        user_id = ObjectId(id)
        role = user_data.get('role')

        products_list_copy = []
        products_list = await GetListProducts(user_id, role) 

        products_list_copy = await sync_to_async(copy.deepcopy)(products_list)

        for item in products_list_copy:
            item['expiration_date_1'] = item['expiration_date_1'].date().strftime('%d.%m.%Y')
            item['expiration_date_2'] = item['expiration_date_2'].date().strftime('%d.%m.%Y')

        request.session['user_data']['products_list'] = products_list_copy
        request.session.modified = True
        
        if products_list:
            return await sync_to_async(render)(request, "list_of_medicines.html", {"products_list": products_list})
        
        else: 
            message = "Помилка при обробці даних. Дані відсутні."
            return await sync_to_async(render)(request, "list_of_medicines.html", {"products_list": products_list, "message": message})
        
    except:
        message = "Помилка при завантаженні сторінки."
        return await sync_to_async(render)(request, "list_of_medicines.html", {"products_list": products_list, "message": message})
    

@session_login_required
async def change_status_preview(request):

    try:
         
        selected_package_id = request.GET.get('selected')

        user_data = request.session.get('user_data', {})

        selected_product = None


        selected_product = next(
            (p for p in user_data.get('products_list', []) if str(p.get('package_id')) == str(selected_package_id)), None )

        if selected_product: 

            request.session['user_data']['selected_product'] = selected_product
            request.session.modified = True

            form = NewStatusForm(current_status = selected_product['status'])

            return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product})
        
        else: 
            form = NewStatusForm()
            message = "Помилка при завантаженні сторінки."
            return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
    
    except:
        form = NewStatusForm()
        message = "Помилка при обробці даних."
        return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
 

@session_login_required
async def change_status_view(request):

    try:

        message = ""

        if request.method == 'POST':

            user_data = request.session.get('user_data', {})
            selected_product = user_data.get('selected_product')

            form = NewStatusForm(request.POST, current_status = selected_product['status'])

            if form.is_valid():

                if selected_product:
                    
                    selected_package_id = selected_product['package_id']
                    selected_batch_id = selected_product['batch_id']
                    selected_product_id = selected_product['product_id']
                    selected_expiration_date_1 = selected_product['expiration_date_1']
                    selected_expiration_date_2 = selected_product['expiration_date_2']

                    new_status = form.cleaned_data['selected_status']

                    action = request.POST.get('action')

                    if action == 'package':
         
                        selected_product['status'] = new_status

                        result = await publish_change_status_for_package(selected_package_id, selected_batch_id, selected_product_id, 
                                                            selected_expiration_date_1, selected_expiration_date_2, new_status)

                        #res = await ChangeStatusForPackage(selected_package_id, selected_batch_id, selected_product_id, selected_expiration_date_1, selected_expiration_date_2, new_status)

                        if result == True:
                            products_list = user_data.get('products_list')

                            for product in products_list:
                                if product['package_id'] == selected_package_id:
                                    product['status'] = new_status
                                    break       

                            request.session['user_data']['selected_product'] = selected_product
                            request.session.modified = True

                            message = "Статус упаковки успішно змінено!"  
                            form = NewStatusForm(current_status = new_status) 
                            return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
                        
                        elif result == False:
                            form = NewStatusForm(current_status = selected_product['status']) 
                            message = "При зміні статусу упаковки виникла помилка."
                            return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
                        
                        else:
                            form = NewStatusForm(current_status = selected_product['status']) 
                            message = "Вичерпано час очікування відповіді від запиту."
                            return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
                        
                    elif action == 'batch':

                        products_list = user_data.get('products_list')
                    
                        if products_list and selected_product:  
                            
                            selected_batch_id = selected_product['batch_id']

                            batch_packages = [item for item in products_list if item['batch_id'] == selected_batch_id]

                            statuses = [item['status'] for item in batch_packages]

                            if len(set(statuses)) < 2:

                                result = await publish_change_status_for_batch(selected_batch_id, selected_product_id, 
                                                            selected_expiration_date_1, selected_expiration_date_2, new_status)

                                #res = await ChangeStatusForBatch(selected_batch_id, selected_product_id, selected_expiration_date_1, selected_expiration_date_2, new_status)
                                
                                if result == True:

                                    selected_product['status'] = new_status

                                    for item in products_list:
                                        if item['batch_id'] == selected_batch_id:
                                            item['status'] = new_status

                                    request.session['user_data']['selected_product'] = selected_product
                                    request.session['user_data']['products_list'] = products_list
                                    request.session.modified = True

                                    message = "Статуси упаковок в партії успішно змінено!"
                                    form = NewStatusForm(current_status = new_status)    
                                    return await sync_to_async(render)(request, "change_status.html", {'form': form,"selected_product": selected_product, "message": message})
                                
                                elif result == False:
                                    message = "При зміні статусів упаковок в партії виникла помилка."
                                    form = NewStatusForm(current_status = selected_product['status']) 
                                    return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
                                
                                else:
                                    message = "Вичерпано час очікування відповіді від запиту."
                                    form = NewStatusForm(current_status = selected_product['status']) 
                                    return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
                            else:
                                message = "Для зміни статусу для упаковок усієї партії треба, щоб упаковки мали однаковий статус!"
                                form = NewStatusForm(current_status = selected_product['status']) 
                                return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
                        else:
                            message = "Помилка при обробці даних."
                            form = NewStatusForm(current_status = selected_product['status']) 
                            return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
                else:
                    form = NewStatusForm(current_status = selected_product['status']) 
                    message = "Помилка при обробці даних."
                    return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product, "message": message})
            else:

                message = "Невалідні дані!"
                return await sync_to_async(render)(request, "change_status.html", {'form': form, "selected_product": selected_product,"message": message})

        else:
            message = "Проблеми з відправкою запиту. Спробуйте ще раз."
            form = NewStatusForm()

        return await sync_to_async(render)(request, 'change_status.html', {"form": form, "message": message})
    
    except Exception as e:

        message = e
        return await sync_to_async(render)(request, 'change_status.html', {"message": message})