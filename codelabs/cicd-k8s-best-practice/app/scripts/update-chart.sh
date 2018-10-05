#!/usr/bin/env bash

helm package manifests/demo

# todo(lwander): incorporate versioning
gsutil cp demo-0.1.0.tgz gs://spin-gcs-bucket-pkt7q2deswc40mbqkjym-1538143684/manifests/demo/demo.tgz

rm demo-0.1.0.tgz

gsutil cp manifests/production/values.yaml gs://spin-gcs-bucket-pkt7q2deswc40mbqkjym-1538143684/manifests/demo/production/values.yaml

gsutil cp manifests/staging/values.yaml gs://spin-gcs-bucket-pkt7q2deswc40mbqkjym-1538143684/manifests/demo/staging/values.yaml
