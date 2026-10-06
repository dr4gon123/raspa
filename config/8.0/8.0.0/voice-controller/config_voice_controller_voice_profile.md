# config voice-controller voice-profile

Configure FortiVoice voice profile.

## Syntax

```
config voice-controller voice-profile
    Description: Configure FortiVoice voice profile.
    edit <name>
        set login-passwd {password}
        set login-passwd-override [enable|disable]
    next
end
```

## Parameters

+-----------------------+-----------------------------------+--------------------+--------------------+--------------------+
| Parameter             | Description                       | Type               | Size               | Default            |
+=======================+===================================+====================+====================+====================+
| login-passwd          | Login password of managed         | password           | Not Specified      |                    |
|                       | FortiVoice.                       |                    |                    |                    |
+-----------------------+-----------------------------------+--------------------+--------------------+--------------------+
| login-passwd-override | Enable/disable overriding the     | option             | \-                 | disable            |
|                       | admin administrator password for  |                    |                    |                    |
|                       | a managed FortiVoice with the     |                    |                    |                    |
|                       | FortiGate admin administrator     |                    |                    |                    |
|                       | account password.                 |                    |                    |                    |
+-----------------------+-----------------------------------+--------------------+--------------------+--------------------+
|                       | +-------------+--------------------------------------------------------+                         |
|                       | | Option      | Description                                            |                         |
|                       | +=============+========================================================+                         |
|                       | | *enable*    | Override a managed FortiVoice\'s admin administrator   |                         |
|                       | |             | password.                                              |                         |
|                       | +-------------+--------------------------------------------------------+                         |
|                       | | *disable*   | Use the managed FortiVoice admin administrator account |                         |
|                       | |             | password.                                              |                         |
|                       | +-------------+--------------------------------------------------------+                         |
+-----------------------+-----------------------------------+--------------------+--------------------+--------------------+
| name                  | FortiVoice Profile name.          | string             | Maximum length: 35 |                    |
+-----------------------+-----------------------------------+--------------------+--------------------+--------------------+

