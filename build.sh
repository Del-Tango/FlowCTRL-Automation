#!/bin/bash -x
#
# Python Build WizZard

declare -a DEPENDENCIES
declare -a BUILD_DIRS

# Cold parameters

SCRIPT_NAME='Build WizZard'
VERSION='SpeedBall'
VERSION_NO='1.0.0'
PACKAGE_NAME='flow_ctrl'
PACKAGE_VERSION='2.0.0'
DEPENDENCIES=( 'python3' 'python3-pip' 'twine' )
REQUIREMENTS_FILE='./requirements.txt'
DISTRIBUTION_DIR='./dist'
TEST_DIR="./${PACKAGE_NAME}/tst"
CONF_DIR="./${PACKAGE_NAME}/conf"
UNIT_TEST_DIR="${TEST_DIR}/unit"
INT_TEST_DIR="${TEST_DIR}/integration"
VENV_DIR=".venv"
TEMP_FILE='.bw_out.temp'
PYLINT_CONF_FILE="${CONF_DIR}/setup.pylint.conf"
FLAKE8_CONF_FILE="${CONF_DIR}/setup.flake8.conf"
MYPY_CONF_FILE="${CONF_DIR}/setup.mypy.conf"
PARENT_DIR=$(basename $(dirname `realpath ./module.py`))
BUILD_DIRS=(
    '_build/' "${DISTRIBUTION_DIR}" "${PACKAGE_NAME}.egg-info/"
)

# Hot parameters

MODE='BUILD' # (SETUP | TEST | CHECK | BUILD)
BUILD='on'
INSTALL='off'
PUBLISH='off'
YES='off'


function display_usage() {
    cat <<EOF
  _____________________________________________________________________________

    *                        *  ${SCRIPT_NAME}  *                           *
  ___________________________________________________v${VERSION_NO}${VERSION}_____________

    [ Usage ]: ~$ $0 (BUILD | INSTALL | PUBLISH)

        -h | --help                 Display this message.

        -S | --setup                Install build dependencies.

        -T | --test                 Run autotesters.

        -c | --check                Check module type hints used properly.

        -C | --cleanup              Cleanup project directory. Removes directories
           |                        created during the build process, removes
           |                        compiled python __pycache__'s, the mypy cahe
           |                        and overwrites all log files with a timestamp.

    [ Example ]: Install dependencies -

        ~$ sudo $0 --setup

    [ Example ]: Run autotesters and check type hints in source files -

        ~$ $0 --test --check --cleanup

    [ Example ]: Build the source and binary distributions -

        ~$ $0
        ~$ $0 BUILD

        [ NOTE ]: Build is set as the default, so it doesn't need to be
            specified unless this build wizzard script is modified.

    [ Example ]: Build distributions and install source -
        ~$ $0 INSTALL

    [ Example ]: Time saver -
        ~$ $0 --test --check BUILD INSTALL && $0 --cleanup -y
EOF
}

# ACTIONS

function test_module() {
    echo "[ TEST ]: Running Python3 Unit Tests..."
    echo "[ WARNING ]: (~$ ./build.sh BUILD INSTALL) required before running this action!"
    if [ -d "${VENV_DIR}" ]; then
        local CMD="${VENV_DIR}/bin/python3"
    else
        local CMD="python3"
    fi

    if ! ${CMD} -m unittest discover -s "${UNIT_TEST_DIR}" -p "test_*.py"; then
        if ! ${CMD} -m pytest ${UNIT_TEST_DIR} -v; then
            echo "[ NOK ]: Python3 Unit tests failed!"
        fi
    else
        echo "[ OK ]: Python3 Unit tests passed!"
    fi

    if ! ${CMD} -m pytest ${INT_TEST_DIR} -v; then
        echo "[ NOK ]: Python3 Integration tests failed!"
    else
        echo "[ OK ]: Python3 Integration tests passed!"
    fi
    return $EXIT_CODE
}

