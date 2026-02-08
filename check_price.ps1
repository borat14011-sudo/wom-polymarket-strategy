$response = Invoke-WebRequest -Uri "https://gamma-api.polymarket.com/events?slug=us-strikes-iran-by" -UseBasicParsing
$data = $response.Content | ConvertFrom-Json

foreach ($market in $data.markets) {
    if ($market.question -like "*February 13*") {
        $yesPrice = [double]$market.outcomePrices[0] * 100
        $entryPrice = 12.0
        $positionSize = 4.20
        $priceDiff = $yesPrice - $entryPrice
        $pl = $priceDiff * $positionSize / $entryPrice
        
        Write-Host "Market: $($market.question)"
        Write-Host "Current: $($yesPrice.ToString('F1'))%"
        Write-Host "Entry: $($entryPrice)%"
        Write-Host "P/L: `$$($pl.ToString('F2')) ($($priceDiff.ToString('F1'))%)"
    }
}
