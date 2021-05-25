#!/bin/bash
# rsync code to correct location, restart gunicorn server

# test for a command argument
echo `whoami`
if [ ! -n "$1" ];
then 
        echo "Usage: `basename $0` environment"
        exit -1
fi
# directory where the checked out repo is
SOURCEDIR=/home/wide/nufuk/

cd $SOURCEDIR
git pull

#the environment we are using (staging, production)
SITE_ENV="$1"
DESTDIR="/var/www/fuk/$SITE_ENV"
if [ ! -d "$DESTDIR" ] ; then
        echo "Target site environment does not exist."
        exit -1
fi

# Copy the site code over, excluding files in the separate excludes file.
rsync -a --delete --exclude-from=rsync-excludes.txt $SOURCEDIR $DESTDIR

sudo service gunicorn-$SITE_ENV restart
