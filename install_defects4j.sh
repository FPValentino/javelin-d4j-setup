#!/bin/bash
set -e # Stops the script if any command fails

echo "========================================================"
echo "🎯 Javelin: Automated Defects4J Environment Installer"
echo "========================================================"

# 1. Automatically locate the user's home directory
USER_HOME=$HOME
echo "📁 Detected Ubuntu Home Directory: $USER_HOME"
echo ""

# 2 & 3. SDKMAN and Java Version Management
echo "🛠️ Java Environment Setup"
echo "INFO: Defects4J strictly requires Java 11 for its framework, and Java 8 to compile older bugs."
echo "Since GitBug-Java requires modern Java (e.g., Java 21), we highly recommend using SDKMAN."
echo "SDKMAN allows you to install multiple Java versions and swap between them instantly without breaking your Linux OS."
echo ""
read -p "Do you want to install and use SDKMAN for Java management? (y/n): " use_sdkman

if [[ "$use_sdkman" =~ ^[Yy]$ ]]; then
    echo "Installing base dependencies for SDKMAN..."
    sudo apt-get update -y && sudo apt-get install -y zip unzip curl

    if [ ! -d "$USER_HOME/.sdkman" ]; then
        echo "Downloading SDKMAN..."
        curl -s "https://get.sdkman.io" | bash
    else
        echo "SDKMAN is already installed!"
    fi

    # Source SDKMAN so we can use it immediately in this script
    export SDKMAN_DIR="$USER_HOME/.sdkman"
    [[ -s "$USER_HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$USER_HOME/.sdkman/bin/sdkman-init.sh"

    echo "Checking and installing required Java versions via SDKMAN..."
    sdk install java 11.0.22-tem || true
    sdk install java 8.0.402-tem || true

    echo "Setting default Java to 11 for the Defects4J installation..."
    sdk default java 11.0.22-tem
    sdk use java 11.0.22-tem
else
    echo "⚠️ Skipping SDKMAN. Checking system Java..."
    if ! command -v java &> /dev/null; then
        echo "❌ Java is not installed on this system."
        read -p "Would you like to install OpenJDK 11 via apt now? (y/n): " install_apt_java
        if [[ "$install_apt_java" =~ ^[Yy]$ ]]; then
            sudo apt-get update -y && sudo apt-get install -y openjdk-11-jdk
        else
            echo "❌ Java 11 is required to proceed. Exiting."
            exit 1
        fi
    else
        # Extract the major Java version number
        JAVA_VER=$(java -version 2>&1 | head -1 | cut -d'"' -f2 | sed '/^1\./s///' | cut -d'.' -f1)
        echo "✅ Detected system Java version: $JAVA_VER"
        if [ "$JAVA_VER" != "11" ]; then
            echo "⚠️ WARNING: Your active Java is not version 11. Defects4J Perl scripts may fail!"
            sleep 3
        fi
    fi
fi

# 4. Install Defects4J Linux Dependencies
echo ""
echo "📦 Installing underlying Linux Dependencies for Defects4J..."
sudo apt-get update -y
sudo apt-get install -y git subversion perl curl cpanminus make gcc python3-pip

# 5. Clone Defects4J into the Home Directory
echo ""
echo "⚙️ Cloning Defects4J framework..."
if [ -d "$USER_HOME/defects4j" ]; then
    echo "⚠️ Directory $USER_HOME/defects4j already exists. Skipping git clone."
else
    cd "$USER_HOME"
    git clone https://github.com/rjust/defects4j.git
fi

cd "$USER_HOME/defects4j"

# 6. Install Perl Modules Safely (Without Sudo)
echo ""
echo "🐪 Configuring Perl Modules safely in user space..."
cpanm --local-lib="$USER_HOME/perl5" local::lib && eval $(perl -I "$USER_HOME/perl5/lib/perl5/" -Mlocal::lib)

# Ensure perl library path is saved forever
if ! grep -q "perl5/lib/perl5" "$USER_HOME/.bashrc"; then
    echo 'eval $(perl -I ~/perl5/lib/perl5/ -Mlocal::lib)' >> "$USER_HOME/.bashrc"
fi
cpanm --installdeps .

# 7. Initialize Framework and Download Bug Databases
echo ""
echo "📥 Initializing Defects4J Bug Databases..."
echo "⏳ (This downloads historical repositories and will take a few minutes)..."
./init.sh

# 8. Add to PATH
echo ""
echo "🔗 Adding Defects4J to your system PATH..."
if ! grep -q "defects4j/framework/bin" "$USER_HOME/.bashrc"; then
    echo 'export PATH=$PATH:"$HOME/defects4j/framework/bin"' >> "$USER_HOME/.bashrc"
fi
export PATH=$PATH:"$USER_HOME/defects4j/framework/bin"

echo ""
echo "✅ Defects4J Installation Complete!"
echo "Running test query on project 'Lang'..."
defects4j info -p Lang || echo "⚠️ Framework is installed, but you may need to reload your terminal to use it."

echo "========================================================"
echo "🎉 Setup Finished! Please run the following command to finalize:"
echo "source ~/.bashrc"
echo "========================================================"