from django.test import TestCase


# Create your tests here.
from django.contrib.auth import authenticate
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
user = authenticate(username='system', password='system123')
if user is not None:
   logging.debug('TRUE')
   print("Login Successfull")
else:
     logging.debug('False')
