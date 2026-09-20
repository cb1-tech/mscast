#!/usr/bin/env bash
echo "DOCKER_HOST=${DOCKER_HOST:-unset}"
echo "socket candidates:"
ls -l /var/run/docker.sock 2>/dev/null
ls -l /run/user/1000/docker.sock 2>/dev/null
echo "--- dockerd processes ---"
ps -eo pid,user,args | grep -E 'dockerd|rootlesskit|containerd' | grep -v grep | head -10
echo "--- linger ---"
loginctl show-user sanjay 2>/dev/null | grep -i linger
echo "--- systemd docker service ---"
systemctl is-active docker 2>/dev/null
systemctl --user is-active docker 2>/dev/null
echo "--- containers ---"
docker ps -a --format '{{.Names}} | {{.Status}}'
