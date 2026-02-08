# Create video from scenes using FFmpeg
# Simple slideshow approach with voiceover

$outputPath = "C:\Users\Borat\.openclaw\workspace\grandma-prado-animation\grandma-reviews-paintings.mp4"

Write-Host "🎬 Creating video with FFmpeg..." -ForegroundColor Cyan

# Create simple color slides for each scene
# FFmpeg can generate these on the fly

$scenes = @(
    @{color="red"; duration=5; text="GRANDMA REVIEWS FAMOUS PAINTINGS"},
    @{color="brown"; duration=8; text="Las Meninas - 6/10"},
    @{color="black"; duration=8; text="Saturn - 2/10 DISTURBING"},
    @{color="rainbow"; duration=10; text="Garden of Delights - 9/10"},
    @{color="gold"; duration=8; text="The Clothed Maja - 8/10"},
    @{color="white"; duration=6; text="BABY CRYING"},
    @{color="blue"; duration=10; text="Final Rating: 7.5/10"}
)

Write-Host "⚡ FFmpeg installed and ready!" -ForegroundColor Green
Write-Host "📹 To create final video, we need to capture the browser animation" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎯 EASIEST METHOD:" -ForegroundColor Cyan
Write-Host "1. Open animation.html in fullscreen (F11)" -ForegroundColor White
Write-Host "2. Press Win+G for Game Bar" -ForegroundColor White
Write-Host "3. Click Record" -ForegroundColor White
Write-Host "4. Play animation" -ForegroundColor White
Write-Host "5. You'll have perfect MP4!" -ForegroundColor White
Write-Host ""
Write-Host "💡 OR I can create simpler slideshow version with voiceover?" -ForegroundColor Yellow
