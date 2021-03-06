import os
import yaml
from celery import chain
from diana.distrib.dcelery import app
from diana.distrib.apis import *
from diana.utils.dicom import DicomLevel

# Need a service stack to generate events

if os.path.exists("./services.yml"):
    service_path = "./services.yml"
elif os.path.exists("etc/diana/services.yml"):
    service_path = "/etc/diana/services.yml"
else:
    raise FileNotFoundError("Can not find services.yml")

with open( service_path, "r" ) as f:
    services = yaml.safe_load(f)

orthanc = OrthancEndpoint(**services['orthanc'])
splunk = SplunkEndpoint(**services['orthanc'])

beat_schedule = {
    'status_report': {
        'task': 'message',
        'schedule': 60.0,  # Every 30 seconds
        'args': ["All ok"]
    },

    'index_new_series': {
        'task': 'index_new_series',
        'schedule': 5.0 * 60.0,  # Every 5 minutes
        'args': (orthanc, splunk),
        'kwargs': {'timerange': ("-10m", "now")}
    },

    'index_dose_reports': {
        'task': 'index_dose_reports',
        'schedule': 5.0 * 60.0,  # Every 5 minutes
        'args': (orthanc, splunk),
        'kwargs': {'timerange': ("-10m", "now")}
    }

}


@app.task
def index_new_series(orthanc, splunk):

    q = { "new series" }
    ids = orthanc.find( q )

    for id in ids:
        dixel = orthanc.getstar( id ).get()
        splunk.putstar(dixel)

        # or
        #
        # chain( orthanc.get_s(id) | splunk.put_s() )()


def index_dose_reports(orthanc, splunk, timerange=("-10m", "now")):

    q = { "is dose series",
          timerange }
    ids = splunk.find(q)

    for id in ids:

        data = orthanc.getstar( id, 'meta' )
        instances = data['instances']
        for oid in instances:
            dixel = orthanc.getstar( oid, level=DicomLevel.INSTANCES ).get()
            splunk.putstar( dixel, index=splunk.dose_index )

        # or
        #
        # chain(orthanc.get_s(id, level=DicomLevel.SERIES) | splunk.put_s(index=splunk.series_index))()

def route(orthanc0, orthanc1, anon_map=None):

    q = { "new series" }
    ids = orthanc0.find( q )

    for id in ids:
        dixel = orthanc0.getstar( id ).get()
        orthanc1.putstar( dixel )
        orthanc0.remove( dixel )
