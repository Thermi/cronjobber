# cronjobber

### How to use?

Just import it into your program and add the jobs that should be run.

### Example

def example_function(input_string):
    print(input_string)

CRON = CronJobber()
CRON.add_job(datetime.datetime.now()+datetime.timedelta(seconds=1), print, 1)
CRON.add_job(datetime.datetime.now()+datetime.timedelta(seconds=2), example_function, "My example string")