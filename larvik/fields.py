from django.conf import settings
from django.contrib.postgres.fields.array import ArrayField
from django.db import models

from larvik.storage.s3 import ZarrStorage
from larvik.stores import BioImageFile, XArrayStore


class BioImageFileField(models.FileField):
    attr_class = BioImageFile
    description = "BioImageFile"



class StoreFileField(models.FileField):
    attr_class = XArrayStore
    description = "XArrayStore"


class ShapeField(ArrayField):
    pass


class DimsField(ArrayField):
    pass

