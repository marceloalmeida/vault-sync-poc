#!/usr/bin/env python3

from argparse import ArgumentParser
import hvac
from progress.bar import ShadyBar
from progress.spinner import PixelSpinner, Spinner
import re

def parse_args():
    '''Initialization of global variables'''
    parser = ArgumentParser(description="Vault to Vault Sync")
    parser.add_argument('--source-vault-url', metavar='URL', type=str, required=True,
                        help='Vault URL to copy secrets from')
    parser.add_argument('--source-vault-token', metavar='Token', type=str, required=True,
                        help='Vault token to copy secrets from')
    parser.add_argument('--source-vault-mount', metavar='Mount', type=str, default='secret/',
                        help='Vault mount to copy secrets from')
    parser.add_argument('--target-vault-url', metavar='URL', type=str, required=True,
                        help='Vault URL to copy secrets from')
    parser.add_argument('--target-vault-token', metavar='Token', type=str, required=True,
                        help='Vault token to copy secrets from')
    parser.add_argument('--target-vault-mount', metavar='Mount', type=str, default='secret/',
                        help='Vault mount to copy secrets from')
    args = parser.parse_args()

    return args

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

if __name__ == '__main__':

    cfg = parse_args()

    client_old = hvac.Client(url=cfg.source_vault_url, token=cfg.source_vault_token)
    client_new = hvac.Client(url=cfg.target_vault_url, token=cfg.target_vault_token)

    old_kv_secrets = list_secrets(client_old, cfg.source_vault_mount)

    bar = ShadyBar('Copying', max=len(old_kv_secrets), suffix=global_suffix)
    for old_secret in old_kv_secrets:
        data = client_old.read(old_secret)["data"]
        client_new.write(lreplace(cfg.source_vault_mount, cfg.target_vault_mount, old_secret), **data)
        bar.suffix = global_suffix + ' - ' + old_secret
        bar.next()

    bar.finish()
