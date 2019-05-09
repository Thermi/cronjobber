#! /bin/env python3

"""
    Cron jobber that takes tasks to execute at a certain time and executes them.
    Copyright (C) 2019  Noel Kuntze <noel.kuntze@thermi.consulting>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the    
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import datetime
import threading
import time

class CronJobber():
    """
    Store and manage a time ordered list with jobs to run. It runs the jobs at the given time, assuming it is in the future.
    """
    class Job():
        """
        This defines a job to run.
        """
        def __init__(self, start_time, func, args):
            self.time = start_time
            self.func = func
            self.args = args

        def __repr__(self):
            return """Execute at %s""" % (self.time)

        def run(self):
            self.func(self.args)

        def get_time(self):
            return self.time

    def __init__(self):
        self.__job_queue = []
        self.__lock = threading.RLock()
        self.__wakeup_thread = None

    def add_job(self, start_time: datetime.datetime, func, args):
        with self.__lock:
            self.__job_queue.append(self.Job(start_time, func, args))
            self.__job_queue.sort(key=lambda x: x.time)
            # check what the next job is and if it's later, reschedule for the now next job
            if self.__job_queue[0].get_time() > start_time and self.__wakeup_thread:
                self.__wakeup_thread.cancel()

                self.__wakeup_thread = threading.Timer(self.__get_seconds_to_next_wakeup, self.run_job)
                self.__wakeup_thread.start()

    def get_lock(self):
        return self.__lock

    def get_job_queue__no_lock(self):
        return self.__job_queue

    def remove_job_no_lock(self, index):
        self.__job_queue.pop(index)

    def get_next_wakeup_time(self):
        with self.__lock:
            if self.__job_queue:
                return self.__job_queue[0].get_time()
        return datetime.date.max

    def __get_seconds_to_next_wakeup(self):
        if self.__job_queue:
            return (self.__job_queue[0].get_time() - datetime.datetime.now()).total_seconds()
        else:
            return None

    def run_job(self, check_time=False):
        with self.__lock:
            if self.__job_queue:
                next_job = self.__job_queue[0]
                if check_time:
                    if next_job.get_time() <= datetime.datetime.now():
                        self.__job_queue.pop(0)
                        next_time = self.__get_seconds_to_next_wakeup()
                        if next_time:
                            self.__wakeup_thread = threading.Timer(next_time, self.run_job)
                            self.__wakeup_thread.start()
                        return next_job.run()
                else:
                    self.__job_queue.pop(0)
                    next_time = self.__get_seconds_to_next_wakeup()
                    if next_time:
                        self.__wakeup_thread = threading.Timer(next_time, self.run_job)
                        self.__wakeup_thread.start()
                    return next_job.run()

if __name__ == '__main__':
    def test(funcs_and_args: tuple):
        print("%s: %s" % (funcs_and_args[1][0], datetime.datetime.now()))

    print(datetime.datetime.now())
    CRON = CronJobber()
    CRON.add_job(datetime.datetime.now()+datetime.timedelta(seconds=1), test, ((print, ), (1, )))
    CRON.add_job(datetime.datetime.now()+datetime.timedelta(seconds=10), test, ((print, ), (4, )))
    CRON.add_job(datetime.datetime.now()+datetime.timedelta(seconds=13), test, ((print, ), (5, )))
    CRON.add_job(datetime.datetime.now()+datetime.timedelta(seconds=16), test, ((print, ), (6, )))
    CRON.add_job(datetime.datetime.now()+datetime.timedelta(seconds=3), test, ((print, ), (3, )))
    print()
    print(datetime.datetime.now())
    print()
    time.sleep(20)
