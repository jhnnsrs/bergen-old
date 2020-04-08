# import the logging library
import json
import logging
import xarray as xr
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
import pandas as pd
from django.conf import settings
# Get an instance of a logger
from uuid import uuid4
from larvik.generators import ArnheimGenerator

logger = logging.getLogger(__name__)

class ZarrQueryMixin(object):
    """ Methods that appear both in the manager and queryset. """


class ZarrQuerySet(QuerySet):

    def delete(self):
        # Use individual queries to the attachment is removed.
        for zarr in self.all():
            zarr.delete()


        super().delete()


class LarvikArrayManager(Manager):
    generatorClass = ArnheimGenerator
    group = None
    queryset = ZarrQuerySet

    def get_queryset(self):
        return self.queryset(self.model, using=self._db)


    def from_xarray(self, array: xr.DataArray, fileversion=settings.LARVIK_FILEVERSION, apiversion= settings.LARVIK_APIVERSION,**kwargs):
        """Takes an DataArray and the model arguments and returns the created Model
        
        Arguments:
            array {xr.DataArray} -- An xr.DataArray as a LarvikArray
        
        Returns:
            [models.Model] -- [The Model]
        """
        import larvik.extenders as e

        item = self.model(**kwargs)
        generated = self.generatorClass(item, self.group)
        array.name = generated.name

        # Store Generation
        item.store.name = generated.path
        item.shape = list(array.shape)
        item.dims = list(array.dims)

        try: 
            df = array.biometa.channels.compute()
            channels = df.where(pd.notnull(df), None).to_dict('records')
            item.channels = channels
        except:
            logger.info("Representation does not Contain Channels?")
            


        # Actually Saving
        item.unique = uuid4()
        item.store.save(array, item, fileversion=fileversion, apiversion= apiversion)
        item.save()
        return item

