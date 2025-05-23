#!/bin/bash

set -e

#PACKAGE_NAME="your-package-name"
PYTHON_VERSION="3.11.6"
VENV_DIR=".venv"

# Detect OS
OS=$(uname)
echo "🖥️ Detected OS: $OS"

install_pyenv_mac() {
    echo "🍏 Installing pyenv and dependencies on macOS..."
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install it from https://brew.sh first."
        exit 1
    fi

    brew update
    brew install pyenv

    # Add pyenv to shell
    if ! grep -q 'pyenv init' ~/.zshrc; then
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
        echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
        echo 'eval "$(pyenv init -)"' >> ~/.zshrc
        echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
    fi

    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
}

install_pyenv_linux() {
    echo "🐧 Installing pyenv and dependencies on Linux..."
    sudo apt update
    sudo apt install -y make build-essential libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
        libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git

    if [ ! -d "$HOME/.pyenv" ]; then
        git clone https://github.com/pyenv/pyenv.git ~/.pyenv
    fi

    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"

    if ! grep -q 'pyenv init' ~/.bashrc; then
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
        echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
        echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    fi

    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
}

install_pyenv() {
    if command -v pyenv &> /dev/null; then
        echo "✅ pyenv is already installed."
        return
    fi

    case "$OS" in
        Darwin)
            install_pyenv_mac
            ;;
        Linux)
            install_pyenv_linux
            ;;
        *)
            echo "❌ Unsupported OS: $OS"
            exit 1
            ;;
    esac
}

# Install pyenv if needed
install_pyenv

# Ensure correct Python version
if ! pyenv versions --bare | grep -qx "$PYTHON_VERSION"; then
    echo "⬇️ Installing Python $PYTHON_VERSION..."
    pyenv install "$PYTHON_VERSION"
else
    echo "✅ Python $PYTHON_VERSION already installed."
fi

pyenv local "$PYTHON_VERSION"

# Set up virtual environment
echo "🐍 Creating virtual environment..."
python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install package
# echo "📦 Installing $PACKAGE_NAME..."
# pip install --upgrade pip
# pip install "$PACKAGE_NAME"

echo "Setup complete!"
echo "✅ Virtual environment is ready."
#echo "✅ $PACKAGE_NAME installed."

