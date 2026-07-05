import csv
import datetime
import os

from pep_parse.settings import BASE_DIR


class PepParsePipeline:
    def open_spider(self, spider):
        self.stats = {}

    def process_item(self, item, spider):
        status = item.get('status')
        self.stats[status] = self.stats.get(status, 0) + 1
        return item

    def close_spider(self, spider):
        results_dir = os.path.join(BASE_DIR, 'results')
        os.makedirs(results_dir, exist_ok=True)

        now = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        filename = f'status_summary_{now}.csv'
        filepath = os.path.join(results_dir, filename)

        with open(filepath, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Статус', 'Количество'])
            for status, count in self.stats.items():
                writer.writerow([status, count])
            writer.writerow(['Total', sum(self.stats.values())])
