import logging
from webob import exc
from webob import Request, Response

log = logging.getLogger("switcheroo")

def parseURL(raw_input):
	"""
	Read the first pattern out of the input matching
	a url of the general form [subdomain.]?[domain].[tld][.cc]?

	"""

	import re
	pattern = re.compile("[\w]+[\.]?[\w]+[\.][\w\w]+[\.]?[\w\w]+")
	result = pattern.match(raw_input)
	if result:
		return "http://" + result.group(0)
	else:
		return None

class Switcheroo(object):
	"""
	WSGI Application that can be redirected.

	"""

	def __init__(self):
		"""

		"""

		self.default_target = ""
		self.current_target = ""

	def __call__(self, environ, start_response):
		"""
		Delegates requests to the proper method handler.

		"""

		req = Request(environ)
		path = req.path_info
		method = None
		try:
			try:
				method = getattr(self, '_%s' % req.method.lower())
			except AttributeError:
				#
				raise exc.HTTPBadRequest('Not implemented.')
			response = method(req, path)
		except exc.HTTPException, e:
			response = e
		return response(environ, start_response)

	def _get(self, request, path):
		res = Response()
		if path == "/":
			res = exc.HTTPSeeOther(location=self.current_target)
		else:
			url = parseURL(path[1:])
			if url:
				self.current_target = url
			print url
			res = exc.HTTPSeeOther(location=self.current_target)
		return res

if __name__ == '__main__':
	import optparse
	parser = optparse.OptionParser(usage='%prog --port=PORT')
	parser.add_option(
		'-p', '--port',
		default='8080',
		dest='port',
		type='int',
		help='Port to serve on (default 8080)')
	options, args = parser.parse_args()

	app = Switcheroo()
	from wsgiref.simple_server import make_server
	httpd = make_server('', options.port, app)
	print 'switcheroo serving on port %s' % options.port
	httpd.serve_forever()


