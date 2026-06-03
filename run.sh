#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Visual colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Hardcode the DevPod workspace ID so we can reliably target it
WORKSPACE_NAME="ballotvision-dev"

show_help() {
    echo "BallotVision Development Control Script (DevPod Edition)"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  test      Run the test suite via pytest"
    echo "  lint      Check code style with black and flake8"
    echo "  docs      Generate Doxygen documentation"
    echo "  shell     Open an interactive bash shell inside the container"
    echo "  help      Show this help message"
}

# -------------------------------------------------------------------------
# 1. ENVIRONMENT ROUTING
# Check if we are running on the host machine (outside the container)
# -------------------------------------------------------------------------
if [ ! -f "/.dockerenv" ] && [ -z "$DEVPOD" ]; then
    echo -e "${YELLOW}Host environment detected. Routing task to DevPod...${NC}"
    
    # Verify the DevPod CLI is installed on the host
    if ! command -v devpod &> /dev/null; then
        echo "Error: The 'devpod' CLI is not installed or not in your PATH."
        exit 1
    fi

    # Default to help if no argument is provided
    CMD_ARG="${1:-help}"

    echo -e "${BLUE}Starting DevPod workspace (this will build the image if needed)...${NC}"
    devpod up . --id $WORKSPACE_NAME --ide none

    if [ "$CMD_ARG" == "shell" ]; then
        echo -e "${BLUE}Entering container shell...${NC}"
        devpod ssh $WORKSPACE_NAME
        exit 0
    fi

    echo -e "${BLUE}Executing command inside the container...${NC}"
    # By passing $CMD_ARG directly inside the double quotes, the host expands it 
    # explicitly (e.g., into ./run.sh test) before sending it over SSH.
    devpod ssh $WORKSPACE_NAME --command "
        if [ -f /workspace/run.sh ]; then
            cd /workspace
        elif [ -f /workspaces/BallotVision/run.sh ]; then
            cd /workspaces/BallotVision
        else
            TARGET_DIR=\$(find /workspace /workspaces -name run.sh -print -quit 2>/dev/null | xargs dirname)
            if [ -n \"\$TARGET_DIR\" ]; then
                cd \"\$TARGET_DIR\"
            else
                echo 'Error: Could not locate run.sh inside the container mount points.'
                exit 1
            fi
        fi
        ./run.sh $CMD_ARG
    "
    
    exit $?
fi

# -------------------------------------------------------------------------
# 2. CONTAINER EXECUTION
# If we reach this point, we are safely INSIDE the container.
# -------------------------------------------------------------------------
case "$1" in
    test)
        echo -e "${BLUE}Running tests with pytest...${NC}"
        pytest -v --cov=src/ballot_vision
        ;;
    lint)
        echo -e "${BLUE}Checking code formatting (Black)...${NC}"
        black --check src/ tests/
        echo -e "${BLUE}Linting code (Flake8)...${NC}"
        flake8 src/ tests/
        echo -e "${GREEN}All style checks passed!${NC}"
        ;;
    docs)
        echo -e "${BLUE}Generating Doxygen documentation...${NC}"
        if [ ! -d "docs" ]; then mkdir docs; fi
        if [ ! -f "docs/Doxyfile" ]; then 
            cd docs && doxygen -g > /dev/null && cd ..
            echo "Created default docs/Doxyfile. Update it with your configuration."
        fi
        doxygen docs/Doxyfile
        echo -e "${GREEN}Documentation generated successfully in docs/build/html/index.html${NC}"
        ;;
    *)
        show_help
        ;;
esac

