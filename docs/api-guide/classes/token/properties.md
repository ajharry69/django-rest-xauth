# Properties

## normal
**Type:** `str`

Returns a `str` of unencrypted [JWT][jwt-url] token.

## encrypted
**Type:** `str`

Returns a `str` of encrypted version of [`normal`](#normal) [JWT][jwt-url] token described above.

**NOTE:** `django-rest-xauth`'s authentication class expects this to be the value of a `Authorization` header with 
`Bearer` prefix. For example, `Bearer eyj...`

## tokens
**Type:** `dict`

Returns a `dict` of both **normal** and **encrypted** [JWT][jwt-url] tokens.

## checked_claims
**Type:** `dict`

Contains a dictionary of standard [JWT claims][jwt-std-claims-url] that will be checked/verified for validity during 
token decoding. For example, during authorization when token is provided. `django-rest-xauth` checked claims.

```python
{
    'nbf': 00000000,
    'exp': 00000000,
    'iat': 00000000,
    'sub': 'value',
}
```

## claims
**Type:** `dict`

Contains a combination of `checked_claims` and additional data payload that will be included in the signed 
[JWT][jwt-url] token returned by [`normal`](#normal).

[jwt-url]: https://jwt.io/
[jwt-std-claims-url]: https://www.iana.org/assignments/jwt/jwt.xhtml