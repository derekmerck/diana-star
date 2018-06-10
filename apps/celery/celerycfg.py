import os

broker_host = os.environ.get("BROKER_HOST", "localhost")
broker_port = os.environ.get("BROKER_PORT", "6379")
broker_db   = os.environ.get("BROKER_DB", "1")
result_db   = os.environ.get("BROKER_HOST", "2")
broker_pw   = os.environ.get("BROKER_PW", "passw0rd!")

broker_url     = "redis://{broker_host}:{broker_port}/{broker_db}".format(
                    broker_host=broker_host,
                    broker_port=broker_port,
                    broker_db=broker_db )
result_backend = "redis://{broker_host}:{broker_port}/{result_db}".format(
                    broker_host=broker_host,
                    broker_port=broker_port,
                    result_db=result_db )

timezone = 'America/New_York'
