// Deploy at resource-group scope:
//   az deployment group create -g rg-microworld -f main.bicep -p main.parameters.json
//
// Confirmed empirically against this subscription (an "Azure for Students Starter" /
// DreamSpark grant, not the $100-credit "Azure for Students" offer) on 2026-11-25:
//   - Only Microsoft.Web and Microsoft.Sql are usable among compute/storage-shaped
//     providers. Microsoft.Compute, Microsoft.Storage, Microsoft.Network,
//     Microsoft.App, Microsoft.ContainerInstance/Registry, Microsoft.KeyVault,
//     Microsoft.ManagedIdentity, Microsoft.DocumentDB, Microsoft.OperationalInsights,
//     and Microsoft.Consumption are all DisallowedProvider on this identity — not a
//     quota that can be raised, a policy on the subscription type itself.
//   - App Service is capped at the Free (F1) SKU: attempting Basic (B1) returned
//     "your DreamSpark subscription can only create sites in the 'Free' SKU."
//   - Only `brazilsouth` accepted a deployment among 11 regions tried; everything
//     else (including eastus, westeurope, japaneast) was RequestDisallowedByAzure.
//
// There is therefore no 24/7 compute on Azure here: F1 has no Always On and a small
// daily CPU-minute quota, so it cannot host a continuously-ticking engine. The engine
// lives in free GitHub Actions (scheduled runs against the public repo, unlimited
// minutes) and writes its state to a dedicated git branch read directly by the
// static site. This template's only job is the one thing that genuinely needs a
// live server: a small authenticated endpoint the frontend can POST a scenario
// request to, which then dispatches a GitHub Actions run. See ../README.md.
targetScope = 'resourceGroup'

@description('Must be brazilsouth on this subscription — see the comment above.')
param location string = 'brazilsouth'

@description('Short name used as a prefix for all resources.')
param namePrefix string = 'microworld'

@description('Globally-unique Web App name (becomes <name>.azurewebsites.net).')
param webAppName string = '${namePrefix}-api-${uniqueString(resourceGroup().id)}'

var tags = {
  project: 'master-thesis-microworld'
  managedBy: 'bicep'
}

resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${namePrefix}-plan'
  location: location
  tags: tags
  sku: {
    name: 'F1'
    tier: 'Free'
  }
  kind: 'linux'
  properties: {
    reserved: true // required for Linux plans
  }
}

resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: webAppName
  location: location
  tags: tags
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: false // not available on F1; cold starts after ~20 min idle are expected
      appCommandLine: 'gunicorn --bind=0.0.0.0 --timeout 600 app:app'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

output webAppHostname string = webApp.properties.defaultHostName
output webAppName string = webApp.name
