#!/usr/bin/env python3

import config as cfg
import hvac
from progress.bar import ShadyBar
from progress.spinner import PixelSpinner, Spinner
import re

global_suffix='%(index)d/%(max)d - %(percent).1f%% - %(avg).4f - %(elapsed)ds - %(eta)ds'

def lreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)

def list_secrets(client, path, result_list=[], spinner=Spinner("Loading secrets paths ")):
    list_secrets_result = client.list(path=path)
    for secret in list_secrets_result["data"]["keys"]:
        if secret.endswith("/"):
            list_secrets(client, path+secret, result_list, spinner=spinner)
        else:
            result_list.append(path+secret)
        spinner.next()

    return result_list

client_old = hvac.Client(url=cfg.old["url"], token=cfg.old["token"])
client_new = hvac.Client(url=cfg.new["url"], token=cfg.new["token"])

old_kv_secrets = list_secrets(client_old, cfg.old["mount"])

bar = ShadyBar('Copying', max=len(old_kv_secrets), suffix=global_suffix)
for old_secret in old_kv_secrets:
    data = client_old.read(old_secret)["data"]
    client_new.write(lreplace(cfg.old["mount"], cfg.new["mount"], old_secret), **data)
    bar.suffix = global_suffix + ' - ' + old_secret
    bar.next()

bar.finish()
