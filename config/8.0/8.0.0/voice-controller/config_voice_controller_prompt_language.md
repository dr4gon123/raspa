# config voice-controller prompt-language

Configure Prompt Language.

## Syntax

```
config voice-controller prompt-language
    Description: Configure Prompt Language.
    edit <name>
        set description {string}
    next
end
```

## Parameters

+-------------+-----------------------------------+--------+---------+---------+
| Parameter   | Description                       | Type   | Size    | Default |
+=============+===================================+========+=========+=========+
| description | Description.                      | string | Maximum |         |
|             |                                   |        | length: |         |
|             |                                   |        | 63      |         |
+-------------+-----------------------------------+--------+---------+---------+
| name        | Voice Prompt Language.            | string | Maximum |         |
|             |                                   |        | length: |         |
|             |                                   |        | 35      |         |
+-------------+-----------------------------------+--------+---------+---------+

