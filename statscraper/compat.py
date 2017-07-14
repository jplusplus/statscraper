import six

if six.PY3:
	from json import JSONDecodeError
	unicode = str
elif six.PY2:
	unicode = unicode
	JSONDecodeError = ValueError
