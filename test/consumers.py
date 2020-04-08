from typing import Dict, List, Tuple

import numpy as np
from django.db import models

import dask.array as da
from elements.models import Transformation
from larvik.consumers import SyncLarvikConsumer
from larvik.discover import register_consumer
from test.models import Tester

@register_consumer("synctester", model= Tester)
class SyncTester(SyncLarvikConsumer):
    pass

