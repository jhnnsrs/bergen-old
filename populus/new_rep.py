import json
import os
import sys

import dask.array as da
import django
import xarray as xr
import zarr as zr
from pandas.io.json import to_json
from twisted.python.compat import xrange
from zarr.storage import DirectoryStore


def main():
    from elements.models import Representation, Sample
    import larvik.extenders as e
    samp = Sample.objects.create(name="Hallo",creator_id=1)
    store = DirectoryStore("test")
    array = xr.open_zarr(store)["data"]
    Representation.objects.all().delete()
    Representation.objects.from_xarray(array, sample=samp, creator_id=1, name="test")



if __name__ == "__main__":
    
    sys.path.insert(0, '/bergen')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mandal.settings")
    django.setup()

    main()