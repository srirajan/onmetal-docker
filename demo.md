

 * List On Metal images
```
nova image-list |egrep 'Name|OnMetal; 
```

 * List On Metal images
```
nova flavor-list |egrep 'Name|OnMetal'
```

 * Build a Ubuntu 14.04 LTS (Trusty Tahr) On Metal server

```
date; nova boot --flavor onmetal-compute1 --image 6cbfd76c-644c-4e28-b3bf-5a6c2a879a4a --key-name sri-mb play01 --progress; date
```


 * Basic setup
```
apt-get update
apt-get upgrade
update-rc.d docker.io  defaults
docker pull ubuntu
docker pull centos
```
