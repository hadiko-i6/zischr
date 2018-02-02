# zischr

zischr is a self-service accounting solution for moderate group sizes (15-20 people)

## Deployment on Raspberry Pi 3

(This assumes the Pi has the single purpose of running zischr. Otherwise, you should consider a better isolation strategy. We're happy about a PR with scripts / Dockerfiles / whatever for the `deployment/` directory).

Install Raspbian Stretch on your Raspberry Pi 3 ([Official Guide](https://www.raspberrypi.org/documentation/installation/installing-images/README.md)).
Change the password of the default `pi`.
Afterwards, run the following commands as **root**:

```
apt-get install git
cd /root
git clone https://github.com/hadiko-i6/zischr.git /root/zischrdb_checkout
mkdir /root/zischrdb
/root/zischrdb_checkout/deployment/raspi3/deploy.sh
```  

This installs build & runtime dependencies and deploys a **copy** of the relvant runtime files ot `/zischr`.
`deploy.sh` also removes everythin in `/zischr` (the fsdb is kept in `/root/zischrdb`, no worries).

To keep a Git history of zischrdb, take a look into the hook functionality of the `backend server` command in the `zischr-backend.service` file.

### Updating
```
cd /root/zischrdb_checkout
git pull --ff-only
deployment/raspi3/deploy.sh
```
