# config telemetry-controller application custom

Configure FortiTelemetry custom applications.

## Syntax

```
config telemetry-controller application custom
    Description: Configure FortiTelemetry custom applications.
    edit <app-name>
        set app-address {var-string}
        set comment {var-string}
    next
end
```

## Parameters

+-------------+-----------------------------------+------------+---------+---------+
| Parameter   | Description                       | Type       | Size    | Default |
+=============+===================================+============+=========+=========+
| app-address | Application URL.                  | var-string | Maximum |         |
|             |                                   |            | length: |         |
|             |                                   |            | 4095    |         |
+-------------+-----------------------------------+------------+---------+---------+
| app-name    | Application name.                 | string     | Maximum |         |
|             |                                   |            | length: |         |
|             |                                   |            | 79      |         |
+-------------+-----------------------------------+------------+---------+---------+
| comment     | Comment.                          | var-string | Maximum |         |
|             |                                   |            | length: |         |
|             |                                   |            | 255     |         |
+-------------+-----------------------------------+------------+---------+---------+

