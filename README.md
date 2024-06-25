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

## Usage
### Prerequisite
If you really want to use a Python interpreter version below 3.9, please find out the following patterns in source code 
and refactor them:
    
Added in Python 3.9:
- New module `from zoneinfo import ZoneInfo` is used instead of `from pytz import timezone` as *tzinfo* object class
- Dictionary merge operator `|` to merge two dictionaries

Added in Python 3.8:
- Assignment operator `:=` to capture sub-expressions inline
  
## Todo List

- [ ] **As of 26/06:**

  - [x] (p0) My tags list page
  - [x] (p1) Add navigation bar
  - [ ] (p1) Refactor enum fields
  - [ ] (p1) Global error handler and logger
  - [ ] (p2) Tutorial video

- [ ] **Features (optional):**
  - [ ] Google OAuth2
  - [ ] Use display name apart from username

- [ ] **Readme Content:**
  - [ ] photo of system designs
  - [ ] link to WSGI
  - [ ] usage, install guide, important file locations...
  - [ ] How to install Git
