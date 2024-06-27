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
**Essential:**

| Feature                         | Sub-Feature                                              | Status      | ETA   |
|---------------------------------|----------------------------------------------------------|-------------|-------|
| Store references                | PDF only                                                 | DONE        |       |
| Manage references               | Add, replace, delete, download                           | DONE        |       |
| Manage customizable tags        | Add, update, delete                                      | DONE        |       |
| Match tags                      | On references                                            | DONE        |       |
| Query for references            | Based on filters                                         | DONE        |       |
| Integration with LLM            |                                                          |             |       |
|                                 | Stand-alone client                                       | DONE        |       |
|                                 | Integration into views                                   | DONE        |       |
| Flexible programming interfaces |                                                          |             |       |
|                                 | Switch between LLMs                                      | DONE        |       |
|                                 | Switch between CDNs                                      | DONE        |       |
| Track progress                  |                                                          |             |       |
|                                 | Track reference uploads                                  | DONE        |       |
|                                 | Track LLM processing                                     | DONE        |       |
| Productionization               |                                                          |             |       |
|                                 | Docker-related files                                     | DONE        |       |
|                                 | Deployment with Gunicorn, MariaDB, Nginx                 | DONE        |       |
| User documentation              |                                                          |             |       |
|                                 | Installation                                             | DONE        |       |
|                                 | Configuration                                            | DONE        |       |
|                                 | Usage                                                    | IN PROGRESS | 30/06 |
|                                 | Important notices                                        | IN PROGRESS | 02/07 |
|                                 | Tutorial video                                           | BACKLOG     | 09/07 |
| Developer documentation         |                                                          |             |       |
|                                 | Preface (project structure, some basics)                 | DONE        |       |
|                                 | Advanced deployment (settings, custom clients, database) | IN PROGRESS | 01/07 |
|                                 | Miscellaneous                                            | IN PROGRESS | 02/07 |
|                                 | Simple API reference                                     | BACKLOG     | 09/07 |
| Usable UI                       |                                                          |             |       |
|                                 | Basic layout                                             | DONE        |       |
|                                 | Beautified page (apply quick solutions)                  | IN PROGRESS | 02/07 |

**Optional:**                 

| Feature                         | Sub-Feature                            | Status            | ETA         |
|---------------------------------|----------------------------------------|-------------------|-------------|
| Integration with Google OAuth   |                                        | BACKLOG           |             |


## Installation
### Prerequisite
- Python 3.9
- Docker (Engine version 27.0.1) 

