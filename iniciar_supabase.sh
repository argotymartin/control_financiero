#!/bin/bash
export SUPABASE_URL='https://zsbbyvqcxqwhmydztbax.supabase.co'
export SUPABASE_ANON_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
export SUPABASE_SERVICE_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU'
export ADMIN_USUARIOS='argoty.martin@gmail.com,martin.argoty@hotmail.com'
export CORREO_REMITENTE='argoty.martin@gmail.com'
export CORREO_CLAVE_APP='vbzs yrtk auhr quya'

echo "=================================================="
echo "  Iniciando Control Financiero (Supabase)..."
echo "=================================================="
python3 web_pagos_supabase.py
