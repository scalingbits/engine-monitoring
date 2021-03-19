#!/usr/bin/env bash
# version 1.1
# March, 2021
SERVICEFILE="/etc/systemd/system/aws-sitewise.service"
if [[ -e ${SERVICEFILE} ]];then
   echo "AWS Sitewise Service is already installed as SYSTEMD, trying to stop
the service."
   echo "*****";
   systemctl stop aws-sitewise.service
   rm ${SERVICEFILE}
fi
echo "[Unit]" >  ${SERVICEFILE};
echo "Description=AWS Sitewise Service" >>  ${SERVICEFILE};
echo "After=syslog.target network.target" >>  ${SERVICEFILE};
echo " " >>  ${SERVICEFILE};
echo "[Service]" >>  ${SERVICEFILE};
echo "Type=forking" >>  ${SERVICEFILE};
echo "User=root" >>  ${SERVICEFILE};
echo "WorkingDirectory=/usr/local/sitewise" >>  ${SERVICEFILE};
echo "ExecStart=/bin/bash ./stirlingdevice_performance.sh" >>  ${SERVICEFILE};
echo "Restart=always" >>  ${SERVICEFILE};
echo "RestartSec=60" >>  ${SERVICEFILE};
echo " " >>  ${SERVICEFILE};
echo "[Install]" >>  ${SERVICEFILE};
echo "WantedBy=multi-user.target" >>  ${SERVICEFILE};
systemctl daemon-reload
systemctl enable aws-sitewise.service
systemctl start aws-sitewise.service
echo "Done installing prerequisites (SYSTEMD)"
