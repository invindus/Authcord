#!/usr/bin/env bash

function rprintf () {
	printf "[CFG] $1" "${@:2}" 
}

function rnprintf () {
	rprintf "$@"
	printf "\n"
}

nl=$'\n'
function help_proc () {
	cat <<-END
		-p <PORT:int>      port for backend (8000)$nl
		-n <HOSTNAME:str>  hostname for backend (localhost)$nl
		-d                 run frontend dev server rather than django$nl
	END
	exit 0
}

SRV_PORT=8000
HNM=localhost

export FE_DEV_SERVER=false


while getopts 'p:hn:d' opt; do
	case $opt in
		(h) help_proc ;;
		# unimplemented
		(p) SRV_PORT=$OPTARG;;
		(n) HNM=$OPTARG;;
		(d) export FE_DEV_SERVER=true;;
	esac
done

PROTO=http:

rnprintf "DEV IS %s" $FE_DEV_SERVER
rnprintf "PORT IS %d" $SRV_PORT
rnprintf "NAME IS %s" $HNM

SRV="$PROTO://$HNM:$SRV_PORT"
rnprintf "SRV IS %s" $SRV

cd $(dirname "$(realpath $0)")
echo $PWD

function npm_proc () {
	cat <<-END
		================================
		FE PROC: INSTALLING NPM PACKAGES
		================================
	END
	npm i || return 1
	cat <<-END
		==============================
		FE PROC: BUILDING THE FRONTEND
		==============================
	END
	npm run build || return 1
	cat <<-END
		===========================
		FE PROC: BUILDING SUCCEEDED
		===========================
	END
	return 0
}

function serve_proc () {
	cat <<-END
		================================================
		BE PROC: INITIALIZING PYTHON BACKEND ENVIRONMENT
		================================================
	END
	virtualenv .venv
	cat <<-END
		=====================================
		BE PROC: ENTERING VIRTUAL ENVIRONMENT
		=====================================
	END
	source .venv/bin/activate || return 1
	pip install -r requirements.txt || return 1
	cat <<-END
		=======================
		BE PROC: RUNNING SERVER
		=======================
	END
	python manage.py runserver || return 1
	cat <<-END
		=================================
		BE PROC: SERVER EXITED GRACEFULLY
		=================================
	END
	return 0
}

npm_proc && serve_proc

