from rest_framework import renderers
import csv
import io

class CSVRenderer(renderers.BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = [data]

        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)

        return csv_buffer.getvalue()