# Create your views here.
import json

import xarray as xr
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import FileResponse, HttpResponse, StreamingHttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.serializers import Serializer
from zarr.storage import (array_meta_key, attrs_key, default_compressor,
                          group_meta_key)

from larvik.logging import get_module_logger
from larvik.models import LarvikArray
from larvik.utils import UUIDEncoder

channel_layer = get_channel_layer()

# Zarr Specific Settings
zarr_metadata_key = '.zmetadata'
api_array = "array"





class LarvikJobWrapper(object):

    def __init__(self, data=None, actiontype=None, actionpublishers=None, job=None, channel=None):
        self.actiontype = actiontype
        self.data = data
        self.job = job if job else data
        self.actionpublishers = actionpublishers
        self.channel = channel



class LarvikViewSet(viewsets.ModelViewSet):
    # TODO: The stringpublishing is yet not working

    publishers = None
    viewset_delegates = None
    stringpublish = True


    def __init__(self, **kwargs):
        self.logger = get_module_logger(type(self).__name__)
        super().__init__(**kwargs)

    def publish(self, serializer, method):

        serializedData = serializer.data
        serializedData = json.loads(json.dumps(serializedData, cls=UUIDEncoder)) #Shit workaround to get UUUID to be string

        if self.publishers is not None:
            self.logger.info(f"Publishers {self.publishers}")
            for el in self.publishers:
                self.logger.info(f"What up dog {el}")
                modelfield = "empty"
                try:
                    path = ""
                    for modelfield in el:
                        try:
                            value = serializedData[modelfield]
                            path += "{0}_{1}_".format(str(modelfield), str(value))
                        except KeyError as e:
                            self.logger.info("Modelfield {0} does not exist on {1}".format(str(el), str(self.serializer_class.__name__)))
                            self.logger.info("Publishing to String {0}".format(modelfield))
                            path += "{0}_".format(str(modelfield))
                    path = path[:-1]
                    self.logger.info("Publishing to Models {0}".format(path))
                    stream = str(serializer.Meta.model.__name__)
                    async_to_sync(channel_layer.group_send)(path, {"type": "stream", "stream": stream, "room": path,
                                                                   "method": method, "data": serializedData})
                except KeyError as e:
                    self.logger.info("Error Babe !!!".format(str(el), str(self.serializer_class.__name__)))


    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.logger.info("CALLED create")
        self.publish(serializer, "create")

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.publish(serializer, "update")

    def perform_destroy(self, instance):
        serialized = self.serializer_class(instance)
        self.publish(serialized, "delete")
        super().perform_destroy(instance)


