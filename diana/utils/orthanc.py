import logging, json
import attr
from .requester import Requester
from .dicom import DicomLevel

# Diana-agnostic API for orthanc, no endpoint or dixel dependencies

@attr.s
class OrthancRequester(Requester):
    user = attr.ib(default="orthanc")
    password = attr.ib(default="orthanc")
    auth = attr.ib(init=False)

    @auth.default
    def set_auth(self):
        return (self.user, self.password)

    def get(self, resource, params=None):
        logging.debug("Getting {} from orthanc".format(resource))
        url = self._url(resource)
        return self._get(url, params=params, auth=self.auth)

    def put(self, resource, data=None):
        logging.debug("Putting {} to orthanc".format(resource))
        url = self._url(resource)
        return self._put(url, data=data, auth=self.auth)

    def post(self, resource, data=None):
        logging.debug("Posting {} to orthanc".format(resource))
        url = self._url(resource)
        return self._post(url, data=data, auth=self.auth)

    def delete(self, resource):
        logging.debug("Deleting {} from orthanc".format(resource))
        url = self._url(resource)
        return self._delete(url, auth=self.auth)

    def get_item(self, oid, level, view):
        # View in [meta, tags, file*, image*, archive**]
        # * only instance level
        # * only series or study level

        params = None
        if view == "meta":
            postfix = None

        elif view == "tags":
            if level == DicomLevel.INSTANCES:
                postfix = "tags"
            else:
                postfix = "shared-tags"
            params = [("simplify", True)]

        elif view == "file" and level == DicomLevel.INSTANCES:
            postfix = "file"  # single dcm

        elif view == "image" and level == DicomLevel.INSTANCES:
            postfix = "preview"  # single dcm

        elif view == "archive" and level > DicomLevel.INSTANCES:
            postfix = "archive"        # zipped archive

        else:
            logging.error("Unsupported get view format {} for {}".format(view, level))
            return

        if postfix:
            resource = "{}/{}/{}".format(level, oid, postfix)
        else:
            resource = "{}/{}".format(level, oid)

        return self.get(resource, params)

    def put_item(self, file):
        resource = "instances"
        self.post(resource, data=file)

    def delete_item(self, oid, level):
        resource = "{}/{}".format(level, oid)
        return self.delete(resource)

    def anonymize_item(self, oid, level, replacement_map=None):

        resource = "{}/{}/anonymize".format(level, oid)

        if replacement_map:
            replacement_json = json.dumps(replacement_map)
            data = replacement_json
            headers = {'content-type': 'application/json'}
            return self.post(resource, data=data, headers=headers)

        return self.post(resource)

    def find(self, query, remote_aet, retrieve_dest=None):

        resource = 'modalities/{}/query'.format(remote_aet)
        headers = {"Accept-Encoding": "identity",
                   "Accept": "application/json"}

        r = self.post(resource, data=query, headers=headers)

        if not r:
            logging.warning("No reply from orthanc remote lookup")
            return

        qid = r["ID"]
        resource = 'queries/{}/answers'.format(qid)

        self.get(resource)

        if not r:
            logging.warning("No answers from orthanc lookup")
            return

        answers = r
        ret = []
        for aid in answers:
            resource = 'queries/{}/answers/{}/content?simplify'.format(qid, aid)
            r = self.get(resource)
            if not r:
                logging.warning("Bad answer from orthanc lookup")
                return

            ret.append(r)

            # If retrieve_dest defined, move data there (usually 1 study to here)
            if retrieve_dest:
                resource = 'queries/{}/answers/{}/retrieve'.format(qid, aid)
                rr = self.post(resource, data=retrieve_dest)
                logging.debug(rr)

        # Returns an array of answers
        return ret

    def send_item(self, oid, level, dest, dest_type):
        resource = "/{}/{}/send".format(dest_type, dest)
        data = oid
        self.post(resource, data=data)

    def statistics(self):
        return self.get("statistics")
