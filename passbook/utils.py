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


def render_pass( p):
    response = HttpResponse(mimetype='application/vnd.apple.pkpass')
    response['Content-Disposition'] = 'attachment; filename=%s.pkpass' % p.type
    z = p.zip()
    response.write(z)
    return response