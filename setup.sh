action() {
    local shell_is_zsh="$( [ -z "${ZSH_VERSION}" ] && echo "false" || echo "true" )"
    local this_file="$( ${shell_is_zsh} && echo "${(%):-%x}" || echo "${BASH_SOURCE[0]}" )"
    local this_dir="$( cd "$( dirname "${this_file}" )" && pwd )"

    export PYTHONPATH="${this_dir}:${PYTHONPATH}"
    export LAW_HOME="${this_dir}/.law"
    export LAW_CONFIG_FILE="${this_dir}/law.cfg"

    export ROOTS_DIR="${this_dir}/roots"
    export CONFIGURATOR_CACHE_DIR="~/.cmssw-configurator-cache"
    export WORKSPACE_DIR="${this_dir}/release"
    
    source "$( law completion )" ""
    law index --verbose
}
action