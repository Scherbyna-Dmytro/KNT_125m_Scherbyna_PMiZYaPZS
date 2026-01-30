import asyncio
from umongo import Document, fields, instance
from marshmallow import validate
from motor.motor_asyncio import AsyncIOMotorClient
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance

instance = MotorAsyncIOInstance()

def get_db():

    _client = None
        
    if _client is None:
        _client = AsyncIOMotorClient('mongodb+srv://dsscherbinazp_db_user:zpEfh6bfddu20ef7@cluster1.y0gwbdq.mongodb.net/',
                                    uuidRepresentation='standard')
                                    
                            #mongodb+srv://dsscherbinazp_db_user:zpEfh6bfddu20ef7@cluster1.y0gwbdq.mongodb.net/ - основна БД
                            #mongodb://localhost:27017/
                            

    db = _client.medicine_db

    #db = _client.medicine_db - основна БД
    #db = _client.test_medicine_db

    instance.set_db(db)
        
    return db


@instance.register
class MedUser(Document):

    login = fields.StringField(required = True, unique=True, validate = validate.Length(min = 4, max = 10)) 
    password = fields.StringField(required = True, validate = validate.Length(max = 255))
    address = fields.StringField(required = True, validate = validate.Length(min = 25, max = 150))
    isAdmin = fields.BooleanField(load_default = False)

    class Meta:
        collection_name = "med_user"

@instance.register
class Product(Document):

    product_name = fields.StringField(required = True, validate = validate.Length(min = 3, max = 100))
    manufacturer_name = fields.StringField(required = True, validate = validate.Length(min = 3, max = 100))

    class Meta:
        collection_name = "product"

@instance.register
class Batch(Document):

    product_id = fields.ReferenceField(Product, required = True)
    user_id = fields.ReferenceField(MedUser, required = True)
    package_size = fields.StringField(required = True, validate = validate.Length(min = 5, max = 25))
    expiration_date_1 = fields.DateTimeField(required = True)
    expiration_date_2 = fields.DateTimeField(required = True)
    number_of_packages = fields.IntField(required = True, validate = validate.Range(min = 1))

    class Meta:
        collection_name = "batch"

@instance.register
class Package(Document):

    batch_id = fields.ReferenceField(Batch, required = True)
    qr_code_path = fields.StringField(validate = validate.Length(max = 70))
    status = fields.StringField(load_default = "Active", validate = validate.Length(max = 20))

    class Meta:
        collection_name = "package"




# class MedUser(Document):
    
#     login = StringField(primary_key = True, maxlength = 10, minlength = 4)
#     password = StringField(required = True, maxlength = 255)
#     address = StringField(required = True, maxlength = 150, minlength = 25)
#     isAdmin = BooleanField(required = True, default = False)
#     meta = {'db_alias': 'test_db'}

# class Product(Document):
#     product_id = UUIDField(primary_key = True, default = uuid.uuid4, maxlength = 36, binary=True)
#     product_name = StringField(required = True, maxlength = 100, minlength = 3)
#     manufacturer_name = StringField(required = True, maxlength = 100, minlength = 3)
#     meta = {'db_alias': 'test_db'}

# class Batch(Document):
#     batch_id = UUIDField(primary_key = True, default = uuid.uuid4, maxlength = 36, binary=True)
#     product_id = ReferenceField(Product, required = True)
#     login = ReferenceField(MedUser, required = True)
#     package_size = StringField(required = True, minlength = 5, maxlength = 25)
#     expiration_date_1 = DateField(required = True)
#     expiration_date_2 = DateField(required = True)
#     number_of_packages = IntField(required = True, min_value = 1)
#     meta = {'db_alias': 'test_db'}

# class Package(Document):
#     package_id = UUIDField(primary_key = True, maxlength = 36, binary=True)
#     batch_id = ReferenceField(Batch, required = True)
#     qr_code_path = StringField(required = True, maxlength = 70)
#     status = StringField(required = True, default = "Active", maxlength = 20)
#     meta = {'db_alias': 'test_db'}