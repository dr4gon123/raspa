# config application classification-scope

Configure application classification scopes.

## Syntax

```
config application classification-scope
    Description: Configure application classification scopes.
    edit <name>
        set comment {var-string}
    next
end
```

## Parameters

+-----------+-----------------------------------+------------+---------+---------+
| Parameter | Description                       | Type       | Size    | Default |
+===========+===================================+============+=========+=========+
| comment   | Comments.                         | var-string | Maximum |         |
|           |                                   |            | length: |         |
|           |                                   |            | 255     |         |
+-----------+-----------------------------------+------------+---------+---------+
| name      | Application classification scope  | string     | Maximum |         |
|           | name.                             |            | length: |         |
|           |                                   |            | 35      |         |
+-----------+-----------------------------------+------------+---------+---------+

