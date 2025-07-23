#!/bin/bash
cd /home/ec2-user/oz
docker-compose down -v
docker-compose build
docker-compose up -d
