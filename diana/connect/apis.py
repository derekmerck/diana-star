"""
Diana Endpoint APIs:

- Orthanc (dcm RESTful PACS and PACS proxy)
- File    (dcm files)
- Redis   (data cache)
- Splunk  (data index)
- Classifier (AI)

As much Diana-agnostic functionality as possible has been abstracted to
related modules in "generic" for use with other modules, packages, or applications.

"""

import logging, os, time
from redis import Redis
from dill import loads, dumps
import attr
from diana.utils import Endpoint, Item, DicomLevel, OrthancRequester, SplunkRequester, DicomFileIO
from .utils.anon_map import simple_anon_map
from .utils.orth_fiq import find_item_query
from .dixel import Dx


# All Diana Endpoints implement a Factory for passing unpickle-able
# instances by pattern

@attr.s
class DianaFactory(object):
    service = attr.ib(default=None)

    # Can't pass endpoints bc of sockets and other unpickleable objects,
    # so use a blueprint to recreate the endpoint at the worker
    @classmethod
    def factory(self, pattern):
        service = pattern['service'].lower()
        if service == "orthanc":
            return OrthancEndpoint(**pattern)
        if service == "redis":
            return RedisEndpoint(**pattern)
        if service == "file":
            return FileEndpoint(**pattern)
        if service == "classification":
            return ClassificationEndpoint(**pattern)
        else:
            raise KeyError("No such api as {}".format(pattern['service']))

    # Dump the factory pattern for this endpoint (will include passwords, etc)
    @property
    def p(self):
        pattern = {}
        for item in self.__init__.__code__.co_varnames[1:]:
            if item == "queue":
                # Ignore distrib variables
                continue
            pattern[item] = self.__dict__[item]
        return pattern


@attr.s
class OrthancEndpoint(Endpoint, DianaFactory):
    service = attr.ib( default="orthanc" )
    host = attr.ib( default="localhost" )
    port = attr.ib( default="8042" )
    path = attr.ib( default = "")
    user = attr.ib( default="orthanc" )
    password = attr.ib( default="orthanc" )
    location = attr.ib()
    requester = attr.ib()
    inventory = attr.ib()

    # This is only used as an identifier for logging
    @location.default
    def set_loc(self):
        return "http://{}:{}/{}".format(self.host, self.port, self.path)

    @requester.default
    def set_req(self):
        # HTTP gateway
        req = OrthancRequester(host=self.host, port=self.port, path=self.path)
        try:
            stats = req.get("statistics")
            logging.debug( "Connected to orthanc at {}".format(self.location) )
            logging.debug( format(stats) )
            return req
        except ConnectionError:
            logging.error("No connection for orthanc! Requester is None")
            return None

    # Do NOT need to do this unless doing lazy puts or finds
    # TODO: Need a way to init appropriate level for an interator or __in__
    @inventory.default
    def set_inv(self):
        try:
            return {
                # "patients":  [],   # self.requester.get("patients"),
                "studies":   [],   # self.requester.get("studies"),
                "series":    [],   # self.requester.get("series"),
                "instances": [],   # self.requester.get("instances")
                }
        except:
            logging.error("Inventory failed for orthanc!  Inventory is None".format(self.location))
            return None

    def get(self, oid, level, view="tags"):
        result = self.requester.get_item(oid, level, view=view)
        if view=="tags":
            # We can assemble a dixel
            item = Dx(meta=result, level=level)
            return item
        else:
            # Return the meta infor or binary data
            return result

    def put(self, item):
        if item.level != DicomLevel.INSTANCES:
            logging.warning("Can only 'put' Dicom instances.")
            raise ValueError
        if not item.file:
            logging.warning("Can only 'put' file data.")
            raise KeyError
        return self.requester.put_item(item.file)

    def handle(self, item, instruction, **kwargs):

        if instruction == "anonymize":
            replacement_map = kwargs.get('replacement_map', simple_anon_map)
            replacement_dict = replacement_map(item.meta)
            return self.requester.anonymize(item.oid, item.level, replacement_dict=replacement_dict)

        elif instruction == "remove":
            oid = item.oid()
            level = item.level
            return self.requester.delete_item(oid, level)

        elif instruction == "find":
            domain = kwargs.get("remote_aet", "local")
            retrieve_dest = kwargs.get("retrieve_dest", None)
            query = OrthancEndpoint.find_item_query()
            return self.requester.find(query, domain, retrieve_dest=retrieve_dest)

        elif instruction == "send":
            modality = kwargs.get("modality")
            peer = kwargs.get("peer")
            if modality:
                self.requester.send(item.id, item.level, modality, dest_type="modality")
            if peer:
                self.requester.send(item.id, item.level, peer, dest_type="peer")

        elif instruction == "clear":
            self.inventory['studies'] = self.requester.get("studies")
            for oid in self.inventory:
                self.requester.delete_item(oid, DicomLevel.STUDIES)

        elif instruction == "info":
            return self.requester.statistics()

        raise NotImplementedError("No handler found for {}".format(instruction))

    # These do not take and return items, so they may be gets or puts?

    def anonymize(self, item, replacement_map=None):
        return self.handle(item, "anonymize", replacement_map=replacement_map)

    def remove(self, item):
        return self.handle(item, "remove")

    def find(self, q, domain="local", retrieve="false"):
        return self.handle(None, "find", query=q, domain=domain, retrieve=retrieve)

    def send(self, item, peer=None, modality=None):
        return self.handle(None, "send", peer=peer, modality=modality)

    def clear(self):
        return self.handle( None , "clear" )

    def info(self):
        return self.handle( None , "info" )

    def __contains__(self, item):

        # Can mark the inventory stale by calling self.set_inv()
        if item.level == DicomLevel.STUDIES:
            if len(self.inventory['studies']) == 0:
                self.inventory['studies'] = self.requester.get("studies")
            inv = self.inventory['studies']
        elif item.level == DicomLevel.SERIES:
            if len(self.inventory['series']) == 0:
                self.inventory['series'] = self.requester.get("series")
            inv = self.inventory['series']
        elif item.level == DicomLevel.INSTANCES:
            if len(self.inventory['instances']) == 0:
                self.inventory['instances'] = self.requester.get("studies")
            inv = self.inventory['instances']
        else:
            self.logger.warn("Can only '__contain__' study, series, instance dixels")
            return

        return item.oid() in inv

