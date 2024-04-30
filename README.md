# Authcord

## Deployment

- Set `USE_PROD` config var
- Set `SRV_URL` config var to the URI of the instance __without__ a trailing slash
- Add `heroku/nodejs` buildpack
- Add postgres addon

## Connectivity
Due to errors in others' code the following issues were ran into, that were out of our control:
- lack of consistency with the UUID as specified in the spec leads to some inconsistent links
- internal errors of others' servers prevents us from posting a comment on their post
- lack of sharing their posts lead to issues relating to properly interacting with posts and comments
- servers missing features that were specified by the spec

## Contributors and Instances
- Abdullah Mohammed
- Amirul Hossain
- Corbin Beck [[nortif8](https://github.com/nortif8)]
  - [https://authcord-8a838051c728.herokuapp.com/](https://authcord-8a838051c728.herokuapp.com/)
  - service prefix: `api`
  - superuser
      - username: `suri`
      - password: `suri`
- Harjot Singh
    - [main instance](https://authcord1399-8a8b104296b1.herokuapp.com/)
    - service prefix: `api`
    - superuser:
        - username: `goku`
        - password: `123456`
    - References:
        -For the github activity user story, got the inspiration from this repo: https://github.com/vardansaini/CMPUT404-project-socialdistribution/blob/master/backend/follow/views.py
- Sam Chan

## Contributors / Licensing

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle.

All text is licensed under the CC-BY-SA 4.0 http://creativecommons.org/licenses/by-sa/4.0/deed.en_US

Contributors:

    Karim Baaba
    Ali Sajedi
    Kyle Richelhoff
    Chris Pavlicek
    Derek Dowling
    Olexiy Berjanskii
    Erin Torbiak
    Abram Hindle
    Braedy Kuzma
    Nhan Nguyen 
