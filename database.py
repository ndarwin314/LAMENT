from mongoengine import Document, DictField, IntField

class Snail(Document):
    snails = DictField(required=True)
    server = IntField(required=True)