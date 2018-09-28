#!/usr/bin/env bash

gcloud container builds submit -q --tag gcr.io/spinnaker-summit-demo-project/demo src/ --project spinnaker-summit-demo-project
