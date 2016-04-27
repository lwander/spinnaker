kubectl delete pv,pvc,rc,svc,job -l stack=cassandra --namespace=spinnaker

gcloud compute disks delete data-cassandra
