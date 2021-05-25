#!/bin/bash

# Bootstrap a local install of the fuk code.

# Get some dependencies in. Pip, fabric and virtualenv all need to be installed
# at system python level.
# Also needs git, but should come with the gui.
# And libjpeg. Follow these instructions http://gpiot.com/mac-os-x-lion-install-the-python-image-library-pil/

sudo easy_install pip
sudo pip install fabric
sudo pip install cuisine
sudo pip install virtualenv


git clone https://github.com/BenAtWide/nufuk.git

# or do it in Github Mac?

# once virtualenv has activated

pip install -r requirements.txt