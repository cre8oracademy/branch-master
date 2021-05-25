#!/usr/bin/env python
# create a load of test private messages

import requests
from django.test.client import Client

words="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

def get_some_words():
	""" A random selection of words"""
	import random
	wlist = words.split()
	l = random.randint(1, len(wlist))
	return " ".join(wlist[0:l])
	

def send_a_pm(touser, fromuser, frompass):
	c=Client()
	c.login(username=fromuser, password=frompass)
	response=c.post("/pm/compose/", {'to':touser, 'body':get_some_words()})		
	print response.content
	
	
send_a_pm('ben', 'garvin', 'garvin')