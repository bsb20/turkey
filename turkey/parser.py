import os
import pathlib
import csv
import json
from datetime import datetime, timedelta


def parse_ms(line):
    return float(line.split()[1].strip()) * 1000


def parse_file(params, filepath):
    with open(filepath, 'r') as f:
        for line in f:
            if line.find('datetime') > -1:
                params['starttime'] = datetime.strptime(
                    line.split()[1].strip(), '%Y-%m-%dT%H:%M:%S')
            elif line.find('real') > -1:
                real = parse_ms(line)
                params['real'] = str(real)
                params['endtime'] = params['starttime'] + \
                    timedelta(milliseconds=real)
            elif line.find('user') > -1:
                params['user'] = str(parse_ms(line))
            elif line.find('sys') > -1:
                params['sys'] = str(parse_ms(line))


class Parser():
    def __init__(self, args):
        self.out_dir = args.out_dir

        job_files = list(pathlib.Path(self.out_dir).glob('*.job'))
        if len(job_files) == 0:
            raise ValueError('Could not find job file!')

        with open(str(job_files[0]), 'r') as f:
            self.jobs = json.load(f)

    def parse(self):
        counter = 0
        keys = self.jobs[0].keys()
        keys.extend(['starttime', 'endtime', 'id', 'real', 'user', 'sys'])

        with open(os.path.join(self.out_dir, 'parsed.csv'), 'w') as f:
            writer = csv.DictWriter(
                f, fieldnames=keys, delimiter=',')
            writer.writeheader()

            for job in self.jobs:
                job['id'] = counter

                parse_file(job, os.path.join(
                    self.out_dir, 'out', str(counter), 'task.out'))

                writer.writerow(job)
                counter += 1
