from wiki_game_data.exporters import GameItemExporter
import json
import codecs

class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('Wiki_games_data.json', 'w', encoding='utf-8')

    def open_spider(self, spider):
        self.exporter = GameItemExporter(self.file)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        line = json.dumps(dict(item), ensure_ascii=False,
            indent = 4,
            sort_keys = False,
            separators = (',', ': ')
        )
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()