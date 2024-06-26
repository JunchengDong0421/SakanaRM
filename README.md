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

- [ ] **Essential:**
  - [x] Data storage for references/papers
  - [x] Manage references (add, replace, delete, download)
  - [x] Manage customizable tags (add, update, delete)
  - [x] Match tags on references 
  - [x] Query for references based on filters
  - [ ] (99% done, ETA: 2 min) Integration with LLM
  - [x] Flexible programming interfaces to switch between LLMs
  - [x] Track progress of reference uploads and LLM
  - [x] Productionization
  - [ ] (40% done, ETA: 2 days) User documentation
  - [ ] (20% done, ETA: 4 days) Developer documentation
  - [ ] (80% done, ETA: 2 days) Usable (not so ugly) UI


- [ ] **Optional:**
  - [ ] Integration with Google OAuth 2

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
### Steps
1. Clone repository:   
`git clone git@github.com:JunchengDong0421/SakanaRM.git`
2. Set working directory to project root:    
`cd SakanaRM/`    

If used with [SakanaCDN](https://github.com/JunchengDong0421/SakanaCDN), open another terminal tab and:
3. Clone SakanaCDN repository:    
`git clone git@github.com:JunchengDong0421/SakanaCDN.git`
4. Set working directory to project root:    
`cd SakanaCDN/`

## Configuration
You need to at least configure the CDN client correctly for the server to work as expected. If you do not want the 
default simple 
word tagging, you also need to configure the 
### LLM Client

### CDN Client

## Usage
### Production Environment
1. Make sure docker daemon process is running:    
`sudo dockerd`
2. 

### Development Environment

### Pure Personal Use (not recommended)

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
**Note:** Whenever you make any changes to your data models (in any *models.py*) or add new applications to 
**INSTALLED_APPS** (in *SakanaRM/SakanaRM/settings.py*), you should **manually** run the following code in the app 
root (*SakanaRM/* directory):    
`python manage.py makemigrations`    
and don't forget to **add the generated files** to your version control so that migrations can be applied in 
docker entrypoint.

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

### Docker-related Files
#### healthcheck.sh
MariaDB health check uses official example in [this link](https://mariadb.com/kb/en/using-healthcheck-sh/). 
If the code or script for some reasons does not work anymore, please check for updates on official websites.

## Todo List

- [ ] **As of 03/07:**
  - [ ] (p1) Beautify pages with quick solutions, use better dataset for demonstration
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
