#!/bin/bash
source /home/ubuntu/.virtualenvs/escolar/bin/activate
PYTHONIOENCODING=utf_8 /var/www/projetos/escolar/escolar/manage.py alerta_aniversariantes_do_dia $1