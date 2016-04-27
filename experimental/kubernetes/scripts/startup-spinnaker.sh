echo "Starting all services..."
echo

kubectl create -f svcs/spin/spin-clouddriver.yaml
kubectl create -f svcs/spin/spin-deck.yaml
kubectl create -f svcs/spin/spin-echo.yaml
kubectl create -f svcs/spin/spin-front50.yaml
kubectl create -f svcs/spin/spin-gate.yaml
kubectl create -f svcs/spin/spin-igor.yaml
kubectl create -f svcs/spin/spin-orca.yaml

echo
echo "Starting all replication controllers..."
echo

kubectl create -f rcs/spin/spin-clouddriver.yaml
kubectl create -f rcs/spin/spin-deck.yaml
kubectl create -f rcs/spin/spin-echo.yaml
kubectl create -f rcs/spin/spin-front50.yaml
kubectl create -f rcs/spin/spin-gate.yaml
kubectl create -f rcs/spin/spin-igor.yaml
kubectl create -f rcs/spin/spin-orca.yaml
