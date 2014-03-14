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

Then, you can find example in examples dir. In simple case, ``run-maria`` will start Maria System.  
You also can specify options by yourself like ``run-maria --debug`` or ``run-maria -p 22 --host 0.0.0.0``.  
Get options define use this command ``run-maria -h``.  
And ``run-maria --host-key=./examples/host.key -i file:./examples/ssh_interface.py#NGSSHInterface`` will start maria system with all examples.

Anyway, I think single process will be ok in production environment with supervisord or something like that.  

## Maybe a bug

I disable gevent subprocess monkey patch because I found the execute command function can not exit as I expect, can anyone test it?

## Thanks

[gevent https://github.com/surfly/gevent/](https://github.com/surfly/gevent/)  
[paramiko https://github.com/paramiko/paramiko/](https://github.com/paramiko/paramiko/)  

