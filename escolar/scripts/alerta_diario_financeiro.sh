#!/bin/bash
source /home/ubuntu/.virtualenvs/escolar/bin/activate
PYTHONIOENCODING=utf_8 python /var/www/projetos/escolar/manage.py alerta_diario_financeiro $1