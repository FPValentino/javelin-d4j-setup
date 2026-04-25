# Javelin: Defects4J Extraction Pipeline

This repository contains the strict environment setup and automated extraction scripts required to evaluate the Javelin Spectrum-Based Fault Localization (SBFL) tool using the Defects4J benchmark. 

Because Javelin evaluates modern GitHub projects alongside historical Apache projects to prove the statistical power of Ochiai-MS, this environment heavily utilizes SDKMAN to bridge modern Java environments with legacy compilation requirements inside a WSL Ubuntu instance.

---

## 1. Automated Installation (Recommended)

To completely automate the setup of SDKMAN, the required Java versions, and the Defects4J framework, use the installation script included in this repository.

### Step 1: Clone this repository to your WSL Ubuntu environment
    git clone https://github.com/FCValentino/javelin-d4j-setup.git
    cd javelin-d4j-setup

### Step 2: Make the script executable
    chmod +x install_defects4j.sh

### Step 3: Run the installer
    ./install_defects4j.sh

---

## 2. Manual Installation (Alternative)

If you prefer to install the components manually, follow these steps:

### Java Environment (SDKMAN)
    curl -s "https://get.sdkman.io" | bash
    source "$HOME/.sdkman/bin/sdkman-init.sh"
    sudo apt-get update
    sudo apt-get install -y zip unzip python3-pip
    sdk install java 11.0.22-tem
    sdk install java 8.0.402-tem
    sdk install java 21.0.2-tem

> Usage Note: Always ensure your terminal is running Java 11 (sdk use java 11.0.22-tem) before running any defects4j framework commands.

### Defects4J Framework
    sudo apt-get install -y git subversion perl curl cpanminus make gcc
    cd ~
    git clone https://github.com/rjust/defects4j.git
    cd defects4j
    cpanm --local-lib=~/perl5 local::lib && eval $(perl -I ~/perl5/lib/perl5/ -Mlocal::lib)
    echo 'eval $(perl -I ~/perl5/lib/perl5/ -Mlocal::lib)' >> ~/.bashrc
    cpanm --installdeps .
    ./init.sh
    echo 'export PATH=$PATH:"$HOME/defects4j/framework/bin"' >> ~/.bashrc
    source ~/.bashrc

---

## 3. The Extraction Script (extract_d4j.py)

This repository includes an interactive Python script (extract_d4j.py) designed to safely extract both the -buggy and -fixed versions of a Defects4J bug into a unified workspace. This ensures compatibility with the automated generate_patches.py pipeline.

### Script Prerequisites
The script requires a global installation of the questionary library to render the interactive terminal UI.

    pip3 install questionary --break-system-packages

### Running the Extractor
Run the script from anywhere in your terminal:

    python3 extract_d4j.py

1. Select a Project: Use your arrow keys to select a classic or modern benchmark project (e.g., Lang, Math, Closure).
2. Define the Range: Input the specific bugs you wish to extract (e.g., 1-5, or 1, 3, 10).
3. Output: The script will automatically safely extract all selected bugs into ~/javelin-workspaces/.

---

## 4. Post-Extraction Compilation

Once extracted, navigate to the buggy folder and compile using the Defects4J wrapper. 
### Compilation
(Ensure you are using Java 11 or Java 8 depending on the project's age!)

    cd ~/javelin-workspaces/Defects4J-Lang-1-buggy (Only Example Project)
    defects4j compile
    defects4j test

The compiled .class and .java files are now ready to be processed by Javelin to generate your CSV ranking matrices!
