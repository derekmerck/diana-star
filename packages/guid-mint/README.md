# Distributed DICOM Analytics and Archive (diana-star)

Derek Merck <derek_merck@brown.edu>  
Brown University and Rhode Island Hospital  
Winter 2018

Source: <https://www.github.com/derekmerck/diana-star>  
Documentation: <https://diana.readthedocs.io>  


## Overview

Hospital picture archive and communications systems (PACS) are not well suited for "big data" analysis.  It is difficult to identify and extract datasets in bulk, and moreover, high resolution data is often not even stored in the clinical systems.

**diana** is a [DICOM][] imaging informatics platform that can be attached to the clinical systems with a very small footprint, and then tuned to support a range of tasks from high-resolution image archival to cohort discovery to radiation dose monitoring.

**diana-star** is a celery queuing system with a diana api.  This provides a backbone for distributed task management.  The "star" suffix is in honor of the historical side-note of Matlab's Star-P parallel computing library.


## Dependencies

- Python 3.6
- Many Python packages


## Installation

```bash
$ git clone https://www.github.com/derekmerck/DIANA
$ pip install -r DIANA/requirements.txt
```


## Setup environment

```bash
$ git clone https://github.com/derekmerck/diana-star
$ cd diana-star
$ conda env create -f conda_env.yml -n diana
$ pip install -e ./packages
```


## Test scripts with connect and celery app

```bash
# Reset test environment
$ pushd test/vagrant && vagrant destroy && vagrant up && popd

# Create an orthanc and an index
$ cd stack
$ ansible-playbook -i inv.yml ../test/simple_play.yml

# Run a script
$ python test/diana.py

# Create a broker and some virtual workers for default
$ ansible-playbook -i inv.yml ../test/distrib_play.yml

# Create a local worker to manage the heartbeat and specialized jobs
$ python apps/celery/dcelery worker -n heartbeat -B -Q "file,learn"

# Distribute a script, default should be taken by the diana-service container
$ python test/diana-star.py
```

If multiple environments are being used, the `services.yml` config should use addresses that are absolute and reachable for any workers or input scripts sharing a queue.  The parameters will be pickled and sent along with the task, so `localhost` or hostnames that are only defined on certain hosts will break it.

## License

MIT