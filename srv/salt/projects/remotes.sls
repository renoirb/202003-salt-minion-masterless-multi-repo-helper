{% macro git_remote(creates, origin, args={}) %}

{% set user = args.get('user', None) %}
{% set identity = args.get('identity', None) %}

{% set mirror = args.get('mirror', None) %}

{% set branchName = args.get('branch', 'master') %}
{% set remotes = args.get('remotes', []) %}

{% set before_unpack_remote = args.get('before', []) %}

{{ creates }} reset origin for to {{ origin }}:
  cmd.run:
    - cwd: {{ creates }}
    - name: |
        git remote rm origin || true
        git remote add origin {{ origin }}

{% for remote_name,remote in remotes.items() %}
git remote add {{ remote_name }} {{ remote }}:
  cmd.run:
    - unless: grep -q -e 'remote "{{ remote_name }}' .git/config
    - cwd: {{ creates }}
{% endfor %}
{% endmacro %}

{% from "projects/map.jinja" import projects with context %}
{%- set projectsList = salt['pillar.get']('projects:projects', {}) %}
{%- set project_repo_parent = projects.lookup.root_dir ~ '%s/' -%}
{%- set project_repo_dir = project_repo_parent ~ projects.lookup.project_clone_subdir -%}
{%-   set initialSettings = {
          "mirror": True,
} %}
{%-   for slug,obj in projectsList.items() %}
{%-     do obj.update(initialSettings) %}
{%-     if obj.origin is defined %}
{%-       set repo_dir = project_repo_dir|format(slug) %}
{%-       if obj.ssh_key is not defined %}
{%-         set add_identity = {
                  "identity": projects.lookup.ssh_key
            } %}
{%-       else %}
{%-         set add_identity = {
                  "identity": obj.ssh_key
            } %}
{%-       endif %}
{%-       do obj.update(add_identity) %}
{{        git_remote(repo_dir, obj.origin, obj) }}
{%     endif %}
{%-   endfor %}


