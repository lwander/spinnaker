ZONE=--zone=us-central1-f

gcloud config set container/use_client_certificate true &> /dev/null
gcloud container clusters describe spinnaker-host $ZONE &> /dev/null

if [ $? -ne 0 ]; then
    echo "Creating a new cluster... this will take a few minutes."
    gcloud container clusters create spinnaker-host --num-nodes 4 --machine-type n1-standard-2 $ZONE
else
    echo "Cluster 'spinnaker-host' already exists"
    gcloud container clusters get-credentials spinnaker-host $ZONE
fi

if [ $? -ne 0 ]; then
    exit $?
fi

python scripts/prestartup.py

if [ $? -ne 0 ]; then
    exit $?
fi

PROJECT=$(gcloud info --format='value(config.project)')
echo "Using project $PROJECT"

python scripts/prestartup-front50.py $PROJECT

if [ $? -ne 0 ]; then
    exit $?
fi

if [ -f "$HOME/.gcp/$PROJECT/account.json" ]; then
    echo "Using the existing service account in $HOME/.gcp/$PROJECT/account.json"
else
    echo "Generating a new service account..."
    DISPLAY_NAME=kube-gcs-sa
    gcloud iam service-accounts create spinnaker-gcs-account --display-name \
        $DISPLAY_NAME
    SA_EMAIL=$(gcloud iam service-accounts list --filter="displayName:$DISPLAY_NAME" --format='value(email)')
    USER=$(gcloud info --format='value(config.account)')
    gcloud projects add-iam-policy-binding $PROJECT --role="roles/editor" --member="serviceAccount:$SA_EMAIL"
    if [ $? -ne 0 ]; then
        exit $?
    fi
    if [ ! -d "$HOME/.gcp/$PROJECT" ]; then
        mkdir -p $HOME/.gcp/$PROJECT
    fi
    gcloud iam service-accounts keys create $HOME/.gcp/$PROJECT/account.json --iam-account=$SA_EMAIL
    if [ $? -ne 0 ]; then
        exit $?
    fi
fi

echo 
echo "$(tput bold)Presetup complete - now run$(tput sgr0)"
echo "bash scripts/startup-all.sh"
