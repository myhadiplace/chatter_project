from django import template
from bson.objectid import ObjectId
from bson.dbref import DBRef
register = template.Library()

@register.filter('post_id')
def post_id(value):
    return str(value["_id"])

@register.filter('user_dbref')
def create_user_dbref(value):
    user_id = value["_id"]
    return DBRef("users",ObjectId(user_id))