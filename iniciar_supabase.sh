#!/bin/bash
set -a
source .env
set +a

echo "=================================================="
echo "  Iniciando Control Financiero (Supabase)..."
echo "=================================================="
python3 web_pagos_supabase.py
