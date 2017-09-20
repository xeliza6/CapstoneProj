# Setting up the repository

#1. Install Git on your computer
- Windows https://git-scm.com/download/win
- Mac (can't test this for you but will trust the internet)  
`ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew doctor`  
`brew install git`
- You might have to wait a bit or restart commandline before git is recognized as a command

#2. Configure user settings:  
- `$ git config --global user.name "John Doe"`  
- `$ git config --global user.email johndoe@example.com`

#3. Setting the repository to your machine  
- Go to the directory you want your repository to be in  
- Clone the repository: `git clone https://github.com/xeliza6/CapstoneProj.git`
 
#4. cd into the repository and `git pull`