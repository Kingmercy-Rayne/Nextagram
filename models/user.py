from models.base_model import BaseModel
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
import peewee as pw


class User(BaseModel, UserMixin):
    username = pw.CharField(unique=True)
    email = pw.CharField(unique=True)
    password = pw.CharField(null=True)
    picture = pw.CharField(default='profile-placeholder.jpg')
    private = pw.BooleanField(default=False)

    @hybrid_property
    def profile_image_url(self):
        return 'https://s3-ap-southeast-1.amazonaws.com/next-clone-instagram-hiro/' + self.picture

    def is_authenticated(self):
        return True

    # def is_active(self):
    #     return True

    # def is_anonymous(self):
    #     return False

    # def get_id(self):
    #     return (self.id)

    def validate(self):
        duplicate_email = User.get_or_none(User.email==self.email)
        duplicate_username = User.get_or_none(User.username==self.username)
        

        try:
            self.errors
        except:
            self.errors = []

        if duplicate_email:
            self.errors.append('The email already exists!!')
        if duplicate_username:
            self.errors.append("The username already exists!!")

    def idols(self):
        idol = User.alias()
        return (idol.select()
        .join(Following, on=(idol.id == Following.idol_id))
        .where(Following.fan_id == self.id))

    def followers(self):
        follower = User.alias()
        return (follower.select()
        .join(Following, on=(follower.id == Following.fan_id))
        .where(Following.idol_id == self.id))

class Following(BaseModel):
    fan = pw.ForeignKeyField(User)
    idol = pw.ForeignKeyField(User)
    approval = pw.BooleanField(default=False)


