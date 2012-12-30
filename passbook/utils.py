import tempfile


def write_tempfile(data):
    '''
    Creates a tempory file and writes to it.
    Returns the filepath of the file as a string.
    '''
    temp_file = tempfile.mkstemp()
    with open(temp_file[1], 'wb') as f:
        f.write(data)
    return temp_file[1]
