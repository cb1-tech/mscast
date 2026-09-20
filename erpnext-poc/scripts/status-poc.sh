#!/usr/bin/env bash
docker ps -a --filter name=mscast-poc --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "---"
free -h | head -2
echo "---"
curl -s -o /dev/null -w 'site http:%{http_code}\n' http://localhost:8080/api/method/ping
