Maria System
=============

A way to serve git repos through ssh protocol like Github.

## Requirements

You can install requirements from requirements.txt with ``pip install -r requirements.txt``.

## Features

1. support git clone/push/pull with ssh protocol.
2. auth by pub key, you can write your own verify code to use mysql and others easily.
3. people always like coroutine.
4. safely, only allow commands in white list.

## Run it

``python run.py`` will start Maria System, you can specify host and port by yourself like  
``python run.py -p 22 --host 0.0.0.0``, default port is 2200.

anyway, I think single process will be ok in production environment with supervisord or something like that.

## Maybe is a bug

I disable gevent subprocess monkey patch because I found the execute command function can not exit as I expect, can anyone test it?

## Thanks

[gevent https://github.com/surfly/gevent/](https://github.com/surfly/gevent/)  
[paramiko https://github.com/paramiko/paramiko/](https://github.com/paramiko/paramiko/)  

