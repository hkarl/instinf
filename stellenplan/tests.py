"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from stellenplan.models import Fachgebiet
from django.contrib.auth.models import User


class SimpleTest(TestCase):
    fixtures=['stellenplan/fixtures/testdata.json']

    ## def test_basic_addition(self):
    ##     """
    ##     Tests that 1 + 1 always equals 2.
    ##     """
    ##     self.assertEqual(1 + 1, 2)

    def setUp(self):
        user = User.objects.create_user ('temp',
                                         'temp@bla.org',
                                         'secret')

    def test_data_loaded(self):
        fg = Fachgebiet.objects.get(pk=2)
        self.assertIsNotNone(fg)

    def test_consistency(self):
        print "testing consistency"
        from django.test import Client
        c = Client()
        response = c.post ('/accounts/login/',
                           {'username': 'temp',
                            'password': 'secret'})

        ## print "====="
        ## print "login:"
        ## print response
        ## print response.status_code
        ## print "====="

        self.assertEqual(response.status_code, 302)

        response = c.get('/stellenplan/konsistenz')
        print response
        self.assertEqual(response,200)
