# Test Kalshi API connectivity with retry logic
$apiKey = "14a525cf-42d7-4746-8e36-30a8d9c17c96"
$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Content-Type" = "application/json"
}

# Try multiple endpoints
$endpoints = @(
    "https://api.kalshi.com/trade-api/v2/markets",
    "https://api.kalshi.com/v1/markets",
    "https://kalshi.com/api/v1/markets",
    "https://trade-api.kalshi.com/v1/markets"
)

function Test-Endpoint {
    param($url)
    
    Write-Host "Testing: $url"
    
    $maxRetries = 3
    $retryCount = 0
    $backoffFactor = 2
    $baseDelay = 1000 # 1 second
    
    while ($retryCount -lt $maxRetries) {
        try {
            $response = Invoke-RestMethod -Uri $url -Method GET -Headers $headers -TimeoutSec 5
            Write-Host "SUCCESS: Endpoint $url responded" -ForegroundColor Green
            Write-Host "Response: $($response | ConvertTo-Json -Depth 1)"
            return $true
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-Host "Attempt $($retryCount + 1) failed: $errorMsg" -ForegroundColor Yellow
            
            if ($retryCount -eq $maxRetries - 1) {
                Write-Host "All attempts failed for $url" -ForegroundColor Red
                return $false
            }
            
            $delay = $baseDelay * [Math]::Pow($backoffFactor, $retryCount)
            Write-Host "Waiting $($delay)ms before retry..."
            Start-Sleep -Milliseconds $delay
            $retryCount++
        }
    }
    
    return $false
}

# Test all endpoints
Write-Host "=== Testing Kalshi API Endpoints ==="
foreach ($endpoint in $endpoints) {
    Test-Endpoint -url $endpoint
    Write-Host "`n"
}

# Also test DNS resolution
Write-Host "=== Testing DNS Resolution ==="
$domains = @("api.kalshi.com", "kalshi.com", "trade-api.kalshi.com")
foreach ($domain in $domains) {
    try {
        $result = Resolve-DnsName -Name $domain -ErrorAction Stop
        Write-Host "$domain resolves to: $($result.IPAddress)" -ForegroundColor Green
    }
    catch {
        Write-Host "$($domain): DNS resolution failed - $($_.Exception.Message)" -ForegroundColor Red
    }
}