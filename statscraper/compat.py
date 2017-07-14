import six

if six.PY3:
    from io import BytesIO as StringIO
    from json import JSONDecodeError
    unicode = str
elif six.PY2:
    from StringIO import StringIO
    unicode = unicode
    JSONDecodeError = ValueError
