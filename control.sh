#!/bin/bash

# ==========================================
# Odoo Development Environment Control Script
# ==========================================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}Error: .env file not found. Please copy .env.example to .env and configure it.${NC}"
    exit 1
fi

# Determine docker compose command
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}Error: docker compose or docker-compose not found.${NC}"
    exit 1
fi

# Variables
COMPOSE_FILE="docker-compose.yml"
WEB_CONTAINER="vitalcare-web-1" # Adjust if compose project name changes, or use dynamic lookup
DB_CONTAINER="vitalcare-db-1"

# Function to get container name dynamically
get_container_name() {
    local service=$1
    $DOCKER_COMPOSE ps -q $service | xargs docker inspect --format '{{.Name}}' | sed 's/\///'
}

# --- Functions ---

function show_header() {
    clear
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}   Odoo Dev Environment - Control Panel   ${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo -e "Project: ${GREEN}${PROJECT_NAME:-Odoo}${NC}"
    echo -e "Odoo Version: ${YELLOW}${ODOO_VERSION:-18.0}${NC}"
    echo -e "Web Port: ${YELLOW}${WEB_PORT:-8069}${NC}"
    echo -e "${BLUE}==========================================${NC}"
}

function start_env() {
    echo -e "${GREEN}Starting environment...${NC}"
    $DOCKER_COMPOSE up -d
    echo -e "${GREEN}Environment started!${NC}"
}

function stop_env() {
    echo -e "${YELLOW}Stopping environment...${NC}"
    $DOCKER_COMPOSE stop
    echo -e "${GREEN}Environment stopped.${NC}"
}

function restart_web() {
    echo -e "${YELLOW}Restarting Odoo Web container...${NC}"
    $DOCKER_COMPOSE restart web
    echo -e "${GREEN}Odoo Web restarted.${NC}"
}

function view_logs() {
    echo -e "${BLUE}Select logs to view:${NC}"
    echo "1) Web (Odoo)"
    echo "2) Database (Postgres)"
    echo "3) Both"
    read -p "Option: " log_opt
    case $log_opt in
        1) tail -f logs/odoo.log ;;
        2) tail -f logs/postgresql.log ;;
        3) tail -f logs/odoo.log logs/postgresql.log ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
}

function shell_access() {
    echo -e "${BLUE}Entering Odoo Shell...${NC}"
    $DOCKER_COMPOSE exec web /bin/bash
}

function reset_db() {
    echo -e "${RED}WARNING: This will DELETE the database and all data!${NC}"
    read -p "Are you sure? (y/N): " confirm
    if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
        echo -e "${YELLOW}Stopping containers...${NC}"
        $DOCKER_COMPOSE down -v
        echo -e "${GREEN}Database and volumes removed.${NC}"
        echo -e "${GREEN}Starting fresh environment...${NC}"
        $DOCKER_COMPOSE up -d
        echo -e "${GREEN}Done!${NC}"
    else
        echo -e "${BLUE}Operation cancelled.${NC}"
    fi
}

function run_tests() {
    read -p "Enter module name to test (or 'all'): " module_name
    if [ "$module_name" == "all" ]; then
        echo -e "${YELLOW}Running all tests... (This might take a while)${NC}"
        $DOCKER_COMPOSE exec web odoo --test-enable --stop-after-init -d ${DB_NAME}
    else
        echo -e "${YELLOW}Running tests for module: $module_name${NC}"
        $DOCKER_COMPOSE exec web odoo --test-enable --stop-after-init -d ${DB_NAME} -i $module_name
    fi
}

function update_module() {
    read -p "Enter module name to update: " module_name
    echo -e "${YELLOW}Updating module: $module_name${NC}"
    $DOCKER_COMPOSE exec web odoo -u $module_name -d ${DB_NAME} --stop-after-init
    echo -e "${GREEN}Update complete. Restarting web service to apply changes if needed...${NC}"
    $DOCKER_COMPOSE restart web
}

function show_status() {
    $DOCKER_COMPOSE ps
}

function show_menu() {
    show_header
    echo "1) Start Environment"
    echo "2) Stop Environment"
    echo "3) Restart Odoo Web"
    echo "4) View Logs"
    echo "5) Shell Access (Odoo Container)"
    echo "6) Update Module (-u)"
    echo "7) Run Tests"
    echo "8) Reset Database (Clean Start)"
    echo "9) Show Status"
    echo "0) Exit"
    echo -e "${BLUE}------------------------------------------${NC}"
    read -p "Select an option: " option

    case $option in
        1) start_env ;;
        2) stop_env ;;
        3) restart_web ;;
        4) view_logs ;;
        5) shell_access ;;
        6) update_module ;;
        7) run_tests ;;
        8) reset_db ;;
        9) show_status; read -p "Press Enter to continue..." ;;
        0) exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}"; sleep 1 ;;
    esac
    
    echo
    read -p "Press Enter to return to menu..."
    show_menu
}

# Check for arguments (CLI mode)
if [ $# -gt 0 ]; then
    case "$1" in
        start) start_env ;;
        stop) stop_env ;;
        restart) restart_web ;;
        logs) view_logs ;; # This might need non-interactive tweak if called directly
        shell) shell_access ;;
        status) show_status ;;
        help) 
            echo "Usage: $0 [start|stop|restart|logs|shell|status]"
            ;;
        *) echo "Unknown command: $1"; exit 1 ;;
    esac
else
    # Interactive mode
    show_menu
fi
