#!/bin/bash
sudo kubectl delete service citus-master 
sudo kubectl delete service citus-workers
sudo kubectl delete deployment citus-master
sudo kubectl delete statefulset citus-worker
sudo kubectl delete persistentvolumeclaim postgres-pv-claim
sudo kubectl delete persistentvolume postgres-pv-volume
sudo kubectl delete secret postgresql-secrets
sudo kubectl delete secret postgres-secrets-params

