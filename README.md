Maria System
=============

A way to serve git repos through ssh and http protocol like Github.

## Requirements

You can install requirements from requirements.txt with ``pip install -r requirements.txt``.

## Features

1. support git clone/push/pull with ssh and http protocol.
2. auth by pub key, you can write your own verify code to use mysql and others easily.
3. people always like coroutine, powered by gevent.
4. safely, only allow commands in white list.

## Run it

Firstly, you have to install requirements and maria itself in your python environment like:  
```bash
pip install -r requirements
python setup.py develop
```

Then, you can find example in examples dir. In simple case, ``maria`` will start Maria System.  
You also can specify options by yourself like ``maria --debug`` or ``maria -b 0.0.0.0:2200``.  
Get options define use this command ``maria -h``.  
And ``maria -k host.key -b 127.0.0.1:2200 -w async run_socket:app`` will start maria system with all examples.

Anyway, I think single process will be ok in production environment with supervisord or something like that.  

## Test

First, nosetests is required. Get it:
```bash
# pip install nose
```
Then, this will run tests:
```bash
$ cd /path/to/maria/tests
$ nosetests -v
```

## Maybe a bug

I disable gevent subprocess monkey patch because I found the execute command function can not exit as I expect, can anyone test it?

## Thanks

[gevent https://github.com/surfly/gevent/](https://github.com/surfly/gevent/)

[paramiko https://github.com/paramiko/paramiko/](https://github.com/paramiko/paramiko/)
