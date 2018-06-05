import logging, time, collections
import attr
from bs4 import BeautifulSoup
from .requester import Requester

@attr.s
class SplunkRequester(Requester):
    auth = attr.ib()
    hec_port = attr.ib(default=None)  #http event collector port
    hec_token = attr.ib(default=None)
    hec_auth = attr.ib(init=False)

    @auth.default
    def set_auth(self):
        return "123"

    @hec_auth.default
    def set_hec_auth(self):
        return "123"

    def _hec_url(self, resource):
        return "https://{}:{}/{}".format(self.host, self.port, 'services/collector/event')

    # get
    # put
    # post
    # delete

    # get_record
    # put_record
    # find_records

    def get(self, resource, params=None):
        logging.debug("Getting {} from splunk".format(resource))
        url = self._url(resource)
        return self._get(url, params=params, auth=self.auth)

    def put(self, resource, data=None):
        logging.debug("Putting {} to splunk".format(resource))
        url = self._url(resource)
        return self._put(url, data=data, auth=self.auth)

    # Post to the query address
    def post(self, resource, data=None):
        logging.debug("Posting {} to splunk")
        url = self._url()
        return self._post(url, data=data, auth=self.auth)

    # Post to the hec address -- could be aliased to "put"
    def hec_post(self, data=None):
        logging.debug("Posting record to splunk HEC")
        url = self._hec_url()
        return self._post(url, data=data, auth=self.auth)

    def delete(self, resource):
        logging.debug("Deleting {} from splunk".format(resource))
        url = self._url(resource)
        return self._delete(url, auth=self.auth)


    def find(self, query, index):

        def poll_until_done(sid):
            isDone = False
            i = 0
            r = None
            while not isDone:
                i = i + 1
                time.sleep(1)
                r = self.session.do_get('services/search/jobs/{0}'.format(sid), params={'output_mode': 'json'})
                isDone = r['entry'][0]['content']['isDone']
                status = r['entry'][0]['content']['dispatchState']
                if i % 5 == 1:
                    logging.debug('Waiting to finish {0} ({1})'.format(i, status))
            return r['entry'][0]['content']['resultCount']

        if not query:
            query = "search index={0} | spath ID | dedup ID | table ID".format(index)

        r = self.post('services/search/jobs', data="search={0}".format(query))

        soup = BeautifulSoup(r, 'xml')
        sid = soup.find('sid').string
        n = poll_until_done(sid)
        offset = 0
        instances = []
        i = 0
        while offset < n:
            count = 50000
            offset = 0 + count * i
            r = self.get('services/search/jobs/{0}/results'.format(sid),
                        params={'output_mode': 'csv', 'count': count, 'offset': offset})
            instances = instances + r.replace('"', '').splitlines()[1:]
            i = i + 1
        return instances

    def post_event(self, event, index="default", host=None, event_time=None, event_format=None):

        data = collections.OrderedDict([('time', event_time or time.now() ),
                                        ('host', host or self.id),
                                        ('sourcetype', event_format or '_json'),
                                        ('index', index),
                                        ('event', event)])
        self.hec_post(data=data)
