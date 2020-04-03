# Create your views here.
import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse, StreamingHttpResponse, FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.serializers import Serializer
from rest_framework.schemas.openapi import AutoSchema
import xarray as xr
from larvik.logging import get_module_logger
from larvik.models import LarvikArray
from larvik.utils import UUIDEncoder

from zarr.storage import array_meta_key, attrs_key, default_compressor, group_meta_key

zarr_format = 2
zarr_consolidated_format = 1
zarr_metadata_key = '.zmetadata'
channel_layer = get_channel_layer()

api_array = "array"
larvik_c = "c"





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

    def queryselect(self, array, query_params):
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

    def returnFile(self, key, subkey):
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
            url_path=f'{api_array}/c/(?P<c_value>[^/]+)', url_name=f'{api_array}/c')
    def get_c_key(self, request, c_value,  pk):
        return self.returnFile("c",c_value)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/planes/(?P<c_value>[^/]+)', url_name=f'{api_array}/planes')
    def get_planes_key(self, request, c_value,  pk):
        return  self.returnFile("planes",c_value)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/channels/(?P<c_value>[^/]+)', url_name=f'{api_array}/channels')
    def get_channels_key(self, request, c_value,  pk):
        return  self.returnFile("channels",c_value)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/x/(?P<c_value>[^/]+)', url_name=f'{api_array}/x')
    def get_x_key(self, request, c_value,  pk):
        print(c_value)
        return  self.returnFile("x",c_value)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/y/(?P<c_value>[^/]+)', url_name=f'{api_array}/y')
    def get_y_key(self, request, c_value,  pk):
        return  self.returnFile("y",c_value)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/z/(?P<c_value>[^/]+)', url_name=f'{api_array}/z')
    def get_z_key(self, request, c_value,  pk):
        return  self.returnFile("z",c_value)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/t/(?P<c_value>[^/]+)', url_name=f'{api_array}/t')
    def get_t_key(self, request, c_value,  pk):
        return  self.returnFile("t",c_value)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/physy/(?P<c_value>[^/]+)', url_name=f'{api_array}/physy')
    def get_physy_key(self, request, c_value,  pk):
        return  self.returnFile("physy",c_value)
    
    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/physx/(?P<c_value>[^/]+)', url_name=f'{api_array}/physx')
    def get_physx_key(self, request, c_value,  pk):
        return  self.returnFile("physx",c_value)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/physt/(?P<c_value>[^/]+)', url_name=f'{api_array}/physt')
    def get_physt_key(self, request, c_value,  pk):
        return  self.returnFile("physt",c_value)
    
    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/phsyz/(?P<c_value>[^/]+)', url_name=f'{api_array}/phsyz')
    def get_physz_key(self, request, c_value,  pk):
        return  self.returnFile("phsyz",c_value)

    @action(methods=['get'], detail=True,
            url_path=f'{api_array}/data/(?P<c_value>[^/]+)', url_name=f'{api_array}/data')
    def get_data_key(self, request, c_value,  pk):
        return  self.returnFile("data",c_value)






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
