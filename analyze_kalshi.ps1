$data = Get-Content 'kalshi_latest.json' | ConvertFrom-Json

$eventCount = $data.events.Count
$totalMarkets = ($data.events | ForEach-Object { $_.markets.Count } | Measure-Object -Sum).Sum

Write-Output "Events: $eventCount"
Write-Output "Total Markets: $totalMarkets"
Write-Output ""
Write-Output "Sample Event Titles:"
$data.events[0..4] | ForEach-Object {
    $marketCount = $_.markets.Count
    Write-Output "  - $($_.title) [$marketCount markets]"
}
Write-Output ""
Write-Output "Categories:"
$data.events | Group-Object -Property category | Sort-Object Count -Descending | ForEach-Object {
    Write-Output "  - $($_.Name): $($_.Count) events"
}
Write-Output ""
Write-Output "Top 5 by Volume:"
$data.events | ForEach-Object {
    $event = $_
    $_.markets | ForEach-Object {
        [PSCustomObject]@{
            Title = $event.title
            Volume = $_.volume
            Price = $_.last_price_dollars
        }
    }
} | Sort-Object Volume -Descending | Select-Object -First 5 | ForEach-Object {
    Write-Output "  - $($_.Title) | Vol: $($_.Volume) | Price: $($_.Price)"
}
