#!/bin/bash

set -e

APP_NAME="ollumar"
INSTALL_DIR="$HOME/$APP_NAME"
VENV_DIR="$INSTALL_DIR/environment"
BIN_PATH="/usr/local/bin/$APP_NAME"
SOURCE_DIR="$(pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
VIOLET='\033[0;35m'
NC='\033[0m'

print_header() {
    clear
    echo -e "${NC}"
    echo "╔═════════════════════════════════════╗"
    echo "║                                     ║"
    echo -e "║          ${VIOLET}Ollumar Installer${NC}          ║"
    echo "║                                     ║"
    echo "╚═════════════════════════════════════╝"
    echo -e "${NC}"
}

check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 is not installed. Please install it and try again.${NC}"
        exit 1
    fi
    
    if ! python3 -c "import venv" &> /dev/null; then
        echo -e "${RED}Error: python3-venv is not installed. Please install it and try again.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}All dependencies are satisfied.${NC}"
}

install_app() {
    local create_terminal_command=$1
    
    print_header
    echo -e "${YELLOW}Installing $APP_NAME...${NC}"
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Installation directory already exists.${NC}"
        read -p "Do you want to reinstall? [y/N] " choice
        case "$choice" in
            y|Y ) 
                echo "Removing existing installation..."
                rm -rf "$INSTALL_DIR"
                ;;
            * ) 
                echo "Installation aborted."
                read -p "Press Enter to return to the main menu..."
                show_main_menu
                return
                ;;
        esac
    fi
    
    check_dependencies
    
    mkdir -p "$INSTALL_DIR"
    
    echo "Creating directory structure..."
    mkdir -p "$INSTALL_DIR/config"
    mkdir -p "$INSTALL_DIR/ui"
    mkdir -p "$INSTALL_DIR/api"
    mkdir -p "$INSTALL_DIR/tools"
    mkdir -p "$INSTALL_DIR/chat"
    mkdir -p "$INSTALL_DIR/utils"
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/data/history"
    
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    source "$VENV_DIR/bin/activate"
    echo "Installing Python dependencies..."
    pip install --upgrade pip
    pip install prompt_toolkit rich duckduckgo_search requests beautifulsoup4
    
    echo "Copying application files..."
    cp "$SOURCE_DIR/main.py" "$INSTALL_DIR/"
    
    touch "$INSTALL_DIR/config/__init__.py"
    touch "$INSTALL_DIR/ui/__init__.py"
    touch "$INSTALL_DIR/api/__init__.py"
    touch "$INSTALL_DIR/tools/__init__.py"
    touch "$INSTALL_DIR/chat/__init__.py"
    touch "$INSTALL_DIR/utils/__init__.py"
    
    cp "$SOURCE_DIR/config/settings.py" "$INSTALL_DIR/config/"
    cp "$SOURCE_DIR/ui/display.py" "$INSTALL_DIR/ui/"
    cp "$SOURCE_DIR/api/models.py" "$INSTALL_DIR/api/"
    cp "$SOURCE_DIR/tools/search.py" "$INSTALL_DIR/tools/"
    cp "$SOURCE_DIR/tools/research.py" "$INSTALL_DIR/tools/"
    cp "$SOURCE_DIR/chat/history.py" "$INSTALL_DIR/chat/"
    cp "$SOURCE_DIR/chat/messaging.py" "$INSTALL_DIR/chat/"
    cp "$SOURCE_DIR/utils/commands.py" "$INSTALL_DIR/utils/"
    cp "$SOURCE_DIR/utils/spinners.py" "$INSTALL_DIR/utils/"
    
    echo "Creating launcher script..."
    cat > "$INSTALL_DIR/launch.sh" <<EOL
#!/bin/bash
source "$VENV_DIR/bin/activate"
cd "$INSTALL_DIR"
python main.py
EOL
    chmod +x "$INSTALL_DIR/launch.sh"
    
    if [ "$create_terminal_command" = true ]; then
        echo "Creating terminal command..."
        
        cat > "/tmp/$APP_NAME" <<EOL
