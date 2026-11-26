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

output webAppHostname string = webApp.properties.defaultHostName
output webAppName string = webApp.name
