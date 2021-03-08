#!/bin/bash
#Disable swapping
sudo apt install selinux-utils
setenforce 0
#sed -i --follow-symlinks 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
swapoff -a

sudo apt-get update && sudo apt-get install -y apt-transport-https curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl


#Set up on master
sudo kubeadm init
HOME=/home/azureuser
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
sudo kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')"
sudo kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.2.0/aio/deploy/recommended.yaml
yes | sudo apt-get install firewalld

#On workers

#After restart
sudo pico /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
add ExecStart=/usr/bin/kubelet $KUBELET_KUBECONFIG_ARGS $KUBELET_CONFIG_ARGS $KUBELET_KUBEADM_ARGS $KUBELET_EXTRA_ARGS --cgroup-driver=systemd
sudo systemctl daemon-reload
sudo systemctl restart kubelet
sudo systemctl status kubelet
#to see logs: journalctl -u kubelet

#Disable firewall when worker cannot connect to master
sudo iptables --flush
sudo iptables -tnat --flush
sudo systemctl stop firewalld
sudo systemctl disable firewalld
sudo systemctl restart docker

sudo kubeadm join 10.0.0.4:6443 --token mxsbsk.r099tbquv4pjew26     --discovery-token-ca-cert-hash sha256:32995b08986ee7e4a230a73402ffc1dc4ec66d995c9ab17a0a6a31bac8909ec4 


###Pods
#Describe Pod
kubectl describe pods postgres
kubectl get pod
kubectl get svc postgres