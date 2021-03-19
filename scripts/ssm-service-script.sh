# This script gets called by the systemd script
# It's starts the AWS Systems Manager Agent in the background
# This command got initially used by Linux services.
# This script allows to run it from a systemd launch configuration
amazon-ssm-agent start ${0} &
exit 0
