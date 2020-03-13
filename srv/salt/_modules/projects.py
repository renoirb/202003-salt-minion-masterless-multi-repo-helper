#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
:maintainer: Renoir Boulanger <contribs@renoirboulanger.com>
:maturity: False
:requires: requests
:platform: all

Maintenance tasks for keeping a group of projects in sync with remote GitLab.

For each projects configured for this workspace.

@author Renoir Boulanger

See also:
 - http://stackoverflow.com/questions/29920575/salt-python-api-to-run-states-in-minion
 - https://www.hveem.no/salt-cli-visualization-using-runner-and-outputter
 - https://intothesaltmine.readthedocs.io/en/latest/chapters/development/writing-modules.html

RTFM:
 - https://docs.saltstack.com/en/2017.7/topics/development/modules/developing.html
 - https://docs.saltstack.com/en/2017.7/ref/modules/
 - https://docs.saltstack.com/en/2017.7/ref/clients/
 - https://docs.saltstack.com/en/2017.7/ref/output/all/index.html
 - https://docs.saltstack.com/en/2017.7/ref/modules/index.html#writing-execution-modules
 - https://docs.saltstack.com/en/2017.7/ref/modules/all/salt.modules.pillar.html
 - https://docs.saltstack.com/en/2017.7/ref/states/writing.html

Use the Source:
 - https://github.com/saltstack/salt/blob/2017.7/salt/grains/core.py
 - https://github.com/saltstack/salt/blob/2017.7/salt/grains/rest_sample.py

CONTEXT:
Unfinished, code stash: https://gist.github.com/renoirb/ccab5b51bff0eb91a37b42fd9efffb0c
Was originally written to be a "Runner" (i.e. only from master, do this on each minion)
Now, this will become an execution module (i.e. run on this minion, locally).

'''


## Imports: Runtime constants
GITLAB_ENDPOINT = 'https://gitlab.com'



## Imports: Execution module Salt runtime dependencies
# Python Libs
import logging
import json
from datetime import datetime

# Salt Libs
from salt.exceptions import CommandExecutionError
import salt.config
import salt.loader
import salt.utils.http


## Module: Initialization

# Hard Dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

log = logging.getLogger(__name__)

__virtualname__ = 'projects'

def __virtual__():
    '''
    Maintenance tasks for keeping a group of projects in sync with remote GitLab
    '''
    if HAS_REQUESTS:
        return __virtualname__
    else:
        return False, 'The projects module cannot be loaded: requests package unavailable.'
    if salt.utils.which('git') is None:
        return (False,
                'The git execution module cannot be loaded: git unavailable.')
    else:
        return True

## Module: Copy-Pasta from Salt modules/github.py

def _query(url,
           args=None,
           method='GET',
           header_dict=None,
           data=None,
           per_page=None):
    '''
    Make an HTTP call

    Copy-Pasta: https://github.com/saltstack/salt/blob/2017.7/salt/modules/github.py

    '''
    if not isinstance(args, dict):
        args = {}

    log.debug('GitLab URL: {0}'.format(url))

    if per_page and 'per_page' not in args.keys():
        args['per_page'] = per_page

    if header_dict is None:
        header_dict = {}

    privateToken = __salt__['environ.get']('PROJECTS_GITLAB_ACCESS_TOKEN', None)
    if privateToken:
        header_dict['Private-Token'] = privateToken

    if method != 'POST':
        header_dict['Accept'] = 'application/json'

    decode = True
    if method == 'DELETE':
        decode = False

    # GitHub paginates all queries when returning many items.
    # Gather all data using multiple queries and handle pagination.
    complete_result = []
    next_page = True
    page_number = ''
    while next_page is True:
        if page_number:
            args['page'] = page_number
        result = salt.utils.http.query(url,
                                       method,
                                       params=args,
                                       data=data,
                                       header_dict=header_dict,
                                       decode=decode,
                                       decode_type='json',
                                       headers=True,
                                       status=True,
                                       text=True,
                                       hide_fields=['access_token'],
                                       opts=__opts__,
                                       )
        log.debug(
            'GitLab Response Status Code: {0}'.format(
                result['status']
            )
        )

        if result['status'] == 200:
            if isinstance(result['dict'], dict):
                # If only querying for one item, such as a single issue
                # The GitHub API returns a single dictionary, instead of
                # A list of dictionaries. In that case, we can return.
                return result['dict']

            complete_result = complete_result + result['dict']
        else:
            raise CommandExecutionError(
                'GitLab Response Error: {0}'.format(result.get('error'))
            )

            # GitHub use Link Response headers
            # https://developer.github.com/v3/guides/traversing-with-pagination/
            # GitLab uses X-Next-Page
            # https://docs.gitlab.com/ee/api/#pagination
        try:
            next_page_header = result.get('headers').get('X-Next-Page', None)
        except AttributeError:
            # Only one page of data was returned; exit the loop.
            next_page = False
            continue

        if next_page_header:
            page_number = next_page_header
        else:
            # Last page already processed; break the loop.
            next_page = False

    return complete_result


## Module: Private functions

def _call_gitlab_projects_api(per_page=100):
    '''
    Make an API Call to GitLab

    e.g. GET 'https://gitlab.com/api/v4/projects?per_page=100'

    Missing:
    - Passing Private-Token header
    '''
    url = '{0}/api/v4/projects'.format(GITLAB_ENDPOINT)
    headers = {}
    msg = 'GET {0}'.format(url)
    log.debug(msg)
    # https://github.com/saltstack/salt/blob/latest/salt/modules/http.py
    # https://docs.saltstack.com/en/latest/ref/modules/all/salt.modules.http.html#salt.modules.http.query
    ### CANNOT work like this, 2017.7 does not support passing headers
    # req = __salt__['http.query'](
    #         url,
    #         headers,
    #       )
    ### /CANNOT
    ## IN THE MEANTIME...
    req = _query(
            url,
            per_page=per_page
        )
    return req



def _pillar_projects():
    projects = __salt__['pillar.get']('projects:projects', {})
    return projects



## Module: projects.list an example

def list():
    recv = _call_gitlab_projects_api()
    return recv


## Module: projects.g read a grain
def names():
    out = []
    projects = _pillar_projects()
    for name in projects:
        out.append(name)
    return out

def _execute_git_fetch_on_filesystem(project):
    user = 'vagrant'
    identity = '/home/vagrant/.ssh/id_rsa'
    cwd = '/data/projects/{0}/repo'.format(project)
    projectJson = '/data/projects/{0}/project.json'.format(project)
    pillarData = __salt__['pillar.get']('projects:projects:{0}'.format(project), {})
    for remote,url in pillarData.get('remotes', {}).iteritems():
        log.info('cd {0} ; git remote add {1} {2}'.format(cwd, remote, url))
        __salt__['git.remote_set'](cwd, url, remote=remote)
    log.info('Going to fetch {0} in {1}'.format(project, cwd))
    opts = '--all --tags --prune'
    __salt__['git.fetch'](cwd, identity=identity, user=user, opts=opts)
    pillarData['datetime'] = datetime.utcnow().isoformat()
    HEAD = __salt__['git.describe'](cwd)
    pillarData['HEAD'] = HEAD
    contents = json.dumps(
      pillarData,
      sort_keys=True,
      indent=2
    )
    log.info('Writing project definition in {0}'.format(projectJson))
    __salt__['file.write'](projectJson, contents)

def fetch(name=None):
    if name:
        _execute_git_fetch_on_filesystem(name)
    else:
        fetch_all()

def fetch_all():
    projects = names()
    for project in projects:
      _execute_git_fetch_on_filesystem(project)


