// Resource-group-scoped optional dispatcher and bounded ABM execution API.
// The deterministic browser playground and GitHub snapshot feed do not depend on it.
targetScope = 'resourceGroup'

@description('Deployment region. Confirm current subscription quota before deployment.')
param location string = 'brazilsouth'

@description('Short prefix used for the API resources.')
param namePrefix string = 'microworld'

@description('Globally unique Linux Web App name.')
param webAppName string = '${namePrefix}-api-${uniqueString(resourceGroup().id)}'

@description('Allowed browser origin; configure this to the GitHub Pages origin.')
param allowedOrigin string = 'https://edwardcalderon.github.io'

@description('Repository identity used by the legacy workflow-dispatch endpoint.')
param githubRepo string = 'edwardcalderon/Master-s-thesis'

@description('Create a separately billed, private Blob Storage account for empirical captures. Defaults off.')
param createHistoricalDataStorage bool = false

@description('Globally unique lowercase Azure Storage account name; used only when storage creation is enabled.')
param historicalDataStorageName string = 'mwdata${uniqueString(resourceGroup().id)}'

@description('Private container for bounded CEX/DEX raw captures and processed partitions.')
param historicalDataContainer string = 'empirical-market'

var tags = {
  project: 'master-thesis-microworld'
  managedBy: 'bicep'
  role: 'optional-experiment-api'
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
    reserved: true
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
      alwaysOn: false
      appCommandLine: 'gunicorn --bind=0.0.0.0:8000 --timeout 60 app:app'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ALLOWED_ORIGIN'
          value: allowedOrigin
        }
        {
          name: 'GITHUB_REPO'
          value: githubRepo
        }
        {
          name: 'EXPERIMENT_COOLDOWN_SECONDS'
          value: '600'
        }
      ]
    }
  }
}

resource historicalDataStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = if (createHistoricalDataStorage) {
  name: historicalDataStorageName
  location: location
  tags: {
    project: 'master-thesis-microworld'
    managedBy: 'bicep'
    role: 'private-empirical-data-lake'
  }
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Enabled'
    supportsHttpsTrafficOnly: true
  }
}

resource historicalDataBlobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = if (createHistoricalDataStorage) {
  parent: historicalDataStorage
  name: 'default'
  properties: {
    isVersioningEnabled: true
    deleteRetentionPolicy: {
      enabled: true
      days: 14
    }
  }
}

resource historicalDataContainerResource 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = if (createHistoricalDataStorage) {
  parent: historicalDataBlobService
  name: historicalDataContainer
  properties: {
    publicAccess: 'None'
  }
}

resource historicalDataLifecycle 'Microsoft.Storage/storageAccounts/managementPolicies@2022-05-01' = if (createHistoricalDataStorage) {
  parent: historicalDataStorage
  name: 'default'
  properties: {
    policy: {
      rules: [
        {
          enabled: true
          name: 'cool-empirical-runs-after-90-days'
          type: 'Lifecycle'
          definition: {
            filters: {
              blobTypes: [
                'blockBlob'
              ]
              prefixMatch: [
                '${historicalDataContainer}/'
              ]
            }
            actions: {
              baseBlob: {
                tierToCool: {
                  daysAfterModificationGreaterThan: 90
                }
              }
            }
          }
        }
      ]
    }
  }
}

output webAppHostname string = webApp.properties.defaultHostName
output webAppName string = webApp.name
output historicalDataStorageAccountName string = createHistoricalDataStorage ? historicalDataStorageName : ''
output historicalDataContainerName string = createHistoricalDataStorage ? historicalDataContainer : ''
