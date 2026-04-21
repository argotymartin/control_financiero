import sys

project_home = "/home/margoty/app_supabase"
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from web_pagos_supabase import app as application
