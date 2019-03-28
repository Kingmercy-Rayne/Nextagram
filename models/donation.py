from models.base_model import BaseModel
import peewee as pw
from models.image import Image

class Donation(BaseModel):
    value = pw.DecimalField()
    img_id = pw.ForeignKeyField(Image, backref='money_to')
