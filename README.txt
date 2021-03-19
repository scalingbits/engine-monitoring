The scripts used in this project have been derived from the AWS IOT-Sitewise
tutorial (https://docs.aws.amazon.com/iot-sitewise/latest/userguide/ingest-data-from-iot-things.html)
Consult this tutorial to make things work.
The email and SMS integration have been derived from the AWS IOT-Lambfa tutorial
(https://docs.aws.amazon.com/iot/latest/developerguide/iot-lambda-rule.html)

Prerequisites
--------------

1. Create your own AWS IOT "Thing"
   You will get a
    * Name for your thing
    * Public and private certificates for your thing
    * An access point
2. Customize the launch script stirlingdevice_performance.sh
   * The script is supposed to be used out of /usr/local/sitewise
   * Consider to create a subdirectory in /usr/local/sitewise for your thing.
      It allows you to store the credentials
   * Update the parameter for thing name, certificates and access point in the
      launch script
   * This script can be started as root user. It'll create a log on standard out
3. Creating a systemd service
   * The script InstallStirlingSitewiseService.sh has to be run as a user who can become super user
   * It'll create a systemd service file
   * It will then start the service and the service will be started at a reboot
   * The script is idempotent. It can be run multiple times.
        It's stop the service. It'll overwrite the service file. It'll restart the service.
4. Deinstalling the service (only)
   Perform the following commands as super user
   * systemctl stop aws-sitewise.service
   * systemctl disable aws-sitewise.service
   * systemctl daemon-reload
   * rm /etc/systemd/system/aws-sitewise.service
   The commands below will not delete the launch script in /user/local/sitewise
