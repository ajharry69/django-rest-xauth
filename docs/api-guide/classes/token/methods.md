# Methods
## get_claims(token=None, encrypted: bool)
**Type:** `dict`

Returns a `dict` of JWT `token` claims.

## get_payload(token=None, encrypted: bool)
**Type:** `dict`

Returns payload from `token`'s JWT claims.

## refresh()
**Type:** `dict`

Recreates tokens(normal and encrypted). Re-initializes [`normal`][properties-normal-url] and 
[`encrypted`][properties-encrypted-url] properties and returns `dict` of [`tokens`][properties-tokens-url].

[properties-tokens-url]: /api-guide/classes/token/properties/#tokens
[properties-normal-url]: /api-guide/classes/token/properties/#normal
[properties-encrypted-url]: /api-guide/classes/token/properties/#encrypted