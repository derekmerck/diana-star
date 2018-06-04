# Diana-Star

Derek Merck <derek_merck@brown.edu>  
Spring 2018  

## Diana service stack with distributed ("star") functions



## Test scripts with connect and distrib app

```bash
# Create an orthanc and an index
ansible-playbook -i inv.yml test/simple.yml

# Run a script
python test/diana.py

# Create a broker and some virtual workers for default
ansible-playbook -i inv.yml test/distrib.yml

# Create a local worker to manage the heartbeat and specialized jobs
python apps/celery/dcelery worker -n heartbeat -B -Q "default,file,learn"

# Distribute a script
python test/diana-star.py
```


## Build multiarchitecture container services
