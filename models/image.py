from models.base_model import BaseModel
import peewee as pw
from sqlalchemy.ext.hybrid import hybrid_property
from models.user import User 


class Image(BaseModel):
   description = pw.TextField()
   img_path = pw.CharField(null = True)
   user = pw.ForeignKeyField(User, backref='')

   @hybrid_property
   def image_path(self):
      return 'https://s3-ap-southeast-1.amazonaws.com/next-clone-instagram-hiro/' + self.img_path