to clone and use repo, run the following commands
 - git clone --recurse-submodules https://github.com/cloudbrownie/2024cosworkshop.git new_directory
 - cd new_directory
 - git submodule update --init --recursive

to set new upstream remote for your own repo
 - git remote set-url origin "your repo url"
 - git push --recurse-submodules=on-demand

