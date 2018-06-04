import ruamel_yaml as yaml

# Change this line to point at your project service configs
# with open("../../_secrets/dev_services.yml", "r") as f:
with open("../../_secrets/trusty_services.yml", "r") as f:
        services = yaml.safe_load(f)

splunk_cfg  = services.get('splunk')
orthanc_cfg = services.get('orthanc')
redis_cfg   = services.get('redis')

broker_url     = "redis://{host}:{port}/{broker_db}".format(**redis_cfg)
result_backend = "redis://{host}:{port}/{result_db}".format(**redis_cfg)

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
