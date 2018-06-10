from diana.utils import DicomLevel
from diana.distrib.dcelery import app
from diana.distrib.apis import OrthancEndpoint, SplunkEndpoint
from diana.connect.utils.copy_items import copy_items, copy_children

# from diana.connect.apis import OrthancEndpoint as Orthanc, SplunkEndpoint as Splunk
# I think if this one is _last_ it will use the distributed versions


@app.task(name="message")
def message(msg, *args, **kwargs):
    print(msg)


@app.task(name="index_series")
def index_series( archive, index, timerange=("-10m","now") ):

    archive = OrthancEndpoint(archive)
    index = SplunkEndpoint(index)

    worklist = archive.find(
        { "timerange": timerange,
          "level": DicomLevel.SERIES
        }
    )
    available = index.find(
        { "timerange": timerange,
          "level": DicomLevel.SERIES,  # Returns Dx of this type
          "index": "DicomSeries",
          "host": archive.location
        }
    )

    new_items = worklist - available
    copy_items(new_items, archive, index, splunk_index="DicomSeries")


@app.task
def index_dose_reports( archive, index, timerange=("-10m", "now"), **kwargs ):

    archive = OrthancEndpoint(archive)
    index = SplunkEndpoint(index)

    worklist = index.find(
        {   "timerange": timerange,
            "index": "DicomSeries",
            "level": DicomLevel.SERIES,  # Returns Dx at this level
            "host": archive.location,
            "Modality": "SR",
            "SeriesDescription": "*DOSE*"
        }
    )

    # Need to find and send the _child_ instance for each dx
    copy_children(worklist, archive, index, splunk_index="DoseReports")


@app.task
def index_remote( proxy, remote_aet, index, dcm_query=None, splunk_query=None, timerange=("-10m", "now"), **kwargs ):

    archive = OrthancEndpoint(proxy)
    index = SplunkEndpoint(index)

    worklist = proxy.remote_find(
        {"timerange": timerange,
         "level": DicomLevel.SERIES,
         "query": dcm_query
         },
        remote_aet
    )

    available = index.find(
        { "timerange": timerange,
          "level": DicomLevel.SERIES,  # Returns Dx of this type
          "index": "RemoteSeries",
          "host": remote_aet + " via " + proxy.location,
          "splunk_query": splunk_query
        }
    )

    new_items = worklist - available
    copy_items(new_items, proxy, index, splunk_index="RemoteSeries")

@app.task
def route( source, dest, **kwargs ):

    current = 0
    done = False

    while not done:
        changes = source.changes( since=current, limit=10 )
        ret = source.requester.do_get('changes', params={ "since": current, "limit": 10 })

        for change in ret['Changes']:
            # We are only interested interested in the arrival of new instances
            if change['ChangeType'] == 'NewInstance':
                source.send( change['ID'], dest, level=DicomLevel.INSTANCES ).get()
                source.remove( change['ID'], level=DicomLevel.INSTANCES )

        current = ret['Last']
        done = ret['Done']

    source.changes( clear=True )
    source.exports( clear=True )




