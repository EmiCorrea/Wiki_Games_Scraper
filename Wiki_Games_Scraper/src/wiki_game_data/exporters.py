from scrapy.exporters import JsonItemExporter

class GameItemExporter(JsonItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(file)

    def start_exporting(self):
        self.file.write("[")

    def finish_exporting(self):
        self.file.write("]")

    def export_item(self, item):
        if self.first_item:
            self.first_item = False
        else:
            self.file.write(",\n\n")
