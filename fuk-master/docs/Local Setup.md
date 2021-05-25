## Setting up a local install

There are two parts to setting up a local install of the fuk website on your Mac: get Github working, so you can manage code changes, and get Fabric working so you can push changes to the server. 

[Github](http://github.com) is our version control server, and we use their Mac app to make it easier to keep changes in sync. [Fabric](http://fabfile.org) is a Python-based automation system to make it easier to deploy complex web applications to multiple servers.

### Get Github working

This is pretty straightforward. 

- Download a copy of [Github for Mac](http://mac.github.com)
- Once you get it installed and up and running with your Github account credentials, visit the [nufuk repository on Github](https://github.com/BenAtWide/nufuk)
- Click the 'Clone in Mac' button. The app will prompt you for a save location, choose whatever makes sense for your local system, but try and get something with short path names eg /code/nufuk as you will see later it will make life easier!
- Once it has downloaded and saved the repo, click on the arrow on the right hand side of the repo name in the Github app.
- In the black strip on the left hand side, click 'Changes'.
- Click the button to the left of the 'Commit' button, so that it turns green. See screenshot:

[[images/commitandsync.png]]

This setting means that every time you upload a change (or 'commit'), the app will pull down and synchronise any changes made by others and automatically merge them if it can. 

### Get Fabric working

The other half of this recipe requires a bit of command line action to get working. Open up a Terminal window, and type (or copy and paste) these commands.

`sudo easy_install pip`  
This installs the Python package manager called pip, which helps you manage Python programs on your system. The sudo command means that you will need to type your password, as it will be installing system-wide.

`sudo pip install fabric`  
This will install the Fabric program and the various bits and bobs on which it depends.

If there are no errors so far, check this is all working by changing to the code directory that you chose in Github.

`cd code/nufuk` or whatever..  

Once you are there, run the following to make sure fabric is working  

`fab -l`  

It should list out a load of available Fabric commands. If so, all is working, congratulations! If not give me a shout :-(  

### Uploading a change

Assuming all is working as above, lets make a change and upload it. Open up the whole code folder in your text editor, and navigate to the following file:  
fuk/templates/index.html

Make a change to this file and save. It's the home page of the site, and could really do with some attention!

Switch back to Github, and in the black sidebar, click on the Changes button. You will see a list of changed files and a 'diff' on the right showing the actual changes in the file. Add a short message in the Commit summary field describing your change, and hit the Commit button.

At this point, because we chose to 'Commit and Sync' earlier, the Github app will check for and download any other changes on the server, as well as uploading yours.

Once Github has done its thing, go back to the Terminal window, which is hopefully still open at the root of the site code.

Type the following  

`fab dev deploy`

It will ask you for a password for the wide user account on basement.widemedia.com. It may ask you for it a couple of times during the deploy process, so worth having it on the clipboard ready to paste. Once all this is working, we can add some key files to the server so that you don't have to enter a password.

Lots of text will scroll by and eventually it will all be done. At that point you can open up http://dev.fuk.co.uk and your change should be live on the home page.
