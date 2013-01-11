import tempfile
from django.http import HttpResponse


def write_tempfile(data):
    '''
    Creates a tempory file and writes to it.
    Returns the filepath of the file as a string.
    '''
    temp_file = tempfile.mkstemp()
    with open(temp_file[1], 'wb') as f:
        f.write(data)
    return temp_file[1]


def render_pass(p, **kwargs):
    response = HttpResponse(mimetype='application/vnd.apple.pkpass')
    response['Content-Disposition'] = 'attachment; filename=%s.pkpass' % p.type
    for header in kwargs:
        response[header] = kwargs[header]
    z = p.zip()
    response.write(z)
    return response



def to_time_stamp(ts):
    desired_ts = (ts).isoformat()
    idx_for_point = desired_ts.rfind(".")
    desired_ts = desired_ts[:idx_for_point]
    if '+' in desired_ts:
        idx = desired_ts.rfind('+')
        desired_ts = desired_ts[:idx]
    tz = 'Z'
    return desired_ts + tz