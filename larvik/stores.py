import traceback

import s3fs
import xarray as xr
import zarr
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.fields.files import FieldFile
from storages.backends.s3boto3 import S3Boto3Storage
from zarr import blosc
from django.core import serializers
from larvik.logging import get_module_logger

logger = get_module_logger(__name__)


class LocalFile(object):
    def __init__(self, field, haspath=False):
        self.field = field
        self.filename = None
        self.tmppath = "/tmp"
        self.haspath = haspath

    def __enter__(self):
        if self.haspath: return self.field.path # No TempFile Necessary
        import os
        import uuid
        _, file_extension = os.path.splitext(self.field.name)
        self.filename = self.tmppath + "/" + str(uuid.uuid4()) + file_extension
        with open(self.filename, 'wb+') as destination:
            for chunk in self.field.chunks():
                destination.write(chunk)

        return self.filename

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False # uncomment to pass exception through
        if self.haspath:
            return True # We dont need a Temporary File of a Local File
        else:
            import os
            os.remove(self.filename)

        return True


class BioImageFile(FieldFile):

    @property
    def local(self):
        if isinstance(self.storage, S3Boto3Storage):
            return LocalFile(self, haspath=False)
        if isinstance(self.storage, FileSystemStorage):
            return LocalFile(self, haspath=True)
        else:
            raise NotImplementedError("Other Storage Formats have not been established yet. Please use S3 like Storage for time being")


compressor = blosc.Blosc(cname='zstd', clevel=3, shuffle=blosc.Blosc.BITSHUFFLE)
blosc.use_threads = True

zarr.storage.default_compressor = compressor

class NotCompatibleException(Exception):
    pass



class XArrayStore(FieldFile):

    def _getStore(self):
        if isinstance(self.storage, S3Boto3Storage):
            bucket = self.storage.bucket_name
            location = self.storage.location
            s3_path = f"{bucket}/{self.name}"
            # Initilize the S3 file system
            logger.info(f"Bucket [{bucket}]: Connecting to {self.name}")
            s3 = s3fs.S3FileSystem(client_kwargs={"endpoint_url": settings.AWS_S3_ENDPOINT_URL})
            store = s3fs.S3Map(root=s3_path, s3=s3)
            return store
        if isinstance(self.storage, FileSystemStorage):
            location = self.storage.location
            path = f"{location}/{self.name}"
            # Initilize the S3 file system
            logger.info(f"Folder [{location}]: Connecting to {self.name}")
            store = zarr.DirectoryStore(path)
            return store
        else:
            raise NotImplementedError("Other Storage Formats have not been established yet. Please use S3 like Storage for time being")

    @property
    def connected(self):
        return self._getStore()

    def save(self, array, compute=True, apiversion = settings.LARVIK_APIVERSION, fileversion= settings.LARVIK_FILEVERSION):
        if self.instance.unique is None: raise Exception("Please assign a Unique ID first")
        dataset = None
        if apiversion == "0.1":
            dataset = array.to_dataset(name="data")
            dataset.attrs["apiversion"] = apiversion
            dataset.attrs["fileversion"] = fileversion
            if fileversion == "0.1":
                dataset.attrs["model"] = str(self.instance.__class__.__name__)
                dataset.attrs["unique"] = str(self.instance.unique)
            else:
                raise NotImplementedError("This FileVersion has not been Implemented yet")

        else:
            raise NotImplementedError("This API Version has not been Implemented Yet")

        try:
            logger.info(f"Saving File with API v.{apiversion}  and File v.{fileversion} ")
            return dataset.to_zarr(store=self.connected, mode="w", compute=compute, consolidated=True)
        except Exception as e:
            raise e

    def loadDataArray(self, apiversion = settings.LARVIK_APIVERSION):
        dataset = xr.open_zarr(store=self.connected, consolidated=False)
        fileversion = dataset.attrs["fileversion"]
        fileapiversion = dataset.attrs["apiversion"]
        if apiversion == "0.1":
            if  fileapiversion == "0.1" and  fileversion == "0.1":
                logger.info(f"Opening File with API v.{apiversion}  and File v.{fileversion} ")
                import larvik.extenders as e
                array = dataset["name"]
                array.name = self.instance.name
                return
            else:
                raise NotCompatibleException(f"The ApiVersion v.{apiversion} is not able to parse file with API v.{fileapiversion} and File v.{fileversion}")
        else: NotImplementedError("This API Version has not been Implemented Yet")


    def loadDataset(self):
        return xr.open_zarr(store=self.connected, consolidated=False)
