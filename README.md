# SakanaRM: A Collaborative LLM-Assisted Reference Manager
The project features a reference manager that integrates LLM to empower
fully user-controlled reference management. 

## Timeline
From the week of April 29, 2024:

I. A minimum running system (works with pseudo-LLM prompts/keyword tagging) &nbsp;&nbsp;&nbsp;&nbsp;       **3 weeks**

II. Finding an efficient, usable LLM &nbsp;&nbsp;&nbsp;&nbsp;     **1 week**

III. Integration of LLM with modules (involves writing suitable prompts)  &nbsp;&nbsp;&nbsp;&nbsp;        **1 week**

IV. System-level integration -> testing -> review -> optimization and loop…  &nbsp;&nbsp;&nbsp;&nbsp;  **4 weeks**

V. Final product (that fulfills the success metric)    &nbsp;&nbsp;&nbsp;&nbsp;         **by July 15, 2024**

## Features

## Installation
### Prerequisite
- Python 3.9
- Docker (Engine version 27.0.1) 

**How to install Docker**: please follow the [official guide](https://docs.docker.com/engine/install/). 
You can either install Docker Engine or Docker Desktop. Verify critical components are correctly installed by
running commands such as `docker compose version` etc.

If you really want to use a Python interpreter version below 3.9, please find out the following patterns in source code 
and refactor them:
    
Added in Python 3.9:
- New module `from zoneinfo import ZoneInfo` is used instead of `from pytz import timezone` as *tzinfo* object class
- Dictionary merge operator `|` to merge two dictionaries

Added in Python 3.8:
- Assignment operator `:=` to capture sub-expressions inline

## User Documentation
To learn how to use the website, please watch the [tutorial video]().
### Some Important Notices
- Paper titles are NOT unique if uploader is different, but for the same uploader, papers should have unique, non-empty 
titles;
- Tag names are unique. Semicolons, trailing and leading spaces in tag names are not allowed and would be removed by 
system;
- A new paper that is being uploaded does not appear in "My Papers" nor has a detail page until the upload successfully 
completes;

## Developer Documentation
### Important Settings
#### Django:
**STATIC_URL**: part of URL path to request for static files, e.g., "http://localhost:8000/static/a.js" is used to 
request for "a.js" when set to "/static/". Must be the same as in *nginx.conf*.    
**STATIC_ROOT**: directory where static files are collected when command "python manage.py collectstatic" is called, 
usually in production environment. Must be the same as in *docker-compose.prod.yaml*, *Dockerfile.prod* 
and *nginx.conf*.    
**STATICFILES_DIRS**: list of additional static file locations apart from the default *static/* folder in app 
directory.    

For detailed explanation, please visit 
[official documentation (on static files)](https://docs.djangoproject.com/en/5.0/howto/static-files/).

#### Nginx:
**client_max_body_size**: the maximum size of the client request body allowed. If exceeds, server responds with "413 
Request Entity Too Large". Mostly useful for restricting file upload size. Can also be done by filtering requests at
application level through Django's middlewares (or even more fine-grained, at each view function).

## Todo List

- [ ] **As of 03/07:**
  - [ ] (p1) Global error handler and logger
  - [ ] (p2) User space page
  - [ ] (p2) link to paper and user space in search results

- [ ] **As of 26/06:**
  - [x] (p0) My tags list page
  - [x] (p1) Add navigation bar
  - [x] (p0) Finish containerization
  - [ ] (p1) Refactor enum fields
  - [ ] (p2) Tutorial video

- [ ] **Features (optional):**
  - [ ] Google OAuth2
  - [ ] Use display name apart from username
  - [ ] User upload avatars and config media files

- [ ] **Readme Content:**
  - [ ] photo of system designs
  - [ ] link to WSGI
  - [ ] usage, install guide, important file locations...
  - [ ] How to install Git
