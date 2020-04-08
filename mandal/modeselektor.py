"""NMOdule doctstring"""
import os


from larvik.logging import get_module_logger

ARNHEIM_MODE = os.getenv("ARNHEIM_MODE", "S3_POSTGRES_LOCAL_REDIS_DEBUG")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTSET = "!!!!!!! NOT SET !!!!!!!"


try:
    from larvik.logging import get_module_logger
except Exception as e:
    print("Larvik is apparently not installed. Make sure it is")

logger = get_module_logger(__name__)


class ArnheimDefaults:
    #             _____  _   _ _    _ ______ _____ __  __
    #       /\   |  __ \| \ | | |  | |  ____|_   _|  \/  |
    #      /  \  | |__) |  \| | |__| | |__    | | | \  / |
    #     / /\ \ |  _  /| . ` |  __  |  __|   | | | |\/| |
    #    / ____ \| | \ \| |\  | |  | | |____ _| |_| |  | |
    #   /_/    \_\_|  \_\_| \_|_|  |_|______|_____|_|  |_|
    #                  Arnheim Settings
    
    # Domain
    domains = ["localhost"]
    secret_key = NOTSET

    # Zarr Settings
    zarr_dtype = float
    zarr_compression = None

    # Storage S3
    storage = "LOCAL"
    storage_default = 'larvik.storage.local.MediaStorage'
    s3_key = NOTSET
    s3_secret = NOTSET
    s3_host = NOTSET
    s3_port = NOTSET
    s3_public_domain = NOTSET

    # Channel Layer
    channel_backend = "channels_redis.core.RedisChannelLayer"
    channel_host = NOTSET
    channel_port = 6379

    # Storage Local
    media_root = "media"
    static_root = "static_collected"
    media_url = "/media/"
    static_url = "/static/"

    # Database
    sql_engine = "django.db.backends.sqlite3"
    db = NOTSET
    db_user = NOTSET
    db_password = NOTSET
    db_host = NOTSET
    db_port = NOTSET
    db_kwargs = {}
    _initial = None



    # Environment
    logging = False
    debug = False
    loglevel = "INFO"

    def __init__(self , initial = True):
        storage, db, dask, channel, environment = ARNHEIM_MODE.split("_")
        self._initial = initial
        self.printLogo()
        # ENVIRONMENT SETTINGS

        storage = os.getenv("ARNHEIM_STORAGE",storage)
        db = os.getenv("ARNHEIM_DB",db)
        dask = os.getenv("ARNHEIM_DASK",dask)
        channel = os.getenv("ARNHEIM_CHANNEL",channel)
        environment = os.getenv("ARNHEIM_ENVIRONMENT",environment)

        

        if environment == "SUPERDEBUG" :
            self.logging = True
            self.debug = True
            self.loglevel = "DEBUG"
            self.log("In Debug und Supre Debug Log Mode")

        if environment == "DEBUG" :
            self.logging = True
            self.debug = True
            self.loglevel = "INFO"
            self.log("In Debug und Log Mode")

        if environment == "INFO" :
            self.logging = True
            self.debug = False
            self.loglevel = "INFO"
            self.log("In Log Mode")


        self.domains == os.environ.get("ARNHEIM_DOMAINS", "localhost,arnheim.online").split(",")
        self.log(f"Hosting on {repr(self.domains)}")
        # Standard Retrieval
        self.secret_key = os.environ.get('ARNHEIM_KEY', NOTSET)
        if self.debug:
                self.log(f"Arnheim Secret Key {self.secret_key}")

        #Zarr Settings
        self.zarr_compression = os.getenv("ZARR_COMPRESSION",None)
        self.zarr_dtype =  os.getenv("ZARR_DTYPE",float)
        self.log(f"Zarr is using Dtype: {self.zarr_dtype} with Compression: {self.zarr_compression}")

       

        # STORAGE SETTINGS

        if storage == "LOCAL":
            self.storage = "LOCAL"
            self.log(f"Storing Files Locally in {self.media_path}")
            self.log(f"Default Storage Class: {self.storage_default}")
            

        if storage == "S3":
            self.storage = "S3"
            self.storage_default = 'larvik.storage.s3.MediaStorage'
            self.s3_public_domain = os.environ.get("S3_PUBLIC_DOMAIN", NOTSET)
            self.s3_host = os.environ.get("S3_HOST", "minio")
            self.s3_port = os.environ.get("S3_PORT", 9000)
            self.s3_key = os.environ.get("S3_KEY", "weak_access_key")
            self.s3_secret = os.environ.get("S3_SECRET", "weak_secret_key")
            self.log(f"Storing Files in S3 on Host {self.s3_host} at Port {self.s3_port}")
            self.log(f"Accessible on Subdomains of {self.s3_public_domain}")
            self.log(f"Default Storage Class: {self.storage_default}")
            if self.debug:
                self.log(f"AccessKey {self.s3_key}")
                self.log(f"SecretKey {self.s3_secret}")


        if storage == "MINIO":
            self.storage = "S3"
            self.storage_default = 'larvik.storage.s3.MediaStorage'
            self.s3_public_domain = os.environ.get("S3_PUBLIC_DOMAIN", "minio.localhost")
            self.s3_host = os.environ.get("MINIO_SERVICE_HOST", "minio")
            self.s3_port = os.environ.get("MINIO_SERVICE_PORT", 9000)
            self.s3_key = os.environ.get("MINIO_ACCESS_KEY", "weak_access_key")
            self.s3_secret = os.environ.get("MINIO_SECRET_KEY", "weak_secret_key")
            self.log(f"Storing Files in Minio on Host {self.s3_host} at Port {self.s3_port}")
            self.log(f"Accessible on Subdomains of {self.s3_public_domain}")
            self.log(f"Default Storage Class: {self.storage_default}")
            if self.debug:
                self.log(f"AccessKey {self.s3_key}")
                self.log(f"SecretKey {self.s3_secret}")


        # DB SETTINGS
        if db == "LOCAL":
            self.db_name = os.path.join(BASE_DIR, "db.sqlite3")
            self.sql_engine = "django.db.backends.sqlite3"
            self.log(f"Using Local SQlite Database at {self.db}")
            
        if db == "POSTGRES":
            self.db_name = os.environ.get("POSTGRES_DB", "!!!!!!!! NOT SET !!!!!!!!")
            self.sql_engine = "django.db.backends.postgresql"
                        
            self.db_user = os.environ.get("POSTGRES_USER", "user")
            self.db_password = os.environ.get("POSTGRES_PASSWORD", "password")
            self.db_host =  os.environ.get("POSTGRES_SERVICE_HOST", "localhost")
            self.db_port = os.environ.get("POSTGRES_SERVICE_PORT", 5432)
            self.log(f"Using Postgres Backend at Host {self.db_host} at Port {self.db_port}")
            self.log(f"Database Name: {self.db_name}")
            if self.debug:
                self.log(f"User {self.db_user}")
                self.log(f"Password {self.db_password}")


        # DASK SETTINGS

        if dask == "LOCAL":
            self.dask_mode = "LOCAL"
            self.dask_scheduler =  NOTSET
            self.dask_port = NOTSET
            self.log(f"Dask ist no using Cluster")

        if dask == "LOCALCLUSTER":
            self.dask_mode = "LOCALCLUSTER"
            self.dask_scheduler =  os.environ.get("DASK_SCHEDULER_SERVICE_HOST", "localhost")
            self.dask_port = os.environ.get("DASK_SCHEDULER_SERVICE_PORT", 5432)
            self.log(f"Dask ist using Local Cluster")

        if dask == "LOCALCLUSTER":
            self.dask_mode = "DISTRIBUTED"
            self.dask_scheduler =  os.environ.get("DASK_SCHEDULER_SERVICE_HOST", "localhost")
            self.dask_port = os.environ.get("DASK_SCHEDULER_SERVICE_PORT", 5432)
            self.log(f"Dask ist using Distributed Cluster")

        # Channel Settings
        if channel == "LOCAL":
            self.channel_backend = "asgiref.inmemory.ChannelLayer"
            self.log(f"Channel-Layer is Stored in Memory")

        if channel == "REDIS":
            self.channel_backend = "channels_redis.core.RedisChannelLayer"
            self.channel_host =  os.environ.get("REDIS_SERVICE_HOST", "localhost")
            self.channel_port = os.environ.get("REDIS_SERVICE_PORT", 6379)
            self.log(f"Channel-Layer is connected with RedisHost {self.channel_host} at Port {self.channel_port}")

        self.setEnv()

    def setEnv(self):
        """Sets the Environment for S3Storage Backends
        """
        os.environ["AWS_ACCESS_KEY_ID"] = self.s3_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.s3_secret
        self.log("Set Environment Variables")

    def log(self, message):
        if self.logging and self._initial:
            print(message)
    
    def printLogo(self):
        if self._initial is True:
            print("             _____  _   _ _    _ ______ _____ __  __ ")
            print("       /\   |  __ \| \ | | |  | |  ____|_   _|  \/  |")
            print("      /  \  | |__) |  \| | |__| | |__    | | | \  / |")
            print("     / /\ \ |  _  /| . ` |  __  |  __|   | | | |\/| |")
            print("    / ____ \| | \ \| |\  | |  | | |____ _| |_| |  | |")
            print("   /_/    \_\_|  \_\_| \_|_|  |_|______|_____|_|  |_|")
            print("                       Settings                      ")


    @property
    def media_path(self):
        return os.path.join(BASE_DIR,self.media_root)

    @property
    def static_path(self):
        return os.path.join(BASE_DIR,self.static_root)
    
    @property
    def s3_endpointurl(self):
        return self.s3_protocol + "//" + self.s3_host + ":" + str(self.s3_port)

    @property
    def s3_protocol(self):
        return 'http:'