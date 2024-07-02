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
|                                 | Usage                                                    | DONE        |       |
|                                 | Important notices                                        | DONE        |       |
|                                 | Tutorial video                                           | BACKLOG     | 09/07 |
| Developer documentation         |                                                          |             |       |
|                                 | Preface (project structure, some basics)                 | DONE        |       |
|                                 | Advanced deployment (settings, custom clients, database) | DONE        |       |
|                                 | Miscellaneous                                            | DONE        |       |
|                                 | Simple API reference                                     | BACKLOG     | 09/07 |
| Usable UI                       |                                                          |             |       |
|                                 | Basic layout                                             | DONE        |       |
|                                 | Beautified page (apply quick solutions)                  | IN PROGRESS | 05/07 |

**Optional:**                 

| Feature                         | Sub-Feature                            | Status            | ETA         |
|---------------------------------|----------------------------------------|-------------------|-------------|
| Integration with Google OAuth   |                                        | BACKLOG           |             |


## Installation
### Prerequisite
- Python 3.9
- Docker (Engine version 27.0.1, Compose version 2.27.1)     

**System requirements**: Windows not supported. Tested on Ubuntu 22.04. Hardware requirements not investigated and vary 
on usage scenarios.

**How to install Docker**: please follow the [official guide](https://docs.docker.com/engine/install/). 
You can either install Docker Engine or Docker Desktop.    

**Verify versions**:
```
python -V
sudo docker -v
sudo docker compose version
```

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
The system interacts with two external services to work: a "CDN" service, which handles papers upload, replacement, 
deletion, download; and a LLM service, which offers basic chat completion capabilities. Clients for communicating with 
these services are required. You would need to at least configure the provided CDN client correctly for the system to 
work as expected. It is also possible to [custom your own clients](#how-to-custom-llm-and-cdn-clients).

### CDN Client
Within the scope of the project, you don't have to register a real CDN service to use the system, what is needed is just
a simple service that implements APIs to store, replace, get, delete papers. The bundled ***SakanaCDNClient*** is used 
to communicate with the service offered by [SakanaCDN](https://github.com/JunchengDong0421/SakanaCDN).


**The default CDN client** is *****SakanaCDNClient*****. Go to *SakanaRM/core/cdn_utils/sakana_cdn_client.py*, and 
look for the class attribute ***"BASE_URL"***. Change the host IP and port to the actual IP and port which your 
SakanaCDN service binds to, for example, if you are running SakanaCDN on a machine with IP 201.153.35.66 and port 5001, 
change the value to "http://201.153.35.66:5001/files".    
**IMPORTANT**: DO NOT use a loopback address (`localhost`, `127.0.0.1`) if SakanaRM runs in container because routing 
is managed by Docker network. See [Networking in Compose](https://docs.docker.com/compose/networking/) for details.

### LLM Client
The project bundles two classes of client to use for paper processing: ***GPTClient*** and ***SimpleKeywordClient***.
The former integrates with GPT client by [gpt4free](https://github.com/xtekky/gpt4free), while the latter simply 
matches tag names with words in the paper and makes no external calls.    

**The default CDN client** is *****GPTClient*****. Go to *SakanaRM/core/llm_utils/gpt_client.py*, and look for the 
class attribute ***"PAPER_SLICE_LENGTH"***, ***"MODEL"*** and ***"TEMPERATURE"***. Modify how long paper is sliced into 
parts for transmission, the model used and the temperature of the model by setting corresponding values, or just accept 
the default value and skip this step. To use the alternative ***SimpleKeywordClient***, go to *SakanaRM/core/views.py*, 
add a line of import if non-existent: `from .llm_utils import SimpleKeywordClient`, then find and replace all 
`GPTClient()` to `SimpleKeywordClient()` in code.

### Database
By default, the production server uses MariaDB that runs as a separate service, the development server creates and runs
a SQLite3 instance in one service. If you want to use other databases, see 
[switch to other databases](#switch-to-other-databases).


## Usage
### Production Environment
1. Make sure docker daemon process is running:    
`sudo dockerd`
2. Check that port `80` and `5000` on target machine are not occupied: please Google for solutions.
3. Go to *SakanaRM/SakanaRM/settings.py*, change the ***SECRET_KEY*** variable to a different random string.
4. Start your CDN services first, if SakanaCDN (current directory is *SakanaCDN/*):    
`sudo docker compose up --build`
5. Start SakanaRM services (current directory is *SakanaRM/*):    
`sudo docker compose -f docker-compose.prod.yaml up --build`
6. Visit *http://\<your_server_ip\>*. Done!    


To shut down services:    
`sudo docker compose -f docker-compose.prod.yaml down`    
To restart services:    
`sudo docker compose -f docker-compose.prod.yaml restart`  

### Development Environment
**Note**: After all containers are down, you might see some auto-generated files (log files, db file) in the source code 
directory. You can use them for debugging purposes. DO NOT DELETE these files as they persist data within the 
containers, but instead add them to your version control's ignored files (e.g., *.gitignore*). Also, only the web 
service with a default SQLite database is configured. If you think a separate database service is absolutely needed, 
feel free to add it and change the settings of the Django application.

1. Make sure docker daemon process is running:    
`sudo dockerd`
2. Check that port `8000` and `5000` on target machine are not occupied: please Google for solutions.
3. Start your CDN services first, if SakanaCDN (current directory is *SakanaCDN/*):    
`sudo docker compose up --build`
4. Start SakanaRM services (current directory is *SakanaRM/*):    
`sudo docker compose up --build`
5. Visit *http://\<your_server_ip\>:8000*. Done!    

To shut down services:    
`sudo docker compose down`    
To restart services:    
`sudo docker compose restart`  

### Pure Personal Use (not recommended)
If you don't want to install or mess around with `docker`, plus you are using the server for yourself/with a few 
trusted people only (meaning less load, fewer papers), then it makes sense to only run the services as Python 
executables with Django and Flask's built-in development servers. Since the application doesn't run in a container 
environment anymore, you can configure ***SakanaCDNClient*** to use "http://localhost:5000/files" as ***"BASE_URL"*** 
if you run SakanaCDN on the same machine. Still, you must **weigh the risks** because the development servers are 
**not particularly secure, stable, or efficient** in their design.

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
5. Visit *http://localhost*. Done!    

## User Guide
To learn about how to use the website, please watch the [tutorial video]() made by the author.

### Admin Sites and Superuser
Django offers a powerful admin interface for superusers/staffs to easily manage the models in the system. Always append
`--settings=SakanaRM.settings_dev` to each command if you are using the development settings.
- To create a superuser, add the environment variables `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_USERNAME`, 
`DJANGO_SUPERUSER_EMAIL` to the *"web"* service in *docker-compose.prod.yaml* and *docker-compose.yaml*. Then, run 
`sudo docker compose exec web python manage.py createsuperuser --noinput ` when services are up. For [Pure Personal 
Use](#pure-personal-use-not-recommended), simply run `python manage.py createsuperuser --settings=SakanaRM.settings_dev` 
after database is set up and follow the prompts. 
- To visit the admin sites, go to *http://<your_server_ip>/admin* and log in as a superuser. 
- To [customize admin sites](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/), add your code to *"admin.py"* 
inside every app's directory (*SakanaRM/accounts/*, *SakanaRM/core/*).

### Some Important Notices
- Paper titles are NOT unique if uploader is different, but for the same uploader, papers should have unique, non-empty 
titles;
- Tag names are unique. Semicolons, trailing and leading spaces in tag names are not allowed and would be removed by 
the system;
- You can only abort a workflow when it is pending, whereas the condition for archiving it is the total opposite;
- You cannot delete a workflow. If you don't want the workflow to appear on your home page, archive it;
- Deleting paper will also result in deletion of all corresponding workflows;
- Manual tagging is available on a paper's detail page;
- A new paper that is being uploaded does not appear in "My Papers" nor has a detail page until the upload workflow 
successfully completes;
- Among match types, "exact" means tags selected match exactly those of a paper, "inclusion" means tags selected match 
a subset of those of a paper, and "union" means tags selected match one of those of a paper;
- The display name is the identity of a user shown to others, and it is unique with a maximum length of 150 characters;
- Length limits (unit: characters): username: 150, password: 128, email: 254, first name: 150, last name: 150;

## Developer's Guide
**Note:** Whenever you make any changes to your data models (in any *models.py*) or add new applications to **INSTALLED
_APPS** (in *SakanaRM/SakanaRM/settings_dev.py*), you should **manually** run the following code in the app root 
(*SakanaRM/* directory):    
`python manage.py makemigrations --settings=SakanaRM.settings_dev`    
and don't forget to **add the generated files** to your version control so that migrations can be applied in 
docker entrypoint. You can try to 
[squash migrations](https://docs.djangoproject.com/en/4.2/topics/migrations/#migration-squashing) if there are too 
many of them.

### Preface
SakanaRM is developed under the [Django](https://www.djangoproject.com/) framework, and mostly follows standard 
practices and conventions. To learn more about basics like project structure, please refer to the [official 
documentation](https://docs.djangoproject.com/en/4.2/) or follow the [MDN
tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Tutorial_local_library_website).

SakanaRM started from the 
[default project template](https://docs.djangoproject.com/en/4.2/ref/django-admin/#django-admin-startproject) and 
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
[official documentation (on static files)](https://docs.djangoproject.com/en/4.2/howto/static-files/).

#### Gunicorn:
(in *SakanaRM/gunicorn.conf.py*)    
***worker_class***: there are many [types of worker processes](https://docs.gunicorn.org/en/stable/design.html#design) to
specify. Since the server makes many outgoing requests to external APIs, it is more beneficial to use a type of 
asynchronous worker.    
***loglevel***: set the level of error log, which contains events related to the application and internal processes. 
Does not have anything to do with access log where all HTTP requests processed by the server are logged down.

#### Nginx:
(in *nginx/nginx.conf*)    
***client_max_body_size***: the maximum size of the client request body allowed. If exceeds, server responds with "413 
Request Entity Too Large". Mostly useful for restricting file upload size. Can also be done by filtering requests at
application level through Django's middlewares (or even more fine-grained, at each view function).    
***proxy_set_header Host***: use `$http_host` instead of `$host`, if your web server does not run on port `80` or `443` 
and you want to parse client host header in application server. `$http_host` will include the port number if it was 
part of the client's request.    
***allow & deny***: allow requests only from certain IP addresses. You can place the directives under the "server" block 
to restrict access across the site, or only apply restrictions on certain locations under the "location" blocks. 
Wildcard matching not supported by you can use CIDR donation to allow or deny a range of IP addresses.

### Testing
With Django's testing framework, it is relatively straightforward to write unit tests and integration tests 
(interactions between modules). Always append `--settings=SakanaRM.settings_dev` to each command if you are using the 
development settings.
- To [write tests](https://docs.djangoproject.com/en/4.2/topics/testing/), add test cases to *"tests.py"* inside every 
app's directory (*SakanaRM/accounts/*, *SakanaRM/core/*).
- To run tests, run `sudo docker compose exec web python manage.py test --noinput ` when services are up. For [Pure 
Personal Use](#pure-personal-use-not-recommended), simply run `python manage.py test --settings=SakanaRM.settings_dev` 
after database is set up and follow the prompts. 
- It is recommended to configure a new environment for testing, which is something the project can improve on. See 
[Potential Improvements](#workflow-model--potential-improvements) Part III.

### CI/CD
The CI/CD platform used for this project is GitHub Actions, and pipelines are only created for the main branch 
(*"origin/master"*). To make full use of GitHub Actions, configure testing correctly and add more tests. Do not forget 
to fork the repository first. Every time after a push is made, check that all Actions workflows pass. If you want to 
modify or add any workflows, go to the folder *.github/workflows* and check out the *.yml* files there.

### SSL/HTTPS
The server is NOT configured to establish secure links. To set up HTTPS, Google for solutions then follow 
[Django's official documentation](https://docs.djangoproject.com/en/4.2/topics/security/#ssl-https).

### How to Custom LLM and CDN Clients
To custom your own clients, follow the below steps (remember always to use relative imports):
1. Go to the corresponding utils folder (*SakanaRM/core/xxx_utils/*).
2. Create a *.py* file with the name of your client.
3. Edit the file, first add a line that imports the corresponding abstract class: `from .abstract_xxx_client 
import AbstractXXXClient`.
4. Then, create your own client class, the class must inherit from the abstract class and implement all abstract 
methods of the base class. Make sure you understand the meaning of function parameters and do not override their types! 
For example, `paper` is a readable I/O object, and `tags` is a dictionary of tag items with keys being tag names and 
values being tag definitions etc. 
5. Go to the corresponding *\__init__.py* file (*SakanaRM/core/xxx_utils/\__init__.py*).
6. Edit the file, add a line of import: `from .your_client_name.py import YourClient`.
7. Go to *SakanaRM/core/views.py*.
8. Add a line of import: `from .xxx_utils import YourClient`, find and replace all `OriginalClient()` (original client 
instances) to `YourClient()` in the code.
9. Test if your clients are working fine.    

**Note**: CDN clients need to generate a random filename and request to store the paper as that particular filename. You
can use the function *"random_filename"* in *SakanaRM/core/cdn_utils/utils.py* to make up the filename. For sending
requests, you are recommended to use the library [Requests](https://requests.readthedocs.io/en/latest/) or the advanced 
version [Requests-HTML](https://requests.readthedocs.io/projects/requests-html/en/latest/).

### Configure Logging
Only logs of Django and Gunicorn are manually configured and persisted in this project. For Nginx, access the logs 
located at */var/log/nginx* inside the container when it is running. Log rotations are not implemented at all. 
To make it work, please Google for solutions. Feel free to change log levels or log more information to suit your 
needs! To log messages in a file, first import the logging module: `import logging`, then get logger in this file: `
logger = logging.getLogger(__name__)`, finally log messages in different levels: `logger.<level>(<msg>)`.

**Development**: logs are located in app root (*SakanaRM/*)    
- `django_access.log`, `django_debug.log`, `django_error.log`: Django logs (of all info-level events; all debug-level 
events; unhandled exceptions during handling of a request)
- `access.log`, `error.log`: Gunicorn logs (of all HTTP requests processed; all debug-level events)

**Production**: logs are located inside *"logs"* folder under app root (*SakanaRM/logs*)
- `accounts_info.log`, `core_info.log`, `django_error.log` Django logs (of all info-level events in app *accounts*; 
all info-level events in app *core*; unhandled exceptions during handling of a request)
- `access.log`, `error.log`: Gunicorn logs (of all HTTP requests processed; all debug-level events)

### Useful Docker Compose Commands:
**Note**: always add `-f docker-compose.prod.yaml` if working with production services.

`sudo docker compose logs`: displays logs for all services defined in the *docker-compose.yaml* file.    
`sudo docker compose ps`: lists the status of all services defined in the *docker-compose.yaml* file.    
`sudo docker compose exec <service_name> <command>`: runs a command in a running service container.    
`sudo docker volume ls`: lists all Docker volumes.    
`sudo docker volume inspect <volume_name>`: display detailed information on a volume.    
`sudo docker system df`: show Docker disk usage.    

### Docker-related Files
`docker-compose.prod.yaml`, `docker-compose.yaml`: files that describe the services    
`Dockerfile.prod`, `Dockerfile`: files that specify how images are built, see [Multi-stage 
Build](https://docs.docker.com/build/guide/multi-stage/)    
`entrypoint.prod.sh`, `entrypoint.sh`: scripts to execute inside a container whenever it starts up    
`healthcheck.sh`: the database service uses MariaDB's [official script](https://mariadb.com/kb/en/using-healthcheck-sh/) 
for health check. If the code or script for some reasons does not work anymore, please check for updates on official 
websites.

### Switch to Other Databases
The databases chosen for the project are MariaDB (production) and SQLite3 (development). To configure to use another 
database, follow the steps below:
1. In `docker-compose.prod.yaml`, change image used by `db` service and environment variables to set up the database
correctly.
2. In `settings.py`, change the values in the `DATABASES` variable, make sure they match the values of the environment 
variables in step 1.
3. In `requirements.txt`, add driver dependencies if any is needed, for example, MariaDB needs the *"mysqlclient"* 
library to connect to.

### Firewall & Security
It is recommended to configure a firewall to enforce access control policies on network traffics. You can do that 
with the web server. See [Important Settings - Nginx](#nginx). Just in case, you should always set up an OS level 
firewall on the host machine. For example, [Ubuntu UFW](https://ubuntu.com/server/docs/firewalls), 
[Windows Firewall](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/tools)
etc.    

Django features several security middlewares and mechanisms to protect against common attacks on web applications. See 
[Security in Django](https://docs.djangoproject.com/en/4.2/topics/security/) for details. That's, for example, why you 
should include the field `csrfmiddlewaretoken` with the value `{{ csrf_token }}` (in templates) whenever you post data 
to the server. It's also important to set a different secret key for use in production and keep it secret (i.e., do not 
push it to your public repository). But for database service environment variables, it is fine to leave them as is 
because the service is not exposed to the outside of the container.

### About LLM Providers
To access LLM APIs, the project uses the [gpt4free](https://github.com/xtekky/gpt4free) package. As a developer, you 
should always use the latest version of the package in the development environment to test if it is still usable 
anymore, and make sure all dependencies are noted down in *requirements.txt*. If you do not specify a provider in the 
client, then it will automatically select available ones to use. 

### Windows Support
Since Gunicorn does not support Windows, you should use another WSGI server to run the WSGI application 
(SakanaRM: Django, SakanaCDN: Flask) if you want to [deploy](https://flask.palletsprojects.com/en/2.3.x/deploying/) 
the system on a Windows system. However, if you take the [Pure Personal Use](#pure-personal-use-not-recommended) 
approach, then you don't have to consider this layer of deployment. But, note that Python is not 100% portable between 
platforms. That's why in *SakanaRM/core/views.py*, a line in function *search_result* checks for os names because 
Windows and Linux use different flags to remove zero padding in formatting datetime strings (see 
[link](https://stackoverflow.com/questions/9525944/python-datetime-formatting-without-zero-padding/42709606#42709606)).

### Abandon the CDN Approach
As mentioned above that the server does not require a real CDN service to fully function. Considering the personas 
of users, it is probably better to store papers on the same machine as the server and manage them as media files by 
Django, rather than creating another service to store and get the files. If you are interested in refactoring the code, 
feel free to do so and even send a pull request.

### Workflow Model & Potential Improvements
**Part I**: The *Workflow* model is designed to preserve the status of upload and perform tasks. It is mapped to a 
software thread according to its design (see Part II). However, the execution flow of *Workflow* an instance is somewhat 
client-controlled (specifically, abortion), which is not the case for threads executing the tasks (because neither 
information about them is stored nor their statuses checked), and this makes writing code harder since you have to 
check the current state of the workflow frequently during a task execution.
*To improve*: find a way to manage the threads' execution effectively; or design another model and/or use a different 
programming logic.

**Part II**: The fields `instructions` (brief information about the task, used in workflow detail page), `messages` (
not really used) and `` of Workflow instances are obvious at all. The initial design blueprint is that, user can not
only create standard upload and process workflows as is the case right now, but also can submit a description file to 
customize their own workflows, something like CI/CD pipelines. However, this idea was not implemented in the end.    
*To improve*: design another model or make the idea really work.

**Part III**: Since *Workflow*'s tasks are mostly I/O-bound (network calls, db transactions, file I/O), 
they are programmed, for simplicity, to be executed in threads using Python's 
[threading](https://docs.python.org/3/library/threading.html) module. However, this is not the most efficient way 
because the execution of the calling thread is still blocked.    
*To improve*: use [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor) or 
[event driven programming](https://docs.python.org/3/library/asyncio.html#module-asyncio), or even better, 
[Celery](https://docs.celeryq.dev/en/stable/) to perform concurrent tasks instead of multithreading.

**Part IV**: The Django application server uses two setting files for different environments which makes some commands 
slightly more complicated and log files location different. Also, a new environment (for example, testing) might require 
a new setting file to be added which just complicates matters.    
*To improve*: take the approach of
[smartly utilizing environment variables](https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/#docker).

**Part V**: The result of many requests are determined by the `status` field in the Json response rather than the HTTP
status code. As a consequence, responses of failed requests would also carry the HTTP 200 code and be considered 
"success" by JQuery Ajax, so that part of JavaScript code in this project is written in a dedicated manner.    
*To improve*: add status code to every view function return, refactor JQuery Ajax code to handle failed requests in 
"error" and remove corresponding part from "success".

**Part VI**: Some HTML tables are included in the web pages. It makes sense to make all of them sortable to provide a 
better user experience.    
*To improve*: [make HTML tables sortable](https://webdesign.tutsplus.com/how-to-create-a-sortable-html-table-with-javascript--cms-92993t) 
in project templates.

**Part VII**: The frontend was developed in a haste. The only library used is [JQuery](https://jquery.com/) for DOM 
manipulation. Not very beautiful, not responsive at all.    
*To improve*: use a frontend framework like [React](https://react.dev/) or a CSS framework like 
[Tailwind CSS](https://tailwindcss.com/).

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