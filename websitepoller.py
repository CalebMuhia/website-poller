#!/usr/bin/env python
"""Copyright (C) 2012 Koodilehto osk.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import urllib2
import ssl
import os
import json


APP_NAME = 'Koodilehto Website Poller'
INTERNET_TEST = 'http://www.google.com'

CONFIGFILE = '.websitepollerrc'
CONFIGFILEPATH = os.getenv('HOME') + os.sep + CONFIGFILE
TIMEOUT = 5


try:
    """For Mac OSX use Growl notifier."""
    import gntp.notifier

    notification = gntp.notifier.mini
except ImportError:
    """For Linux try using Pynotigy."""
    try:
        import notify2
        notify2.init(APP_NAME)

        def dbus_out(data):
            n = notify2.Notification(
                'Koodilehto Service Error',
                data
            )

            n.show()

        notification = dbus_out
    except ImportError:
        """All other systems get a printed line."""
        def out(data):
            print data

        notification = out


def poll(sites, useragent, timeout, ok, error):
    """Checks if the given URLs are online. sites - List of URLs to check.
    sites - Website URLs that will be tried.
    useragent - User agent info for the request.
    timeout - Timeout in seconds.
    ok - Function for printing information.
    error - Error reporting function.
    """
    for site in sites:
        ok('Polling ' + site)

        try:
            headers = { 'User-Agent:' : useragent }
            request = urllib2.Request(site, None, headers)
            response = urllib2.urlopen(request, timeout=timeout)
            response.read()
        except urllib2.URLError as e:
            code = str(e.code) if hasattr(e, 'code') else ''
            error(site + ' ' + code)
        except ssl.SSLError as e:
            error(site + ' ' + e.message)
        except Exception as e:
            error(site + ' ' + e.message)
        else:
            ok('OK')


def has_internet():
    """Test if we can connect to the Internet."""
    try:
        urllib2.urlopen(INTERNET_TEST, timeout=TIMEOUT)
        return True
    except urllib2.URLError:
        pass
    return False


def parse_config(filename):
    """Parse the configuration file."""
    try:
        json_data = open(filename, "r")
        data = json.load(json_data)
        json_data.close()
	# Read user agent info.
        try:
            useragent = data['user-agent']
        except KeyError:
            useragent = ""
	# Read website URLs.
        try:
            sites = data['websites']
        except KeyError:
            sites = []
        return (sites, useragent)
    except IOError:
        notification('Please create file ' + filename +
            ' containing the site list in JSON format.')
    except ValueError:
        notification('Please check the contents of your JSON file.')

    return []


if __name__ == '__main__':
    if has_internet():
        (sites, useragent) = parse_config(CONFIGFILEPATH)
        poll(sites, useragent, timeout=TIMEOUT, ok=lambda a: a, error=notification)
