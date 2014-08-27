#!/bin/bash
maria -k host.key -b 127.0.0.1:2200 -w async run_socket:app
