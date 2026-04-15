import sys
import os

project_home = "/home/margoty/app_supabase"
if project_home not in sys.path:
    os.environ["SUPABASE_URL"] = "https://zsbbyvqcxqwhmydztbax.supabase.co"
    os.environ["SUPABASE_ANON_KEY"] = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
    )
    os.environ["SUPABASE_SERVICE_KEY"] = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
    )
    os.environ["ADMIN_USUARIOS"] = "argoty.martin@gmail.com,martin.argoty@hotmail.com"
    os.environ["CORREO_REMITENTE"] = "argoty.martin@gmail.com"
    os.environ["CORREO_CLAVE_APP"] = "vbzs yrtk auhr quya"

if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from web_pagos_supabase import app as application
