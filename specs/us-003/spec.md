## User Story
As a user, I want to enable an authenticator app for multi-factor authentication so that I can securely access the application, delivering the value outlined in "Implement Multi-Factor Authentication".

## Acceptance Criteria
1. Given a user fails the second-factor authentication, when they provide an incorrect code, then access is denied.

## Out of Scope
- Changes to existing user registration flows.
- Integration with other third-party authentication services.

## Dependencies
- This feature relies on a working authentication system that supports JWT token generation.

## Purpose
This specification aims to enhance the security features of the authentication system by incorporating an authenticator app method for the second factor, making user accounts significantly more secure.