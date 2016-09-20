'''Module to provide streaming of sqlalchemy queries back to client'''
import simplejson
from flask import Response

def stream_qry_csv(cols, qry, api_obj):
    def generate():
        yield ','.join([col if isinstance(col, basestring) else col.key for col in cols]) + '\n'
        for row in qry:
            row = [u'"{}"'.format(x) if isinstance(x, basestring) else str(x) for x in list(row)]
            yield u','.join(row) + u'\n'
    return Response(generate(), mimetype='text/csv')

def stream_qry(tables, cols, data, api_obj):
    ''' Based on https://github.com/al4/orlo/blob/1b3930bae4aa37eb51aed33a97c088e576cb5a99/orlo/route_api.py#L285-L311'''
    def generate(tables):
        headers = [col if isinstance(col, basestring) else col.key for col in cols]
        inf = float('inf')

        """
        A lagging generator to stream JSON so we don't have to hold everything in memory
        This is a little tricky, as we need to omit the last comma to make valid JSON,
        thus we use a lagging generator, similar to http://stackoverflow.com/questions/1630320/
        """
        yield u'{'

        rows = data.__iter__()
        try:
            prev_row = next(rows)  # get first result
        except StopIteration:
            # StopIteration here means the length was zero, so yield a valid releases doc and stop
            yield u'''"data": [],
                     "headers": {},
                     "source": {},
                     "subs": {},
                     "limit": {},
                     "warnings": {}
            '''.format(simplejson.dumps(list(headers)), simplejson.dumps([table.info(api_obj) for table in tables]), simplejson.dumps(api_obj.subs),
                       api_obj.limit,
                       simplejson.dumps(api_obj.warnings)) + u'}'
            raise StopIteration

        # We have some releases. First, yield the opening json
        yield u'"data": ['

        # Iterate over the releases
        for row in rows:
            yield simplejson.dumps([x if x != inf else None for x in prev_row]) + u', '
            prev_row = row

        # Now yield the last iteration without comma
        yield simplejson.dumps([x if x != inf else None for x in prev_row])

        yield u'''], "headers": {},
                 "source": {},
                 "subs": {},
                 "limit": {},
                 "warnings": {}
        '''.format(simplejson.dumps(list(headers)), simplejson.dumps([table.info(api_obj) for table in tables]), simplejson.dumps(api_obj.subs),
                   api_obj.limit,
                   simplejson.dumps(api_obj.warnings)) + u'}'

    return Response(generate(tables), content_type='application/json')
