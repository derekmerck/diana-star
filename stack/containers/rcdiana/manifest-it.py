#! python

"""
Manifest-It
Merck, Spring 2018

manifest-it.py can retag, manifest, and push multiple services and architecture produced by ansible-container using the 'project-arch-service' naming convention.  Manifesting requires docker-ce edge in 'experimental mode'.

Usage:

$ manifest-it.py -n rcdiana -a amd64 armv7l -images broker dicom worker movidius

or

$ manifest-it.py -f diana_manifest.yml

where manifest rule file looks like this:

```yml
namespace: rcdiana
images:
  - broker
  - dicom
  - worker
  - movidius
architectures:
  - amd64
  - armv7l
```

Note that armv7hf is arch: arm, variant: v7 in docker's ontology, which makes sense, but is poorly documented.  Acceptable architecture values are listed here:

https://raw.githubusercontent.com/docker-library/official-images/a7ad3081aa5f51584653073424217e461b72670a/bashbrew/go/vendor/src/github.com/docker-library/go-dockerlibrary/architecture/oci-platform.go

"""

import yaml, logging
from subprocess import call
from argparse import ArgumentParser

def parse_args():

    p = ArgumentParser("Retag, manifest, and push multiple services and architecture produced by ansible-container with the 'project-arch-service' naming convention.  Manifesting requires docker-ce edge in 'experimental mode'.")
    p.add_argument("-n", "--namespace", help="Target namespace", default="rcdiana")
    p.add_argument("-a", "--architectures", help="Multiarchitecture manifest entries", default=["amd64", "armv7hf"])
    p.add_argument("-i", "--images", help="List of service images to process")
    p.add_argument("-f", "--file", help="yml file with manifest rules")
    p.add_argument('-d', '--dryrun', action="store_true", help="Retag and manifest but do not push")

    opts = p.parse_args()

    if opts.file:
        with open(opts.file, 'r') as f:
            data = yaml.safe_load(f)
            opts.namespace = data.get('namespace', opts.namespace)
            opts.images = data.get('images', opts.images)
            opts.architectures = data.get('architectures', opts.architectures)

    return opts

def docker_tag(target, tag):
    cmd = ['docker', 'tag', target, tag]
    logging.debug(cmd)
    call(cmd)

def docker_push(tag):
    cmd = ['docker', 'push', tag]
    logging.debug(cmd)
    call(cmd)

def docker_manifest_create(tag, aliases):
    cmd = ['docker', 'manifest', 'create', tag, *aliases]
    logging.debug(cmd)
    call(cmd)

def docker_manifest_annotate(tag, alias, arch="amd64", variant=None, os="linux"):
    cmd = ['docker', 'manifest', 'annotate',
          tag, alias,
          '--arch', arch,
          '--os', os ]
    if variant:
        cmd = cmd + ['--variant', variant]
    logging.debug(cmd)
    call(cmd)

def docker_manifest_push(tag):
    cmd = ['docker', 'manifest', 'push', tag]
    logging.debug(cmd)
    call(cmd)


if __name__ == "__main__":

    opts = parse_args()

    n = opts.namespace
    for i in opts.images:
        for a in opts.architectures:

            source_tag = "{}-{}-{}".format(n, a, i)
            target_tag = "{}/{}:{}".format(n, i, a)

            docker_tag(source_tag, target_tag)
            if not opts.dryrun:
                docker_push(target_tag)

    for i in opts.images:
        main_tag = "{}/{}:latest".format(n,i)
        alias_tags = []
        for a in opts.architectures:
            alias_tags.append("{}/{}:{}".format(n, i, a))
        docker_manifest_create(main_tag, alias_tags)

    for i in opts.images:
        main_tag = "{}/{}:latest"
        for a in opts.architectures:

            if a == "armv7hf":
                aa = "arm"
                vv = "7"
            elif a == "amd64":
                aa = a
                vv = None
            else:
                raise NotImplementedError

            alias = "{}/{}:{}".format(n, i, a)
            docker_manifest_annotate(main_tag,
                                     alias,
                                     arch=aa,
                                     variant=vv,
                                     os="linux")

        if not opts.dryrun:
            docker_manifest_push(main_tag)
