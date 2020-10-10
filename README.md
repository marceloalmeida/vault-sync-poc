# Simple script to copy secrets from one Hashicorp Vault instance to another.

## Origin
### Policy
```hcl
# dump-read
path "secret/*" {
  capabilities = ["read", "list"]
}
```

```sh
vault token create -policy=dump-read -period=30m
```

## Destiny
### Policy
```hcl
# dump-create
path "secret/*" {
  capabilities = ["create", "update"]
}
```

```sh
vault token create -policy=dump-create -period=30m
```
