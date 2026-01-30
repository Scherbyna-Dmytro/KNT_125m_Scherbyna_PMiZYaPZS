from datetime import date, datetime, time
from pathlib import Path
from bson import ObjectId
import qrcode
from django.conf import settings
from .mongoDB_models import *
from django.contrib.auth.hashers import make_password, check_password
from asgiref.sync import sync_to_async


FOLDER_FOR_CODES = Path(settings.BASE_DIR) / "QR-Codes"

async def AddUser(login, password, address):

    db = get_db()

    if await MedUser.find_one({"login": login, "address": address}): #MedUser.objects(login = login, address = address).first():
        return False

    hashed_password = await sync_to_async(make_password)(password)

    user = MedUser(
        login = login,
        password = hashed_password,
        address = address
    )

    await user.commit()
    return True

async def SignIn(login, password):

    db = get_db()
    
    user = await MedUser.find_one({"login": login}) #MedUser.objects(login = login).first()

    if user:
        if await sync_to_async(check_password)(password, user.password):
            return user
        
    return None

async def AddProduct(product, manufacturer):

    db = get_db()
    
    new_product = await Product.find_one({"product_name": product, "manufacturer_name": manufacturer}) 
    #Product.objects(product_name = product, manufacturer_name = manufacturer).first()

    if new_product is None:
        new_product = Product(
            product_name = product,
            manufacturer_name = manufacturer
        )

        await new_product.commit()
        return True
    
    else:
        return False
    

async def GetProducts():

    db = get_db()

    products = await Product.find().to_list(length = None) #Product.objects()
    return products

async def GetUsers():

    db = get_db()

    users = await MedUser.find({"isAdmin": False}).to_list(length = None) #MedUser.objects(isAdmin = False)
    return users


async def AddBatch(product_id, user_id, package_size, expiration_date_1, expiration_date_2, number_of_packages):

    db = get_db()

    user_id = ObjectId(user_id)
    product_id = ObjectId(product_id)

    try:

        if isinstance(expiration_date_1, str):
            expiration_date_1 = datetime.fromisoformat(expiration_date_1).date()
        if isinstance(expiration_date_2, str):
            expiration_date_2 = datetime.fromisoformat(expiration_date_2).date()


        if isinstance(expiration_date_1, date) and not isinstance(expiration_date_1, datetime):
            expiration_date_1 = datetime.combine(expiration_date_1, time.min)
        if isinstance(expiration_date_2, date) and not isinstance(expiration_date_2, datetime):
            expiration_date_2 = datetime.combine(expiration_date_2, time.min)

        new_batch = Batch(
            product_id = product_id,
            user_id = user_id,
            package_size = package_size,
            expiration_date_1 = expiration_date_1,
            expiration_date_2 = expiration_date_2,
            number_of_packages = number_of_packages
        )

        await new_batch.commit()

        # await sync_to_async(os.makedirs)(FOLDER_FOR_CODES, exist_ok = True)

        packages = []
        for _ in range(number_of_packages):
        
            package = Package(
                batch_id = new_batch.id,
            )

            await package.commit()

            pack_id = package.id

            status = "Active"
            qr_data = f"{product_id}|{new_batch.id}|{pack_id}|{expiration_date_1.isoformat()}|{expiration_date_2.isoformat()}|{status}"
            qr_img = await sync_to_async(qrcode.make)(qr_data)

            file_name = f"{pack_id}.png"
            file_path = FOLDER_FOR_CODES / file_name #os.path.join(FOLDER_FOR_CODES, file_name)
            await sync_to_async(qr_img.save)(file_path)

            package.qr_code_path = str(file_path.relative_to(settings.BASE_DIR)) # file_path

            packages.append(package)
        
        for package in packages:
            await package.commit()

        #Package.objects.insert(packages)

        return True
    
    except:
        return False


async def GetListProducts(user_id, isAdmin):

    db = get_db()

    user_id = ObjectId(user_id)
    
    if isAdmin == True:    
       packages = await Package.find().to_list(length = None) #Package.objects.select_related(max_depth = 2)

    else: 
        batches = await Batch.find({"user_id": user_id}).to_list(length = None)
        batch_ids = [ObjectId(batch.id) for batch in batches]   #Batch.objects.filter(login = login).values_list('batch_id')      
        packages = await Package.find({"batch_id": {"$in": batch_ids}}).to_list(length = None)    #Package.objects.filter(batch_id__in = batch_ids).select_related(max_depth = 2)

    result = []
    for package in packages:
        
        batch = await package.batch_id.fetch()
        user = await batch.user_id.fetch()
        product = await batch.product_id.fetch()

        result.append({
            "package_id": str(package.id),
            "status": package.status,

            "batch_id": str(batch.id),
            "address": user.address,
            "package_size": batch.package_size,
            "expiration_date_1": batch.expiration_date_1,
            "expiration_date_2": batch.expiration_date_2,

            "product_id": str(product.id),
            "product_name": product.product_name,
            "manufacturer_name": product.manufacturer_name,
        })

    return result


async def ChangeStatusForPackage(selected_package_id, selected_batch_id, selected_product_id, selected_expiration_date_1, selected_expiration_date_2, new_status):

    db = get_db()

    try:

        package_id = ObjectId(selected_package_id)

        package = await Package.find_one({"id": package_id}) #Package.objects(package_id = package_uuid).first()

        # await sync_to_async(os.makedirs)(FOLDER_FOR_CODES, exist_ok = True)

        if package:

            package.status = new_status

            qr_data = f"{selected_product_id}|{selected_batch_id}|{selected_package_id}|" \
                      f"{selected_expiration_date_1}|{selected_expiration_date_2}|{new_status}"
            
            qr_img = await sync_to_async(qrcode.make)(qr_data)

            file_path = settings.BASE_DIR / package.qr_code_path
            await sync_to_async(qr_img.save)(file_path)

            await package.commit()
        return True
    
    except:
        return False

async def ChangeStatusForBatch(selected_batch_id, selected_product_id, selected_expiration_date_1, selected_expiration_date_2, new_status):

    db = get_db()

    try:

        batch_id = ObjectId(selected_batch_id)

        packages = await Package.find({"batch_id": batch_id}).to_list(length = None) #Package.objects(batch_id = selected_batch_id)

        # await sync_to_async(os.makedirs)(FOLDER_FOR_CODES, exist_ok = True)

        if packages:

            for item in packages:

                item.status = new_status

                qr_data = f"{selected_product_id}|{selected_batch_id}|{str(item.id)}|" \
                        f"{selected_expiration_date_1}|{selected_expiration_date_2}|{new_status}"
                
                qr_img = await sync_to_async(qrcode.make)(qr_data)

                file_path = settings.BASE_DIR / item.qr_code_path
                await sync_to_async(qr_img.save)(file_path)

                await item.commit() 
        return True
    
    except:
        return False