# config application classification

Configure application classifications.

## Syntax

```
config application classification
    Description: Configure application classifications.
    edit <name>
        set color {integer}
        set scope {string}
        set tag {string}
    next
end
```

## Parameters

+-----------+-----------------------------------+---------+---------+---------+
| Parameter | Description                       | Type    | Size    | Default |
+===========+===================================+=========+=========+=========+
| color     | Color of the application          | integer | Minimum | 0       |
|           | classification tag on the GUI.    |         | value:  |         |
|           |                                   |         | 0       |         |
|           |                                   |         | Maximum |         |
|           |                                   |         | value:  |         |
|           |                                   |         | 32      |         |
+-----------+-----------------------------------+---------+---------+---------+
| name      | Application classification name.  | string  | Maximum |         |
|           |                                   |         | length: |         |
|           |                                   |         | 35      |         |
+-----------+-----------------------------------+---------+---------+---------+
| scope     | Application classification scope. | string  | Maximum |         |
|           |                                   |         | length: |         |
|           |                                   |         | 35      |         |
+-----------+-----------------------------------+---------+---------+---------+
| tag       | Application classification tag.   | string  | Maximum |         |
|           |                                   |         | length: |         |
|           |                                   |         | 3       |         |
+-----------+-----------------------------------+---------+---------+---------+