**How to install Docker**: please follow the [official guide](https://docs.docker.com/engine/install/). 
You can either install Docker Engine or Docker Desktop. Verify critical components are correctly installed by
running commands such as `sudo docker compose version` etc.

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
2. Set working directory to project root (where *README.md* is located):    
`cd SakanaRM/`    

If used with [SakanaCDN](https://github.com/JunchengDong0421/SakanaCDN), go to another machine where you want uploaded 
papers to be stored or open another terminal tab (store on same machine) and:
3. Clone SakanaCDN repository:    
`git clone git@github.com:JunchengDong0421/SakanaCDN.git`
4. Set working directory to project root (where *README.md* is located):    
`cd SakanaCDN/`

## Configuration
For the server to work as expected, you need to at least configure the CDN client correctly. You can also [custom your 
own clients](#how-to-custom-llm-and-cdn-clients).

### CDN Client
Within the scope of the project, you don't have to register a real CDN service to use the server, what is needed is just
a simple server that implements APIs to store, replace, get, delete papers. The bundled ***SakanaCDNClient*** is used 
to communicate with the service offered by [SakanaCDN](https://github.com/JunchengDong0421/SakanaCDN).


**The default CDN client is ***SakanaCDNClient*****. To configure ***SakanaCDNClient***, 
go to *SakanaRM/core/cdn_utils/sakana_cdn_client.py*, and look for the class attribute ***"BASE_URL"***. Change the 
host IP and port to the actual IP and port which your SakanaCDN service binds to, for example, if you are running 
SakanaCDN on a machine with IP 201.153.35.66 and port 5001, change the value to "http://201.153.35.66:5001/files".    
**IMPORTANT**: DO NOT use a loopback address (`localhost`, `127.0.0.1`) if SakanaRM runs in container because routing 
is managed by Docker network. See [Networking in Compose](https://docs.docker.com/compose/networking/) for details.

### LLM Client
The project bundles two classes of client to use for paper processing: ***GPTClient*** and ***SimpleKeywordClient***.
The former integrates GPT (provider You.com) by [gpt4free](https://github.com/xtekky/gpt4free), and the latter simply
match tag names with words in the paper.    

**The default CDN client is ***GPTClient*****. You don't need to specifically configure anything. However, to use 
***SimpleKeywordClient***, go to *SakanaRM/core/views.py*, add a line of import if not existent: `from .llm_utils import 
SimpleKeywordClient`, then find and replace all `GPTClient()` to `SimpleKeywordClient()` in code.

### Database
By default, the production server uses MariaDB that runs as a separate service, the development server creates and runs
a SQLite3 instance in one service. If you want to use other databases, see 
[switch to other databases](#switch-to-other-databases).


## Usage
### Production Environment
1. Make sure docker daemon process is running:    
`sudo dockerd`
2. Check that port `80` and `5000` on target machine are not occupied: please Google for solutions.
3. Start your CDN services first, if SakanaCDN (current directory is *SakanaCDN/*):    
`sudo docker compose up --build`
4. Start SakanaRM services (current directory is *SakanaRM/*):    
`sudo docker compose -f docker-compose.prod.yaml up --build`
5. Visit http://\<your_server_ip\>. Done!    


To shut down services:    
`sudo docker compose -f docker-compose.prod.yaml down`    
To restart services:    
`sudo docker compose -f docker-compose.prod.yaml restart`  

### Development Environment
**Note**: After all containers are down, you might see some auto-generated files (log files, db file) in the source code 
directory. You can use them for debugging purposes. DO NOT DELETE these files as they persist data within the 
containers, but instead add them to your version control's ignored files (e.g., *.gitignore*).

1. Make sure docker daemon process is running:    
`sudo dockerd`
2. Check that port `80` and `5000` on target machine are not occupied: please Google for solutions.
3. Start your CDN services first, if SakanaCDN (current directory is *SakanaCDN/*):    
`sudo docker compose up --build`
4. Start SakanaRM services (current directory is *SakanaRM/*):    
`sudo docker compose up --build`
5. Visit http://\<your_server_ip\>. Done!    

To shut down services:    
`sudo docker compose down`    
To restart services:    
`sudo docker compose restart`  

### Pure Personal Use
If you don't want to install or mess around with `docker`, plus you are using the server for yourself/with a few 
trusted people only (meaning less load, fewer papers), then it makes sense to only run the services as Python 
executables with Django and Flask's built-in development servers. Since the server doesn't run in a container 
environment anymore, you can configure ***SakanaCDNClient*** to use "http://localhost:5000/files" as ***"BASE_URL"*** 
if you run SakanaCDN on the same machine. Still, you need to **weight the risks**.

1. Remove all `gunicorn`, `mysqlclient`, `greenlet` and `gevent` dependencies from *SakanaRM/requirements.txt* and
*SakanaCDN/requirements.txt*.
2. Install dependencies:    
```
# For SakanaRM
cd SakanaRM/
pip install -r requirements.txt

# For SakanaCDN
cd SakanaCDN/
pip install -r requirements.txt
```
3. Check that port `80` and `5000` on target machine are not occupied: please Google for solutions.
4. Start SakanaCDN server (now you should be in the same directory as *"app.py"*):    
`python -m flask run --host=0.0.0.0 --port=5000`
5. Start SakanaRM server (now you should be in the same directory as *"manage.py"*):    
```
python manage.py migrate
python manage.py runserver 0.0.0.0:80 --settings=SakanaRM.settings_dev
```
5. Visit http://localhost. Done!    

## User Guide
To learn about how to use the website, please watch the [tutorial video]().

### Some Important Notices
- Paper titles are NOT unique if uploader is different, but for the same uploader, papers should have unique, non-empty 
titles;
- Tag names are unique. Semicolons, trailing and leading spaces in tag names are not allowed and would be removed by 
system;
- A new paper that is being uploaded does not appear in "My Papers" nor has a detail page until the upload successfully 
completes;

## Developer's Guide
**Note:** Whenever you make any changes to your data models (in any *models.py*) or add new applications to 
**INSTALLED_APPS** (in *SakanaRM/SakanaRM/settings.py*), you should **manually** run the following code in the app 
root (*SakanaRM/* directory):    
`python manage.py makemigrations`    
and don't forget to **add the generated files** to your version control so that migrations can be applied in 
docker entrypoint.

### Preface
SakanaRM is developed under the [Django](https://www.djangoproject.com/) framework, and mostly follows standard 
practices and conventions. To learn more about basics like project structure, please refer to the [official 
documentation](https://docs.djangoproject.com/en/4.2/) or follow this 
[tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Tutorial_local_library_website).

SakanaRM started from the 
[default project template](https://docs.djangoproject.com/en/5.0/ref/django-admin/#django-admin-startproject) and 
contains two custom apps:
- accounts: functionalities around user authentication and custom model SakanaUser
- core: core functionalities, including integration with LLM    

All templates are located in the *SakanaRM/templates/* folder, and all [extend](https://docs.djangoproject.com/en/4.2/ref/templates/builtins/#std-templatetag-extends) 
the parent template *"base.html"*.   

All static files are located in the *SakanaRM/static/* folder, and [served](https://docs.djangoproject.com/en/4.2/howto/static-files/deployment/) 
from a dedicated web server (e.g., Nginx).    

`manage.py` is the [entry point](https://docs.djangoproject.com/en/4.2/ref/django-admin/) to all django commands 
(equivalent of running `django-admin`, note there is no `django` command!)    

The project package `SakanaRM` contains setting files (*"settings.py"*, *"settings_dev.py"*) and the WSGI application 
for [deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/) (*"wsgi.py"*)

### System Design
![system design](https://drive.google.com/uc?id=1VWT8YWdz5fvwbkFM_9EtmjhECFfCOhLu)

### MVT Pattern, WSGI Explained
MVT pattern explained: [link](https://medium.com/@codewithbushra/understanding-the-mvt-design-pattern-in-django-code-with-bushra-e4adc3f7d7d3)    
WSGI explained: [link](https://www.fullstackpython.com/wsgi-servers.html)

### Important Settings
#### Django:
(in *SakanaRM/SakanaRM/settings.py*)    
***STATIC_URL***: part of URL path to request for static files, e.g., "http://localhost:8000/static/a.js" is used to 
request for "a.js" when set to "/static/". Must be the same as in *nginx.conf*.    
***STATIC_ROOT***: directory where static files are collected when command "python manage.py collectstatic" is called, 
usually in production environment. Must be the same as in *docker-compose.prod.yaml*, *Dockerfile.prod* 
and *nginx.conf*.    
***STATICFILES_DIRS***: list of additional static file locations apart from the default *static/* folder in app 
directory.    

For detailed explanation, please visit 
[official documentation (on static files)](https://docs.djangoproject.com/en/5.0/howto/static-files/).

#### Gunicorn:
(in *SakanaRM/gunicorn.conf.py*)    
**worker_class**: there are many [types of worker processes](https://docs.gunicorn.org/en/stable/design.html#design) to
specify. Since the server makes many outgoing requests to external APIs, it is more beneficial to use a type of 
asynchronous worker.

#### Nginx:
(in *nginx/nginx.conf*)    
**client_max_body_size**: the maximum size of the client request body allowed. If exceeds, server responds with "413 
Request Entity Too Large". Mostly useful for restricting file upload size. Can also be done by filtering requests at
application level through Django's middlewares (or even more fine-grained, at each view function).    
**proxy_set_header Host**: use `$http_host` instead of `$host`, if your web server does not run on port `80` or `443` 
and you want to parse client host header in application server. `$http_host` will include the port number if it was 
part of the client's request.

### SSL/HTTPS
The server is NOT configured to establish secure links. To set up HTTPS, Google for solutions then follow 
[Django official documentation](https://docs.djangoproject.com/en/5.0/topics/security/#ssl-https).

### How to Custom LLM and CDN Clients

### Use Docker Compose Commands:
**Note**: always add `-f docker-compose.prod.yaml` if working with production services.

`sudo docker compose logs`: Displays logs for all services defined in the *docker-compose.yaml* file.    
`sudo docker compose ps`: Lists the status of all services defined in the *docker-compose.yaml* file.    
`sudo docker compose exec <service_name> <command>`: Runs a command in a running service container.    
`sudo docker volume ls`: Lists all Docker volumes.    
`sudo docker volume inspect <volume_name>`: Display detailed information on a volume    

### Docker-related Files
#### healthcheck.sh
MariaDB health check uses official example in [this link](https://mariadb.com/kb/en/using-healthcheck-sh/). 
If the code or script for some reasons does not work anymore, please check for updates on official websites.

### Switch to Other Databases

### Abandon the CDN Approach
As mentioned above that the server does not require a real CDN service to fully function. Considering the personas 
of users, it is probably better to store papers on the same machine as the server and manage them as media files by 
Django, rather than creating another service to store and get the files. If you are interested in refactoring the code, 
feel free to do so.

### Workflow Model & Potential Improvements
**Part I**: The *Workflow* model is designed to preserve the status of upload and process tasks. Use another model or 
programming logic to improve.

**Part II**: Use [Celery](https://docs.celeryq.dev/en/stable/) instead of multithreading to perform tasks to improve.


## Simple API Reference
### Accounts:
| Path   | Method | Parameters | Return Type  | View               | Name       | Description     |
|--------|--------|------------|--------------|--------------------|------------|-----------------|
| login/ | GET    |            | HttpResponse | display_login_page | login-page | User login page |

### Core:

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

## Author
Juncheng Dong: [jd4115@nyu.edu](mailto:jd4115@nyu.edu), [ge85dih@mytum.de](mailto:ge85dih@mytum.de)