function setup_module() {
    local FAILURES=0
    echo "[ SETUP ]: System dependencies..."
    for package in ${DEPENDENCIES[@]}; do
        apt-get install "${package}" -y
        if [ $? -ne 0 ]; then
            local FAILURES=$((FAILURES + 1))
        fi
    done
    if [ ! -d "${VENV_DIR}" ]; then
        if ! python3 -m venv ${VENV_DIR}; then
            local FAILURES=$((FAILURES + 1))
            echo "[ WARNING ]: Could not create Python3 Virtual Environment in "\
                "(${VENV_DIR})!"
        fi
    fi
    echo "[ ... ]: Python requirements"
    if [ -d "${VENV_DIR}" ]; then
        ${VENV_DIR}/bin/pip3 install -r "${REQUIREMENTS_FILE}"
    else
        pip3 install -r "${REQUIREMENTS_FILE}"
    fi
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    return $FAILURES
}

function build() {
    echo "[ BUILD ]: Source and binary distributions..."
    local FAILURES=0
    if [ -d "${VENV_DIR}" ]; then
        ${VENV_DIR}/bin/python3 setup.py sdist bdist_wheel
    else
        python3 setup.py sdist bdist_wheel
    fi
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    return $FAILURES
}

function cleanup() {
    echo "[ CLEANING ]: Project directory for Ricks..."
    local FAILURES=0
    echo "[ ... ]: Compiled Python __pycache__ directories"
    rm -rf `find . -type d -name '__pycache__'`
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: Python build directories"
    rm -rf ${BUILD_DIRS[@]} ${DOCKER_BUILD_DIR}
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: MyPy cache directory"
    rm -rf '.mypy_cache'
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: Project log files"
    date | tee `find . -type f -name '*.log'`
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: Python package"
    if [ -d "${VENV_DIR}" ]; then
        local CMD="${VENV_DIR}/bin/python3"
    else
        local CMD="python3"
    fi
    if [[ "${YES}" == 'on' ]]; then
        ${CMD} -m pip uninstall "${PACKAGE_NAME}" -y
    else
        ${CMD} -m pip uninstall "${PACKAGE_NAME}"
    fi
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: Removing temporary files"
    rm $TEMP_FILE &> /dev/null
    return $FAILURES
}

function check_source_code() {
    echo "[ CHECKING ]: Rick's Python3 source code..."
    local FAILURES=0
    echo "[ ... ]: Running mypy..."
    mypy --disallow-untyped-defs --config-file ${MYPY_CONF_FILE} *.py
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: Running flake8..."
    flake8 --config ${FLAKE8_CONF_FILE} .
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: Running pylint..."
    pylint --rcfile=${PYLINT_CONF_FILE} ${PARENT_DIR}
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    return $FAILURES
}

function install() {
    echo "[ INSTALL ]: Source distribution archive..."
    local ARCHIVE_PATH=`find ./dist -type f -name '*.tar.gz'`
    if [ -d "${VENV_DIR}" ]; then
        ${VENV_DIR}/bin/pip3 install "${ARCHIVE_PATH}"
    else
        pip3 install "${ARCHIVE_PATH}"
    fi
    return $?
}

function publish() {
    echo "[ PUBLISH ]: To pypi..."
    echo "[ WARNING ]: Publishing currently disabled for this project."
#   # Env vars for twine to publish packages
#   export TWINE_USERNAME=
#   export TWINE_PASSWORD=
#   export TWINE_REPOSITORY_URL=
#   twine upload "${DISTRIBUTION_DIR}/*" --verbose
    return $?
}

# INIT

function init_build_wizzard() {
    local EXIT_CODE=0
    if [[ "$BUILD" == 'on' ]]; then
        build
        EXIT_CODE=$((EXIT_CODE + $?))
    fi

    if [[ "$INSTALL" == 'on' ]]; then
        install
        EXIT_CODE=$((EXIT_CODE + $?))
    fi

    if [[ "$PUBLISH" == 'on' ]]; then
        publish
        EXIT_CODE=$((EXIT_CODE + $?))
    fi
    return $EXIT_CODE
}

