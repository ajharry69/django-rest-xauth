# Endpoints
`X-Forwarded-For` header with request device's **ip-address** is required if access, failed sign-in attempts or password
 reset logging is expected at granular level.

## Registration/Sign-up
**Default:** `signup/`

**Method:** `POST`

**Expected Data:** would depend on your profile serializer setting. Default serializer's expected data payload is.
```json
{
  "username": "",
  "email": "",
  "provider": null,
  "surname": "",
  "first_name": "",
  "last_name": "",
  "mobile_number": "",
  "date_of_birth": null,
  "password": ""
}
```

### Request Headers
1. **Content-Type:** `application/json`

## Login/Sign-in
**Default:** `signin/`

**Method:** `POST`

**Expected Data:** `username` and `password` or None(no POST request data) when `Authorization` header with 
[basic-auth][basic-auth-scheme] credentials provided.

### Request Headers
1. **Content-Type:** `application/x-www-form-urlencoded`
2. **Authorization:** `Basic <credentials>` or None(no authorization header) when `username` and `password` POST 
request data is provided.

## Logout/Sign-out
**Default:** `signout/`

**Method:** `POST`

**Expected Data:** None

### Request Headers
1. **Content-Type:** `application/x-www-form-urlencoded`
2. **Authorization:** `Bearer <encrypted-access-token>` or `Basic <credentials>`

## Profile
**Default:** `profile/{id}/`

**Methods:** `GET`, `PUT`, `PATCH` or `DELETE`

**Expected Data:** Only necessary for `PUT` and `PATCH` methods.

**NOTE:** `GET` is by default allowed to everyone(even non-authenticated users) while `PUT`, `PATCH` or `DELETE` is 
restricted to the account owner(determined by the credentials provided in `Authorization` header) or the superuser.

### Request Headers
1. **Content-Type:** `application/json`(subject to above **expected data** condition)
2. **Authorization:** `Bearer <encrypted-access-token>` or `Basic <credentials>`

## Verification code request
**Default:** `verification-code/request/`

**Method:** `POST`

**Expected Data:** None

### Request Headers
1. **Content-Type:** `application/x-www-form-urlencoded`
2. **Authorization:** `Bearer <encrypted-verification-token>` or `Basic <credentials>`

## Verification code verification
**Default:** `verification-code/verify/`

**Method:** `POST`

**Expected Data:** `code=<sent-verification-code>` 

### Request Headers
1. **Content-Type:** `application/x-www-form-urlencoded`
2. **Authorization:** `Bearer <encrypted-verification-token>` or `Basic <credentials>`

## Password reset request
**Default:** `password-reset/request/`

**Method:** `POST`

**Expected Data:** `email=<used-during-account-registration>`. Temporary password will be sent to it.

### Request Headers
1. **Content-Type:** `application/x-www-form-urlencoded`

## Password reset verification
**Default:** `password-reset/verify/`

**Method:** `POST`

**Expected Data:** (`temporary_password=<sent-password>` or `old_password=<sent-password>`) and `new_password=<value>` 

### Request Headers
1. **Content-Type:** `application/x-www-form-urlencoded`
2. **Authorization:** `Bearer <encrypted-password-reset-token>` or `Basic <credentials>`

## Activation request
**Default:** `activation/request/`

**Method:** `POST`

**Expected Data:** `username=<username/email-address>` of the user whose account is inactive.

**Return Data:** user **_activation token(s)_** and list of possible account deactivation schemes/methods available 
for the user in question.

### Request Headers
1. **Content-Type:** `application/x-www-form-urlencoded`

## Activation verification
**Default:** `activation/verify/`

**Method:** `POST`

**Expected Data:** `answer=<security-question-answer>` 

### Request Headers
1. **Content-Type:** `application/x-www-form-urlencoded`
2. **Authorization:** `Bearer <encrypted-activation-token>` or `Basic <credentials>` 

## Add/attach security question
**Default:** `security-question/add/`

**Method:** `POST`

**Expected Data:** `question|id|question_id=<value>` and `answer|question_answer=<value>`. `question`, `id` or 
`question_id` can either be one of admin/superuser-registered security question's id or case-sensitive name.

**Assumption:** user will configure(add/attach) a security question after creating a verified account(more like an 
account update).

### Request Headers
1. **Content-Type:** `application/x-www-form-urlencoded`
2. **Authorization:** `Bearer <encrypted-access-token>` or `Basic <credentials>` 

## Retrieve security questions
**Default:** `security-questions/`

**Method:** `GET`

**NOTE:** Authorization is not necessary for this.

[basic-auth-scheme]: https://en.wikipedia.org/wiki/Basic_access_authentication