#!/bin/bash
"$INSTALL_DIR/launch.sh"
EOL
        
        sudo mv "/tmp/$APP_NAME" "$BIN_PATH"
        sudo chmod +x "$BIN_PATH"
        echo -e "${GREEN}Terminal command '$APP_NAME' created.${NC}"
        echo "You can now run the app by typing '$APP_NAME' in your terminal."
    else
        echo -e "${YELLOW}No terminal command was created.${NC}"
        echo "To run the app, use: $INSTALL_DIR/launch.sh"
    fi
    
    echo ""
    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo "You can run the application with: $INSTALL_DIR/launch.sh"
    if [ "$create_terminal_command" = true ]; then
        echo "Or simply type: $APP_NAME"
    fi
    
    echo ""
    read -p "Press Enter to return to the main menu..."
    show_main_menu
}

uninstall_app() {
    print_header
    echo -e "${YELLOW}Uninstalling $APP_NAME...${NC}"
    
    if [ ! -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Application is not installed in $INSTALL_DIR.${NC}"
        
        if [ -f "$BIN_PATH" ]; then
            echo "However, the terminal command exists."
            read -p "Do you want to remove the terminal command? (requires sudo) [y/N] " choice
            case "$choice" in
                y|Y ) 
                    sudo rm -f "$BIN_PATH"
                    echo -e "${GREEN}Terminal command removed.${NC}"
                    ;;
                * ) 
                    echo "Terminal command not removed."
                    ;;
            esac
        else
            echo "Nothing to uninstall."
        fi
        
        read -p "Press Enter to return to the main menu..."
        show_main_menu
        return
    fi
    
    echo -e "${RED}Warning: This will remove all application data.${NC}"
    read -p "Are you sure you want to uninstall $APP_NAME? [y/N] " choice
    case "$choice" in
        y|Y ) 
            rm -rf "$INSTALL_DIR"
            echo -e "${GREEN}Application directory removed.${NC}"
            
            if [ -f "$BIN_PATH" ]; then
                read -p "Do you want to remove the terminal command? (requires sudo) [y/N] " choice
                case "$choice" in
                    y|Y ) 
                        sudo rm -f "$BIN_PATH"
                        echo -e "${GREEN}Terminal command removed.${NC}"
                        ;;
                    * ) 
                        echo "Terminal command not removed."
                        ;;
                esac
            fi
            
            echo -e "${GREEN}Uninstallation completed successfully.${NC}"
            ;;
        * ) 
            echo "Uninstallation aborted."
            ;;
    esac
    
    read -p "Press Enter to return to the main menu..."
    show_main_menu
}

remove_installer_files() {
    print_header
    echo -e "${YELLOW}Removing installer files...${NC}"
    
    echo -e "${RED}Warning: This will remove all files in the current directory.${NC}"
    read -p "Are you sure you want to remove all installer files? [y/N] " choice
    case "$choice" in
        y|Y ) 
            current_dir=$(pwd)
            rm -rf "$current_dir"/*
            echo -e "${GREEN}Installer files removed successfully.${NC}"
            ;;
        * ) 
            echo "Operation aborted."
            ;;
    esac
    
    read -p "Press Enter to return to the main menu..."
    show_main_menu
}

show_main_menu() {
    print_header
    echo "Please select an option:"
    echo ""
    echo "1) Install $APP_NAME"
    echo "2) Install $APP_NAME with terminal command (requires sudo)"
    echo "3) Uninstall $APP_NAME"
    echo "4) Remove installer files"
    echo "5) Exit"
    echo ""
    read -p "Enter your choice [1-5]: " choice
    
    case $choice in
        1)
            install_app false
            ;;
        2)
            install_app true
            ;;
        3)
            uninstall_app
            ;;
        4)
            remove_installer_files
            ;;
        5)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            sleep 1
            show_main_menu
            ;;
    esac
}

show_main_menu