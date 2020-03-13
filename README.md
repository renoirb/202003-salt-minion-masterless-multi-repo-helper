# Salt Masterless Multi-Repo Projects helper

Experimentation with salt-minion to manage many git repositories.

In other words, run salt-minion inside a Docker container, that can help
maintain large group of Git repositories from [renoirb/projects-formula][renoirb-projects-formula]

[renoirb-projects-formula]: https://github.com/renoirb/projects-formula 'Renoir’s SaltStack formula from back in 2017 to manage code from many Git repositories'

## Use-Case

1. Re-Use [renoirb/projects-formula][renoirb-projects-formula] to make a team to synchronize many repositories clones consistently
1. Avoid asking the team to install tools manually, leverage Docker
1. Each team member can configure any projects they want, as long as they follow conventions described in [renoirb/projects-formula][renoirb-projects-formula]

## Bookmarks

### Salt and Docker

- https://github.com/clement1289/salt-masterless
- https://github.com/faisyl/alpine-salt
- https://github.com/saltstack/saltdocker/tree/master/Dockerfile.j2
- https://hub.docker.com/r/saltstack/salt

### See also

Other "multi repo" synchronization tools.

- https://myrepos.branchable.com/
- https://fabioz.github.io/mu-repo/grouping/
- https://github.com/esrlabs/git-repo
- https://github.com/mixu/gr
- https://gist.github.com/tbranyen/902154/
- https://gist.github.com/gullz/51abe21274655523df448b828a593318
- https://gist.github.com/stat0s2p/cfab6563ddbbfe2af7747a872e0d6395
