#!/bin/bash

scriptPath=$(dirname "$0")

test -f secrets.sh || {
    echo -e "💥 Error! secrets.sh not found, please create"
    exit 1
}
test -f deploy-vars.sh || {
    echo -e "💥 Error! deploy-vars.sh not found, please create"
    exit 1
}

source $scriptPath/secrets.sh
source $scriptPath/deploy-vars.sh

for varName in USE_KEYVAULT_CERT ISTIO_GW_CRT ISTIO_GW_KEY; do
    varVal=$(eval echo "\${$varName}")
    [[ -z $varVal ]] && {
        echo "💥 Error! Required variable '$varName' is not set!"
        varUnset=true
    }
done

if [[ $USE_KEYVAULT_CERT ]]; then
    ISTIO_GW_CRT=$(az keyvault secret show --id $ISTIO_GW_CRT --query 'value' -o tsv)
    ISTIO_GW_KEY=$(az keyvault secret show --id $ISTIO_GW_KEY --query 'value' -o tsv)
fi

envsubst <$scriptPath/istio-gw-cert.enc.yaml.template >$scriptPath/../base/istio-gw-cert.enc.yaml
sops --encrypt --in-place $scriptPath/../base/istio-gw-cert.enc.yaml
git add $scriptPath/../base/istio-gw-cert.enc.yaml
git commit -m "Updated cert by script $(date)"
git push
