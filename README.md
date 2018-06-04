# Diana-Star

Derek Merck <derek_merck@brown.edu>  
Spring 2018  

A Diana service stack with distributed ("star") functions


## Setup environment

```bash
$ git clone https://github.com/derekmerck/diana-star
$ conda env create -f conda_env.yml -n dstar
```


## Test scripts with connect and distrib app

```bash
# Reset test environment
$ pushd test/vagrant && vagrant destroy && vagrant up && popd

# Create an orthanc and an index
$ cd stack
$ ansible-playbook -i inv.yml ../test/simple_services.yml

# Run a script
$ python test/diana.py

# Create a broker and some virtual workers for default
$ ansible-playbook -i inv.yml ../test/distrib_services.yml

# Create a local worker to manage the heartbeat and specialized jobs
$ python apps/celery/dcelery worker -n heartbeat -B -Q "file,learn"

# Distribute a script, default should be taken by the diana-service container
$ python test/diana-star.py
```

