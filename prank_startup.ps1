$f='C:\Users\Public\p.jpg'
(New-Object Net.WebClient).DownloadFile('https://i.imgur.com/6hfXmtp.png',$f)
$q=[char]34
Add-Type -MemberDefinition ('[DllImport('+$q+'user32.dll'+$q+')]public static extern int SystemParametersInfo(int a,int b,string c,int d);') -Name W -Namespace N
Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name WallpaperStyle -Value 2
Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name TileWallpaper -Value 0
[N.W]::SystemParametersInfo(20,0,$f,3)
