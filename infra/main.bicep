targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Location for the OpenAI resource')
// https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure?tabs=global-standard-aoai%2Cglobal-standard&pivots=azure-openai#models-by-deployment-type
@allowed([
  'australiaeast'
  'brazilsouth'
  'canadaeast'
  'eastus'
  'eastus2'
  'francecentral'
  'germanywestcentral'
  'japaneast'
  'koreacentral'
  'northcentralus'
  'norwayeast'
  'polandcentral'
  'southafricanorth'
  'southcentralus'
  'southindia'
  'spaincentral'
  'swedencentral'
  'switzerlandnorth'
  'uaenorth'
  'uksouth'
  'westeurope'
  'westus'
  'westus3'
])
@metadata({
  azd: {
    type: 'location'
  }
})
param location string

@description('Name of the GPT model to deploy')
param gptModelName string = 'gpt-5.4'

@description('Version of the GPT model to deploy')
// See version availability in this table:
// https://learn.microsoft.com/azure/ai-services/openai/concepts/models?tabs=python-secure%2Cglobal-standard%2Cstandard-chat-completions#models-by-deployment-type
param gptModelVersion string = '2026-03-05'

@description('Name of the model deployment (can be different from the model name)')
param gptDeploymentName string = 'gpt-5.4'

@description('Capacity of the GPT deployment')
// You can increase this, but capacity is limited per model/region, so you will get errors if you go over
// https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits
param gptDeploymentCapacity int = 200


@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Non-empty if the deployment is running on GitHub Actions')
param runningOnGitHub string = ''

var principalType = empty(runningOnGitHub) ? 'User' : 'ServicePrincipal'

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var prefix = '${environmentName}${resourceToken}'
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
    name: '${prefix}-rg'
    location: location
    tags: tags
}

var openAiServiceName = '${prefix}-openai'
module openAi 'br/public:avm/res/cognitive-services/account:0.7.1' = {
  name: 'openai'
  scope: resourceGroup
  params: {
    name: openAiServiceName
    location: location
    tags: tags
    kind: 'OpenAI'
    sku: 'S0'
    customSubDomainName: openAiServiceName
    disableLocalAuth: true
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
    deployments: [
      {
        name: gptDeploymentName
        model: {
          format: 'OpenAI'
          name: gptModelName
          version: gptModelVersion
        }
        sku: {
          name: 'GlobalStandard'
          capacity: gptDeploymentCapacity
        }
      }
    ]
    roleAssignments: [
      {
        principalId: principalId
        roleDefinitionIdOrName: 'Cognitive Services OpenAI User'
        principalType: principalType
      }
    ]
  }
}

var logAnalyticsWorkspaceName = '${prefix}-logs'
module logAnalyticsWorkspace 'br/public:avm/res/operational-insights/workspace:0.9.1' = {
  name: 'logAnalyticsWorkspace'
  scope: resourceGroup
  params: {
    name: logAnalyticsWorkspaceName
    location: location
    tags: tags
  }
}

var applicationInsightsName = '${prefix}-appinsights'
module applicationInsights 'br/public:avm/res/insights/component:0.8.0' = {
  name: 'applicationInsights'
  scope: resourceGroup
  params: {
    name: applicationInsightsName
    location: location
    tags: tags
    workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

// Specific to Azure OpenAI
output AZURE_OPENAI_ENDPOINT string = openAi.outputs.endpoint
output AZURE_OPENAI_CHAT_MODEL string = gptModelName
output AZURE_OPENAI_CHAT_DEPLOYMENT string = gptDeploymentName

output APPLICATIONINSIGHTS_CONNECTION_STRING string = applicationInsights.outputs.connectionString
