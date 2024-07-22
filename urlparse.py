# coding: utf8
# This module is intended for replacement standart urlparse Python module. 
# It uses RFC 3986 URI scheme description.
# The main benefints on this module is ability to simple add/delete 
# query arguments. 
# Also other url fragments are changeble.
import re
from collections import OrderedDict

def parse_url(url):
    """
    Parse url into 7 parts: 
    <scheme>://<username>:<password><domain>/<path>?<query>#<fragment>
    :return: ParsedUrl object
    """
    
    _implicit_encoding = 'ascii'
    _implicit_errors = 'strict'

    def _noop(obj):
        return obj

    def _encode_result(obj, encoding=_implicit_encoding,
                            errors=_implicit_errors):
        return obj.encode(encoding, errors)


    def _decode_args(args, encoding=_implicit_encoding,
                        errors=_implicit_errors):
        return tuple(x.decode(encoding, errors) if x else '' for x in args)


    def _coerce_args(*args):
        # Invokes decode if necessary to create str args
        # and returns the coerced inputs along with
        # an appropriate result coercion function
        #   - noop for str inputs
        #   - encoding function otherwise
        str_input = isinstance(args[0], str)
        for arg in args[1:]:
            # We special-case the empty string to support the
            # "scheme=''" default argument to some functions
            if arg and isinstance(arg, str) != str_input:
                raise TypeError("Cannot mix str and non-str arguments")
        if str_input:
            return args + (_noop,)
        return _decode_args(args) + (_encode_result,)
    
    
    if not isinstance(url, str):
        raise ValueError('Url must be string')
    if isinstance(url, str):
        scheme=""
        url, scheme, _coerce_result = _coerce_args(url, scheme)
    # url scheme must begin with a letter                     
    regexp = (r'^(?P<scheme>[a-z][\w\.\-\+]+)?:(//)?'
              r'(?:(?P<username>\w+):(?P<password>[\w\W]+)@|)'
              r'(?P<domain>[\w-]+(?:\.[\w-]+)*)(?::(?P<port>\d+))?/?'
              r'(?P<path>\/[\w\.\/]+)?(?P<query>\?[\w\.*!=&@%;:/+-]+)?'
              r'(?P<fragment>#[\w-]+)?$')
    match = re.search(regexp, url.strip())
    if match is None:
        raise ValueError('Incorrent url: {0}'.format(url))
    url_parts = match.groupdict()
    return ParsedUrl(url_parts['scheme'], 
                     url_parts['username'], 
                     url_parts['password'], url_parts['domain'], 
                     url_parts['port'],
                     url_parts['path'], url_parts['query'], 
                     url_parts['fragment'])


class ParsedUrl(object):
    """Parsed url with mutable attributes"""
    def __init__(self, scheme, username, password, domain, port, path, query, 
                 fragment):
        self.scheme = scheme
        self.username = username
        self.password = password
        self.domain = domain
        self.port = port
        self.path = path
        if query is not None:
            try:
                self.query = OrderedDict()
                query = query.replace('?', '')
                query_items = query.split('&') if '&' in query \
                              else query.split(';')
                for k, v in map(lambda x: x.split('='), query_items):
                    if k in self.query:
                        if isinstance(self.query[k], list):
                            self.query[k].append(v)
                        else:
                            self.query[k] = [self.query[k], v]
                    else:
                        self.query[k] = v
            except ValueError:
                raise ValueError('Incorrect query: {0}'.format(query))
        else:
            self.query = {}
        if fragment is not None:
            self.fragment = fragment.replace('#', '')
        else:
            self.fragment = fragment
        
    def geturl(self):
        """Return url"""
        url = ''
        if self.scheme is not None:
            url = '{0}://'.format(self.scheme)
        if self.username is not None:
            url = '{0}{1}'.format(url, self.username)
        if self.password is not None:
            url = '{0}:{1}@'.format(url, self.password)
        if self.domain is not None:
            if self.port is not None:
                url = '{0}{1}:{2}/'.format(url, self.domain, self.port)
            else:
                url = '{0}{1}/'.format(url, self.domain)
        if self.path is not None:
            # delete leading slash from path
            path = self.path.lstrip('/')
            url = '{0}{1}'.format(url, path)
        if self.query:  # self.query is dict
            str_query = ''
            for k, v in self.query.items():
                if isinstance(v, list):
                    str_query = '&'.join('{0}={1}'.format(k, i) for i in v)
                elif str_query:
                    str_query = '{0}&{1}={2}'.format(str_query, k, v)                   
                else:
                    str_query = '{0}={1}'.format(k, v)
            url = '{0}?{1}'.format(url, str_query)
        if self.fragment is not None:
            url = '{0}#{1}'.format(url, self.fragment)
        return url
        
            
        
