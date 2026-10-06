# config router vrf

Configure VRF name alias.

## Syntax

```
config router vrf
    Description: Configure VRF name alias.
    edit <id>
        set name {string}
    next
end
```

## Parameters

+-----------+-----------------------------------+--------+---------+---------+
| Parameter | Description                       | Type   | Size    | Default |
+===========+===================================+========+=========+=========+
| id        | VRF ID \<0-511\>.                 | string | Maximum |         |
|           |                                   |        | length: |         |
|           |                                   |        | 7       |         |
+-----------+-----------------------------------+--------+---------+---------+
| name      | Name of VRF ID.                   | string | Maximum |         |
|           |                                   |        | length: |         |
|           |                                   |        | 79      |         |
+-----------+-----------------------------------+--------+---------+---------+