OrthancEndpoint.find_item_query = find_item_query

# Data cache
@attr.s
class RedisEndpoint(Endpoint, DianaFactory):
    service = attr.ib( default="redis" )
    db = attr.ib( default=0 )
    inventory = attr.ib( init=False )

    @inventory.default
    def connect(self):
        return Redis(db=self.db)

    def put(self, item, **kwargs):
        self.inventory.set( item.id, dumps(item) )

    def get(self, id, **kwargs):
        item = loads( self.inventory.get(id) )
        return item


@attr.s
class FileEndpoint(Endpoint, DianaFactory):
    service = attr.ib( default="file" )
    dfio = attr.ib( init=False )

    @dfio.default
    def set_dfio(self):
        return DicomFileIO(location=self.location)

    def put(self, item, path=None, explode=None):
        fn = item.meta['FileName']
        data = item.data

        if item.level == DicomLevel.INSTANCES and \
                os.path.splitext(fn)[-1:] != ".dcm":
            fn = fn + '.dcm'   # Single file
        if item.level > DicomLevel.INSTANCES and \
            os.path.splitext(fn)[-1:] != ".zip":
            fn = fn + '.zip'   # Archive format

        self.dfio.write(fn, data, path=path, explode=explode )

    def get(self, fn, path=None, pixels=False, file=False):
        # print("getting")
        dcm, fp = self.dfio.read(fn, path=path, pixels=pixels)

        _meta = {'PatientID': dcm[0x0010, 0x0020].value,
                 'AccessionNumber': dcm[0x0008, 0x0050].value,
                 'StudyInstanceUID': dcm[0x0020, 0x000d].value,
                 'SeriesInstanceUID': dcm[0x0020, 0x000e].value,
                 'SOPInstanceUID': dcm[0x0008, 0x0018].value,
                 'TransferSyntaxUID': dcm.file_meta.TransferSyntaxUID,
                 'TransferSyntax': str(dcm.file_meta.TransferSyntaxUID),
                 'MediaStorage': str(dcm.file_meta.MediaStorageSOPClassUID),
                 'PhotometricInterpretation': dcm[0x0028, 0x0004].value,  #MONOCHROME, RGB etc.
                 'FileName': fn,
                 'FilePath': fp}

        _data = None
        if pixels:
            _data = dcm.pixel_array

        _file = None
        if file:
            with open(fp, 'rb') as f:
                _file = f.read()

        item = Dx(level=DicomLevel.INSTANCES, meta=_meta, data=_data, file=_file)
        return item


# metadata endpoint Splunk, csv
@attr.s
class SplunkEndpoint(Endpoint, DianaFactory):
    service = attr.ib( default="splunk" )
    host = attr.ib( default="localhost" )
    port = attr.ib( default="8080" )
    hec_port = attr.ib( default="8088" )
    user = attr.ib( default="splunk" )
    password = attr.ib( default="splunk" )
    location = attr.ib()
    requester = attr.ib()
    # inventory = attr.ib()

    # This is only used as an identifier for logging
    @location.default
    def set_loc(self):
        return "http://{}:{} hec:{}".format(self.host, self.port, self.hec_port)

    @requester.default
    def set_req(self):
        # HTTP gateway
        return SplunkRequester(host=self.host, port=self.port, hec_port=self.hec_port)

    def put(self, item, host=None, *kwargs):

        def epoch(dt):
            tt = dt.timetuple()
            return time.mktime(tt)

        record = item.meta
        # This has to be created
        # record_time = epoch(record['InstanceCreationDateTime'])
        record_time = None
        self.req.post_event(record, event_time=record_time, host=host)

    def handle(self, item, instruction, **kwargs):

        if instruction == "find":
            query = kwargs.get("query")
            index = kwargs.get("index")
            return self.requester.find(query, index)

    def find(self, q, index):
        return self.handle(None, "find", query=q, index=index)

@attr.s
class ClassificationEndpoint(Endpoint, DianaFactory):
    service = attr.ib(default="classification")

    def classify(self, item, **kwargs):
        item.meta['classified'] = True
        return item
