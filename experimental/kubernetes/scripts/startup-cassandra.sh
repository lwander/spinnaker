gcloud compute disks create --size=200GB data-cassandra

kubectl create -f volumes/data/data-cassandra.yaml

kubectl create -f claims/data/data-cassandra.yaml

kubectl create -f svcs/data/data-cassandra.yaml

kubectl create -f rcs/data/data-cassandra.yaml

echo
echo "Waiting for cassandra to come up..."
echo

echo "Setting keyspaces for cassandra..."
echo

kubectl create -f jobs/data/data-cassandra-keys.yaml

SUCCESS=$(kubectl get job data-cassandra-keys --namespace=spinnaker -o=jsonpath="{.status.succeeded}")

while [ $SUCCESS -ne "1" ]; do
    SUCCESS=$(kubectl get job data-cassandra-keys --namespace=spinnaker -o=jsonpath="{.status.succeeded}")
done


echo
echo "Cleaning keyspace job..."
echo

kubectl delete job data-cassandra-keys --namespace=spinnaker