# MISCELLANEOUS

EXIT_CODE=0

for opt in ${@}; do
    case "$opt" in
        -y|--yes)
            YES='on'
            ;;
    esac
done

for opt in ${@}; do
    case "$opt" in
        -h|--help)
            display_usage
            exit 0
            ;;
        -S|--setup)
            MODE='SETUP'
            setup_module
            EXIT_CODE=$((EXIT_CODE + $?))
            ;;
        -T|--test)
            MODE='TEST'
            test_module
            EXIT_CODE=$((EXIT_CODE + $?))
            ;;
        -c|--check)
            MODE='CHECK'
            check_source_code
            EXIT_CODE=$((EXIT_CODE + $?))
            ;;
        -C|--cleanup)
            MODE='CLEANUP'
            cleanup
            EXIT_CODE=$((EXIT_CODE + $?))
            ;;
        build|Build|BUILD)
            MODE='BUILD'
            BUILD='on'
            ;;
        install|Install|INSTALL)
            MODE='BUILD'
            INSTALL='on'
            ;;
        publish|Publish|PUBLISH)
            MODE='BUILD'
            PUBLISH='on'
            ;;
    esac
done

if [[ "${MODE}" == 'BUILD' ]]; then
    init_build_wizzard
    EXIT_CODE=$?
fi

exit $EXIT_CODE

# CODE DUMP

# declare -a DOCKER_CONTEXT_FILES

# DOCKER_IMG_REPO='public.ecr.aws/g6x6g6f5'
##MODULE_CONF_FILE='conf/module.conf.json'


#   DOCKER_BUILD_DIR='./docker_build/'
#   DOCKER_APP_DIR='/app'
#   DOCKER_MAINTAINER_NAME='WanoLabs'
#   DOCKER_MAINTAINER_EMAIL='alvearesolutions@gmail.com'
#   DOCKER_IMAGE_VERSION='1.0'
#   DOCKER_IMAGE_DESCRIPTION='This is a Kaya module Docker image.'
#   DOCKER_CONTEXT_FILES=(
#       "${REQUIREMENTS_FILE}"
#       "${MODULE_CONF_FILE}"
#   )
#   DOCKER_CONTEXT_FILES_OPTIONAL=(
#       "${DISTRIBUTION_DIR}/${PACKAGE_NAME}-${PACKAGE_VERSION}.tar.gz"
#   )
#   REPOSITORY_DOMAIN='kaya'
#   PY_REPO='kaya-modules-py'

#   DOCKER_IMAGE="${PACKAGE_NAME}"
#   DOCKER_CONTAINER='kaya_base_integration_tests'
#   DOCKERFILE="Dockerfile"

#       -d=*|--docker-container=*)
#           DOCKER_CONTAINER="${opt#*=}"
#           ;;
#       -D=*|--docker-image=*)
#           DOCKER_IMAGE="${opt#*=}"
#           ;;
#       -F=*|--docker-file=*)
#           DOCKERFILE="${opt#*=}"
#           ;;
#
#       ${VENV_DIR}/bin/python3 -m build --sdist --no-isolation

#       python3 -m build --sdist --no-isolation
#
#       -d=| --docker-container=ID  Implies --test. Specify running Docker container
#          |                        to run integration tests in.

#       -D=| --docker-image=ID      Specify name of Docker image.

#       -F=| --docker-file=PATH     Specify path to Docker image Dockerfile.

#   [ Example ]: Specify integration test environment -

#       ~$ $0 --test --docker-container='test_cont' --docker-image='test_img' \\
#           --docker-file='./Dockerfile'
#
#   [ Example ]: Build distribuition and publish to PyPI -
#       ~$ $0 PUBLISH

#   [ Example ]: Build, install and publish to PyPI -
#       ~$ $0 INSTALL PUBLISH


