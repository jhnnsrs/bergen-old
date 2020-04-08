from test.models import Tester, Testing
from test.serializers import TestingSerializer
from typing import Dict, List, Tuple

import dask.array as da
import numpy as np
from django.db import models

from elements.models import Representation, Sample, Transformation
from larvik.consumers import DaskSyncLarvikConsumer, SyncLarvikConsumer
from larvik.discover import NonePath, register_consumer


@register_consumer("synctester", model= Tester)
class SyncTester(SyncLarvikConsumer):
    requestClass = Testing
    requestClassSerializer = TestingSerializer
    path = NonePath

    def start(self, request: Testing, settings: dict):
        print(request,settings)
        return "DONE"


@register_consumer("dasktester", model= Tester)
class DaskSyncTester(DaskSyncLarvikConsumer):
    requestClass = Testing
    requestClassSerializer = TestingSerializer
    path = NonePath

    def start(self, request: Testing, settings: dict):

        it = da.zeros((1023,1023,3,100))
        lala = it.max(axis=3)
        result = self.compute(lala)
        print(result)
        return "DONE"

@register_consumer("reptester", model= Tester)
class DaskSyncTester(DaskSyncLarvikConsumer):
    requestClass = Testing
    requestClassSerializer = TestingSerializer
    path = NonePath

    def start(self, request: Testing, settings: dict):

        rep = Representation.objects.first()
        samp = Sample.objects.create(name="Hallo",creator_id=1)
        maximumisp = rep.array.max(dim="z")

        newrep, graph = Representation.objects.from_xarray(maximumisp, sample=samp, creator_id=1, compute=False, name=f"MaxISP of {rep.name}")
        store =  self.compute(graph, wanted="THREADED")

        print(maximumisp)
        return "DONE"
