# Javelin: Defects4J Extraction Pipeline

This repository contains the strict environment setup and automated extraction scripts required to evaluate the Javelin Spectrum-Based Fault Localization (SBFL) tool using the Defects4J benchmark. 

Because Javelin evaluates modern GitHub projects alongside historical Apache projects to prove the statistical power of Ochiai-MS, this environment heavily utilizes SDKMAN to bridge modern Java environments with legacy compilation requirements inside a WSL Ubuntu instance.

---

## 1. Automated Installation (Recommended)

To completely automate the setup of SDKMAN, the required Java versions, and the Defects4J framework, use the provided installation script.

Step 1: Create the script file in your terminal:
    nano install_defects4j.sh

Step 2: Paste the following code into the file:

    #!/bin/bash
    set -e
    
    echo "========================================================"
    echo "🎯 Javelin: Automated Defects4J Environment Installer"
    echo "========================================================"
    
    USER_HOME=$HOME
    echo "📁 Detected Ubuntu Home Directory: $USER_HOME"
    echo ""
    
    echo "🛠️ Java Environment Setup"
    echo "INFO: Defects4J strictly requires Java 11 for its framework, and Java 8 to compile older bugs."
    echo "Since GitBug-Java requires modern Java (e.g., Java 21), we highly recommend using SDKMAN."
    echo ""
    read -p "Do you want to install and use SDKMAN for Java management? (y/n): " use_sdkman
    
    if [[ "$use_sdkman" =~ ^[Yy]$ ]]; then
        echo "Installing base dependencies for SDKMAN..."
        sudo apt-get update -y && sudo apt-get install -y zip unzip curl python3-pip
    
        if [ ! -d "$USER_HOME/.sdkman" ]; then
            echo "Downloading SDKMAN..."
            curl -s "https://get.sdkman.io" | bash
        fi
    
        export SDKMAN_DIR="$USER_HOME/.sdkman"
        [[ -s "$USER_HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$USER_HOME/.sdkman/bin/sdkman-init.sh"
    
        echo "Checking and installing required Java versions via SDKMAN..."
        sdk install java 11.0.22-tem || true
        sdk install java 8.0.402-tem || true
        sdk install java 21.0.2-tem || true
    
        echo "Setting default Java to 11 for the Defects4J installation..."
        sdk default java 11.0.22-tem
        sdk use java 11.0.22-tem
    else
        echo "⚠️ Skipping SDKMAN. Checking system Java..."
        # Add basic java check logic here if SDKMAN is skipped
    fi
    
    echo ""
    echo "📦 Installing underlying Linux Dependencies for Defects4J..."
    sudo apt-get update -y
    sudo apt-get install -y git subversion perl curl cpanminus make gcc
    
    echo ""
    echo "⚙️ Cloning Defects4J framework..."
    if [ ! -d "$USER_HOME/defects4j" ]; then
        cd "$USER_HOME"
        git clone https://github.com/rjust/defects4j.git
    fi
    cd "$USER_HOME/defects4j"
    
    echo ""
    echo "🐪 Configuring Perl Modules safely in user space..."
    cpanm --local-lib="$USER_HOME/perl5" local::lib && eval $(perl -I "$USER_HOME/perl5/lib/perl5/" -Mlocal::lib)
    if ! grep -q "perl5/lib/perl5" "$USER_HOME/.bashrc"; then
        echo 'eval $(perl -I ~/perl5/lib/perl5/ -Mlocal::lib)' >> "$USER_HOME/.bashrc"
    fi
    cpanm --installdeps .
    
    echo ""
    echo "📥 Initializing Defects4J Bug Databases..."
    ./init.sh
    
    echo ""
    echo "🔗 Adding Defects4J to your system PATH..."
    if ! grep -q "defects4j/framework/bin" "$USER_HOME/.bashrc"; then
        echo 'export PATH=$PATH:"$HOME/defects4j/framework/bin"' >> "$USER_HOME/.bashrc"
    fi
    export PATH=$PATH:"$USER_HOME/defects4j/framework/bin"
    
    echo ""
    echo "✅ Defects4J Installation Complete! Please run 'source ~/.bashrc'"

Step 3: Make it executable and run it:
    chmod +x install_defects4j.sh
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

(Ensure you are using Java 11 or Java 8 depending on the project's age!)
    cd ~/javelin-workspaces/Defects4J-Lang-1-buggy
    defects4j compile
    defects4j test

The compiled .class and .java files are now ready to be processed by Javelin to generate your CSV ranking matrices!