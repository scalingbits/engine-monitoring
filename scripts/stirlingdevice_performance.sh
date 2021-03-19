# This script gets called by the systemd script
# It's starts the monitoring in the background
# The access point and the certificates are specific for this demonstration
# replace them as needed
python3 stirlingdevice_performance.py \
  --thingName StirlingDevice2 \
  --endpoint aedulr5ft9wm8-ats.iot.eu-central-1.amazonaws.com \
  --rootCA AmazonRootCA1.pem \
  --cert StirlingDevice2/7f888589a4-certificate.pem.crt \
  --key StirlingDevice2/7f888589a4-private.pem.key  &
exit 0
