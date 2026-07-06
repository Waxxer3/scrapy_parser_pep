import csv
import datetime
import os

from pep_parse.settings import BASE_DIR
from .constants import RESULTS_DIR


class PepParsePipeline:
    def open_spider(self, spider):
        self.stats = {}

    def process_item(self, item, spider):
        status = item['status']
        self.stats.setdefault(status, 0)
        self.stats[status] += 1
        return item

    def close_spider(self, spider):
        results_dir = os.path.join(BASE_DIR, RESULTS_DIR)
        os.makedirs(results_dir, exist_ok=True)

        now = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        filepath = os.path.join(
            results_dir,
            f'status_summary_{now}.csv'
        )

        rows = [['Status', 'Count']]
        rows.extend(
            [[status, count] for status, count in self.stats.items()]
        )
        rows.append(['Total', sum(self.stats.values())])

        with open(filepath, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
