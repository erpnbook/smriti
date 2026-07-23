$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:8080/")
$listener.Start()
Write-Host "SMRITI Local Server running at http://localhost:8080/"

$publicDir = "D:\Smriti_Retail_OS\smriti_retail_os\public"
$wwwDir = "D:\Smriti_Retail_OS\smriti_retail_os\www"

while ($listener.IsListening) {
    try {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        $urlPath = $request.Url.AbsolutePath

        if ($urlPath -eq "/") { $urlPath = "/sizewise_invoice" }

        $filePath = ""
        $contentType = "text/html; charset=utf-8"

        if ($urlPath.StartsWith("/assets/smriti_retail_os/")) {
            $relPath = $urlPath.Substring("/assets/smriti_retail_os/".Length)
            $filePath = Join-Path $publicDir $relPath
        } else {
            $cleanName = $urlPath.TrimStart("/").Split("?")[0].Split("#")[0]
            if (-not $cleanName.EndsWith(".html") -and -not $cleanName.Contains(".")) { 
                $cleanName = "$cleanName.html" 
            }
            $filePath = Join-Path $wwwDir $cleanName
        }

        if (Test-Path $filePath -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            
            if ($filePath.EndsWith(".css")) { $contentType = "text/css; charset=utf-8" }
            elseif ($filePath.EndsWith(".js")) { $contentType = "application/javascript; charset=utf-8" }
            elseif ($filePath.EndsWith(".png")) { $contentType = "image/png" }
            elseif ($filePath.EndsWith(".svg")) { $contentType = "image/svg+xml" }
            elseif ($filePath.EndsWith(".json")) { $contentType = "application/json; charset=utf-8" }

            $response.ContentType = $contentType
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $response.StatusCode = 404
            $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found: $urlPath")
            $response.OutputStream.Write($msg, 0, $msg.Length)
        }
        $response.Close()
    } catch {
        # continue listener loop
    }
}
