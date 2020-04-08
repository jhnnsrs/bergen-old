import uuid
from json import JSONEncoder

import dask
import xarray
import zarr as zr
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.postgres.fields.array import ArrayField
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

# Create your models here.
from larvik.fields import DimsField, ShapeField, StoreFileField
from larvik.logging import get_module_logger
from larvik.managers import LarvikArrayManager
from larvik.storage.default import get_default_storagemode
from larvik.storage.local import LocalStorage, ZarrStorage
from larvik.storage.s3 import S3Storage

logger = get_module_logger(__name__)

get_user_model()
class LarvikJob(models.Model):
    statuscode = models.IntegerField( null=True, blank=True)
    statusmessage = models.CharField(max_length=500,  null=True, blank=True)
    settings = models.CharField(max_length=1000) # jsondecoded
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    nodeid = models.CharField(max_length=400, null=True, blank=True)

    class Meta:
        abstract = True

    def _repr_html_(self):
        return f'''<h5>Request by {self.creator.username} </h5>
                <ul>
                    <li> Last Status: {self.statusmessage}</li>
                    <li> Node Status: {self.nodeid}</li>
                    <li> Settings: {self.settings}</li>
                </ul>'''

class LarvikConsumer(models.Model):
    name = models.CharField(max_length=100)
    channel = models.CharField(max_length=100, unique=True, default="Not active")
    settings = models.CharField(max_length=1000)  # json decoded standardsettings

    class Meta:
        abstract = True


class LarvikArrayBase(models.Model):
    fileserializer = None


    store = StoreFileField(verbose_name="store",storage=get_default_storagemode().zarr(), upload_to="zarr", blank=True, null= True, help_text="The location of the Array on the Storage System (S3 or Media-URL)")
    shape = ShapeField(models.IntegerField(),help_text="The arrays shape")
    dims = DimsField(models.CharField(max_length=100),help_text="The arrays dimension")
    name = models.CharField(max_length=1000, blank=True, null= True,help_text="Cleartext name")
    signature = models.CharField(max_length=300,null=True, blank=True,help_text="The arrays unique signature")
    unique = models.UUIDField(default=uuid.uuid4, editable=False)

    objects = LarvikArrayManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    class Meta:
        abstract = True
        

    @property
    def info(self):
        return self.array.info()

    @property
    def viewer(self):
        import larvik.extenders
        return self.array.viewer

    @property
    def biometa(self):
        import larvik.extenders
        return self.array.biometa

    @property
    def array(self):
        """Accessor for the xr.DataArray class attached to the Model
        
        Raises:
            NotImplementedError: If Array does not contain a Store
        
        Returns:
            [xr.DataArray] -- The xr.DataArray class
        """
        if self.store:
            array = self.store.loadDataArray()
            return array
        else:
            raise NotImplementedError("This array does not have a store")


    @property
    def dataset(self):
        """Accessor for the xr.DataSet class attached to the Model
        
        Raises:
            NotImplementedError: If Array does not contain a Store
        
        Returns:
            [xr.Dataset] -- The Dataset 
        """
        if self.store:
            array = self.store.loadDataset()
            return array
        else:
            raise NotImplementedError("This array does not have a store")

    def _repr_html_(self):
        return "<h1>" + f'Array at {str(self.group)} in {self.store}' + "</h1>"




class LarvikArray(LarvikArrayBase):
    channels = JSONField(null=True)

    class Meta:
        abstract = True
