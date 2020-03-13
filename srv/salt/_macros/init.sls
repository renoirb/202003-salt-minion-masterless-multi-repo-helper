{%- macro home_subfolder_owned_by(subdir, username) -%}
{%-   set homedir_path = '/home/%s/%s/'|format(username, subdir)  %}
{{ homedir_path }}:
  file.directory:
    - makedirs: True
    - user: {{ username }}
    - group: {{ username }}
    - recurse:
      - user
      - group
{%- endmacro  %}

{%  macro append_include_only_if_exists(slsName, salt_or_pillar = 'salt') -%}
{#
 # https://docs.saltstack.com/en/latest/topics/jinja/index.html
 #}
{%-   set isValidSaltOrPillar = salt_or_pillar | check_whitelist_blacklist(whitelist=['salt', 'pillar']) -%}
{%-   if isValidSaltOrPillar -%}
{%-     set conditional_sls_template = slsName.replace('.', '/') -%}
{%-     set conditional_sls_file_template = '/srv/%s/' ~ conditional_sls_template ~ '.sls' -%}
{%-     set conditional_sls_file = conditional_sls_file_template|format(salt_or_pillar) -%}
{%-     if salt['file.file_exists'](conditional_sls_file) %}
  - {{ slsName }}
{%-     endif -%}
{%-   endif -%}
{%- endmacro  %}
