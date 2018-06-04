import ruamel_yaml as yaml

with open("../../_secrets/secrets.yml", "r") as f:
    secrets = yaml.safe_load(f)

SERVICE_DOMAIN = "dev"
secrets = secrets.get('services').get(SERVICE_DOMAIN)

splunk = secrets.get('splunk')
orthanc = secrets.get('orthanc')
redis = secrets.get('redis')

broker_url = redis.get('broker_url')
result_backend = redis.get('result_backend')

# task_annotations = {'*': {'rate_limit': '100/m'}}

timezone = 'America/New_York'
beat_schedule = {
    'status_report': {
        'task': 'message',
        'schedule': 60.0,  # Every 30 seconds
        'args': ["All ok"]
    },

    # 'index_dose_reports': {
    #     'task': 'index_dose_reports',
    #     'schedule': 5.0 * 60.0,  # Every 5 minutes
    #     'args': (orthanc, splunk),
    #     'kwargs': { 'timerange': ("-10m", "now") }
    # },

    # 'index_series': {
    #     'task': 'index_series',
    #     'schedule': 5.0 * 60.0,
    #     'args': (orthanc, splunk),
    #     'kwargs': {'splunk_index': 'dose_reports',
    #                'timerange': ("-10m", "now")
    #               }
    #     }

}
