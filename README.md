
#### Consider this a preview, as the ineptly norwegian codenames might suggest

### Idea

Bergen is the API and authentification server for the Arnheim platform. It works in interplay with Arbeider, with who it shares its common programmatical interface: The Django ORM based query language for multidimensional arrays, LarvikArray:

### LarvikArray

LarvikArray is an interface for both Xarray and the Django ORM and enables core feature of both for BioImages:

* Simple ORM based querying of complex experimental layouts
* Different Storage Backends under one API (S3, Local Filesystem,...)
* Easy Pandas and Numpy/Dask/XArray interfaces for data
* Analysis on a Compute Cluster (also part of Platform)
* Metadata retrieval and storage in both Database and XArray through Omero Biometa conversion
* RestAPI for programmtic access anywhere (through Bergen)
* Extensive selection and lazy evaluation of database querys and array slicing (complex queryies simplified and efficient)

### Easy Composition of new Data-Models

Bergen provides two multidimensional array classes out of the box that inherit from the LarvikArray class.

* Representation: a representation *represents* data from the original image stack that shares at least X and Y coordinates (Z, time, and channels optionals)
* Transformation: isolated and transformed ROIs and their underlying data is organized in Transformations. These do not need to share any dimensions of the original sample but may share originial Metadata. 

### Example of Query


```python

rep = Represention.objects.filter(sample__experiment__name__startswith="Animal",type="initial").first() # filters all initial 5Dimension image Stacks of Animal Experiments and takes an examplary first (Database evaluation)
channels = rep.biometa.channels["EmissionWaveLength"] # a pandas dataframe with all just the emission wavelegnt meta data query from the original stack
maxisp = rep.array.sel(t=0,c=0).max(dim="z") # lazily querys t=0 and the first channel from the storage backend, and chains a maximum intensity projection on the z axis

local = maxisp.compute() # through a call to compute the data gets loaded from disk or s3 and processed, this is done via the fantastic dask libraries that can handle massive datasets in the petabyte range and can happen on a cluster. After a compute we are dealing with standard NumpyArrays

local.viewer.show() # if this query was done in a JupyterNotebook it returns an Image of the MaxISP through matplotlib

```

### Authentification and Real Time Communication


Bergen uses OAuth system to provide authoriazion and authentification; users are only able to
use the application once registered on the backend, and can login from a variety of different clients (checkout foreign for a 
working implementation using PyQT)

Real-Time Communication is based on an implementation of Django-Channels that is only available for signed-in users.


### Prerequisites

As Bergen has network dependencies like REDIS (for RTC) and Postgres (Database) it needs a working Docker instance running on your Machine
(detailed instructions found on [Docker Get Started](https://docs.docker.com/get-started/)) and should be run through docker composition.

For Testing on a Local Cluster exists also a Helm chart for easy Kubernetes


### Installing

Once this repository is cloned, cd into the parent directory and adjust the docker-compose.yml
according to your needs ( a good place to start is adjusting the media directories according to your file structure)
once adjusted run (with admin privileges)

```
docker-compose up
```

This should cause the initial installation of all required libraries through docker, (please be patient)

### Running

From now on you can run the project through 
```
docker-compose up
```


## Populating the Database

As there is no initial Database provided you need to setup the Database with a Superuser before starting to do so check the django tutorial on [superuser creation](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Admin_site)
Beware that Django commands like

```
python3 manage.py createsuperuser
python3 manage.py ensuretrontheim #if you wish to use the trontheim.online frontend for non programmers
```

translate to

```
docker-compose run web python manage.py createsuperuser
docker-compose run web python manage.py manage.py ensuretrontheim #if you wish to use the trontheim.online frontend for non programmers
```
in the Docker context

# Basic Information

## Node and Arbeider modules

Modularity is at the heart of the framework. Arnheim relies heavily on the idea of representating an analysis workflow as a graph with multiple nodes. Each node represents an analysis task (for example an Maximum Intensity projection, Edge Enhancing Filter, ROI Isolation,...) that can be chained together with another task. These graphs can then run in batch and intermitten user interaction. (for detailed information visit the documentation (ones up)).

Nodes can be implemented in a variety of programming languages (that can consume task from a REDIS queue and access a postgres database) and are easyily encapsulated in a Docker container. However in order to facilitate the development of these Nodes the framework provided the Arbeider Template:

These modules can rely on the django ORM to access the database, the Dask Cluster, xarray as an accesible interface for the multidimensional arrays, as well as using bindings to tensorflow or the Java ecosystem of image analysis (if so desired through extension of the standard template).

For more details visit the arbeider repo and its example implementations of a Arbeider Node.

### Testing and Documentation

So far Arnheim does not provide unit-tests and is in desperate need of documentation,
please beware that you are using an Alpha-Version

### Issues

As S3 Backend has been a recent addition, main issues arise from there

- A Minio Implementation of S3 Storage is provided for Local Development but struggles with horrific read-and-write speeds
- Remote S3 Testing has not been done yet
- Local Storage is the way to go now

### Roadmap

- Import and Export of Samples
- Kafka pipelining
- ~~Transition to Zarr (dropping HDF5, for multithreaded access)~~ done
- ~~S3 Backend ~~ alpha

## Deployment

Contact the Developer before you plan to deploy this App, it is NOT ready for public release

## Built With

* [Docker](http://www.dropwizard.io/1.0.2/docs/) - Architecture
* [Django](https://maven.apache.org/) - Web Server in python
* [Django-Channels](https://rometools.github.io/rome/) - Used for real-time-communictation
* [Xarray](https://xarray.pydata.org) - Used for working with multidimensional arrays
* [Zarr](https://zarr.readthedocs.io/en/stable/) - Used as a storage backend for distributed access to local and cloud resources
* [DASK](https://dask.org/) - Dask provides advanced parallelism for analytics with Pandas and NumpyArrays

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/jhnnsrs/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

There is not yet a working versioning profile in place, consider non-stable for every release 

## Authors

* **Johannes Roos ** - *Initial work* - [jhnnsrs](https://github.com/jhnnsrs)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.


