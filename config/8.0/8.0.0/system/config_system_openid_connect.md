# config system openid-connect

OpenID connection configuration.

## Syntax

```
config system openid-connect
    Description: OpenID connection configuration.
    set allowed-tenant-id-list <name1>, <name2>, ...
end
```

## Parameters

+------------------------+-----------------------------------+--------+---------+---------+
| Parameter              | Description                       | Type   | Size    | Default |
+========================+===================================+========+=========+=========+
| allowed-tenant-id-list | List of allowed tenant IDs.       | string | Maximum |         |
| `<name>`               |                                   |        | length: |         |
|                        | Allowed tenant ID                 |        | 79      |         |
+------------------------+-----------------------------------+--------+---------+---------+

