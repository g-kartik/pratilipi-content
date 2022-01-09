#!/bin/bash

# Start the first process
python manage.py runserver &

# Start the second process
python manage.py rqworker default &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?