class LarvikArrayViewSet(LarvikViewSet):
    lookup_value_regex = '[^/]+'

    def arraySelect(self,request):
        larvik: LarvikArray = self.get_object()
        query_params = request.query_params
        array = larvik.array
        # We are trying to pass on selection params
        array = self.queryselect(array, query_params)
        return array

    def datasetSelect(self,request):
        larvik: LarvikArray = self.get_object()
        query_params = request.query_params
        dataset = larvik.dataset
        return dataset

    def queryselect(self, array: xr.DataArray, query_params: dict) -> xr.DataArray:
        """Selects the Array Acording to some query parameters
        
        Arguments:
            array {xr.DataArray} -- "The xr.DataArray to select from"
            query_params {dict} -- "The params according to Django QueryDicts"
        
        Raises:
            APIException: An APIExpection
        
        Returns:
            xr.DataArray -- The selected xr.DataArray 
        """
        import larvik.extenders
        try:
            array = array.sel(c=query_params["c"]) if "c" in query_params else array
            array = array.sel(t=query_params["t"]) if "t" in query_params else array
            if "channel_name" in query_params:
                s = f'Name == "{query_params["channel_name"]}"'
                print(s)
                c = array.biometa.channels.compute().query(s).index
                array = array.sel(c= c)
        except Exception as e:
            raise APIException(e)
        return array

    @action(methods=['get'], detail=True,
            url_path='shape', url_name='shape')
    def shape(self, request, pk):
        # We are trying to pass on selection params
        array = self.arraySelect(request)
        answer = json.dumps(array.shape)
        response = HttpResponse(answer, content_type="application/json")
        return response

    @action(methods=['get'], detail=True,
            url_path='dims', url_name='dims')
    def dims(self, request, pk):
        # We are trying to pass on selection params
        array = self.arraySelect(request)
        answer = json.dumps(array.dims)
        response = HttpResponse(answer, content_type="application/json")
        return response



    @action(methods=['get'], detail=True,
            url_path='channels', url_name='channels')
    def channels(self, request, pk):
        # We are trying to pass on selection params
        array = self.arraySelect(request)
        answer = array.biometa.channels.compute().to_json(orient="records")
        response = HttpResponse(answer, content_type="application/json")
        return response

    @action(methods=['get'], detail=True,
            url_path='info', url_name='info')
    def info(self, request, pk):
        # We are trying to pass on selection params
        array: xr.DataArray = self.arraySelect(request)
        with xr.set_options(display_style='html'):
            answer = array._repr_html_()
        response = HttpResponse(answer,  content_type="text/html")
        return response

    def returnFile(self, key: str, subkey: str) -> FileResponse:
        """Returns the FIle in the Store as a File Response 
        
        Arguments:
            key {string} -- key of the xr.Array Variable
            subkey {string} -- subkey of the chunk
        
        Returns:
            [FileResponse] -- The streaming HTTP FileReponse
        """
        larvik: LarvikArray = self.get_object()
        test = larvik.store.storage.open(f"{larvik.store.name}/{key}/{subkey}","rb")
        return FileResponse(test)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/{zarr_metadata_key}', url_name=f'{api_array}/{zarr_metadata_key}')
    def get_zmetadata(self, request, pk):
        larvik: LarvikArray = self.get_object()
        test = larvik.store.storage.open(f"{larvik.store.name}/{zarr_metadata_key}","r")
        file_content = test.read()
        test.close()

        return HttpResponse(content=file_content, content_type="application/json")


    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/{group_meta_key}', url_name=f'{api_array}/{group_meta_key}')
    def get_zgroupdata(self, request, pk):
        larvik: LarvikArray = self.get_object()
        test = larvik.store.storage.open(f"{larvik.store.name}/{group_meta_key}","r")
        file_content = test.read()
        test.close()

        return HttpResponse(content=file_content, content_type="application/json")

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/{attrs_key}', url_name=f'{api_array}/{attrs_key}')
    def get_zattrs(self, request, pk):
        larvik: LarvikArray = self.get_object()
        test = larvik.store.storage.open(f"{larvik.store.name}/{attrs_key}","r")
        file_content = test.read()
        test.close()

        return HttpResponse(content=file_content, content_type="application/json")

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/(?P<c_key>[^/.]+)/(?P<c_value>[^/]+)', url_name=f'{api_array}/arrayaccessor')
    def get_data_key(self, request, c_key, c_value,  pk):
        return  self.returnFile(c_key,c_value)





class LarvikJobViewSet(LarvikViewSet):

    actionpublishers = None  # this publishers will be send to the Action Handles and then they can send to the according
    channel = None
    actiontype = "startJob"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def preprocess_jobs(self, serializer: Serializer):
        """ If you need to alter any data like creating an Model on the fly
         or create various jobs from one request, here is the place
         should return Array of Jobs that need executing"""
        return [self.create_job(serializer.data)]

    def create_job(self, data, actiontype=None, actionpublishers=None, job=None, channel=None) -> LarvikJobWrapper:
        actiontype = actiontype if actiontype else self.actiontype
        actionpublishers = actionpublishers if actionpublishers else self.actionpublishers
        job = job if job else data
        channel = channel if channel else self.channel
        return LarvikJobWrapper(data, actiontype, actionpublishers, job, channel)

    def perform_create(self, serializer):
        """ Right now only the creation of a new Job is possible, no way of stopping a job on its way"""
        serializer.save()
        jobs = self.preprocess_jobs(serializer)
        self.publish_jobs(jobs)
        self.publish(serializer, "create")

    def publish_jobs(self, jobs: [LarvikJobWrapper]):
        for nana in jobs:
            async_to_sync(channel_layer.send)(nana.channel, {"type": nana.actiontype, "data": nana.data,
                                                             "publishers": nana.actionpublishers, "job": nana.job})
