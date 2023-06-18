# "file_folder_rename_script.ps1"
#
# Invoke Like:
#	@echo off
#	REM DRAG AND DROP A FOLDER NAME ONTO THIS BAT
#	set "TopFolder=%~1"
#	powershell.exe -ExecutionPolicy Bypass -File "file_folder_rename_script.ps1" -TopFolder "%TopFolder%"

param( [Parameter(Mandatory = $true)] [string]$TopFolder )

# Pass 1: Update folder names
Get-ChildItem -Path $TopFolder -Recurse -Directory | ForEach-Object {
    $folderPath = $_.FullName
    $folderName = $_.Name

    $newFolderName = $folderName
	#Write-Host "FOLDER_CHECKING: '$folderName'"
    # (a) Check for Pattern A: DD-MM-YYYY or D-M-YYYY or D-MM-YYYY or DD-M-YYYY
    if ($folderName -match     '^(\d{1,2}|\d{2})[-_.](\d{1,2}|\d{2})[-_.](\d{4})(.*)$') {
        $matchedPart = $matches[0]
        Write-Host "FOLDER_MATCH (a): '$folderName' Matched Part: '$matchedPart'"
		$datePart_1 = $matches[1..3] -join '-'
		$datePart_2 = $matches[1..3] -join '_'
		$datePart_3 = $matches[1..3] -join '.'
		$newFolderName = $folderName
		$newFolderName = $newFolderName -replace $datePart_1, ""
		$newFolderName = $newFolderName -replace $datePart_2, ""
		$newFolderName = $newFolderName -replace $datePart_3, ""
        $dayPart = $matches[1]
        $monthPart = $matches[2]
        $yearPart = $matches[3]
        #$newFolderName = $newFolderName -replace $matchedPart, ""
        $reformattedDate = '{0:yyyy-MM-dd}' -f [datetime]::ParseExact("$dayPart-$monthPart-$yearPart", 'd-M-yyyy', $null)
        $trimmedFolderName = $newFolderName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
        if ($trimmedFolderName -eq '') {
            $newFolderName = $reformattedDate
        } else {
            $newFolderName = $reformattedDate + '_' + $trimmedFolderName
        }
		$newFolderName = $newFolderName -replace '_+', '_'
    }
    # (b) Check for Pattern B: YYYY-MM-DD or YYYY-M-D or YYYY-MM-D or YYYY-M-DD
    elseif ($folderName -match '^(\d{4})[-_.](\d{1,2}|\d{2})[-_.](\d{1,2}|\d{2})(.*)$') {
        $matchedPart = $matches[0]
        Write-Host "FOLDER_MATCH (b): '$folderName' Matched Part: '$matchedPart'"
		$datePart_1 = $matches[1..3] -join '-'
		$datePart_2 = $matches[1..3] -join '_'
		$datePart_3 = $matches[1..3] -join '.'
		$newFolderName = $folderName
		$newFolderName = $newFolderName -replace $datePart_1, ""
		$newFolderName = $newFolderName -replace $datePart_2, ""
		$newFolderName = $newFolderName -replace $datePart_3, ""
        $monthPart = $matches[2]
        $dayPart = $matches[3]
        #$newFolderName = newFolderName -replace $matchedPart, ""
        $reformattedDate = '{0:yyyy-MM-dd}' -f [datetime]::ParseExact("$dayPart-$monthPart-$yearPart", 'd-M-yyyy', $null)
        $trimmedFolderName = $newFolderName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
        if ($trimmedFolderName -eq '') {
            $newFolderName = $reformattedDate
        } else {
            $newFolderName = $reformattedDate + '_' + $trimmedFolderName
        }
		$newFolderName = $newFolderName -replace '_+', '_'
    }
    else {
        #Write-Host "FOLDER_NO_MATCH: $folderName"
		#$newFolderName = [regex]::Replace($newFolderName '_+', '_')
    }
    # Only print if the folder name is changing
	$newFolderName = $newFolderName -replace '\ ', '_'
	$newFolderName = $newFolderName -replace '\"', '_'
	$newFolderName = $newFolderName -replace '\''', '_'
	$newFolderName = $newFolderName -replace '\,', '_'
	$newFolderName = $newFolderName -replace '\+', '_'
	$newFolderName = $newFolderName -replace '\&', '_'
	$newFolderName = $newFolderName -replace '\!', '_'
	$newFolderName = $newFolderName -replace '\(', '_'
	$newFolderName = $newFolderName -replace '\)', '_'

	$newFolderName = $newFolderName -replace '_-_', '-'
	$newFolderName = $newFolderName -replace '-_', '-'
	$newFolderName = $newFolderName -replace '_-', '-'

	$newFolderName = $newFolderName -replace '_+', '_'	# not the same as the others
    $newFolderName = $newFolderName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
    if ($newFolderName -ne $folderName) {
        #Write-Host "FOLDER Current Name: '$folderPath' Proposed New Name: '$newFolderName'"
		Write-Host "Rename-Item -LiteralPath $folderPath -NewName $newFolderName -Force"
        # Uncomment the line below to perform the rename
        # Rename-Item -LiteralPath $folderPath -NewName $newFolderName -Force
    }
}

# Pass 2: Update file names
Get-ChildItem -Path $TopFolder -Recurse -File | ForEach-Object {
    $filePath = $_.FullName
    $fileName = $_.Name

	$newFileName = $fileName
	#Write-Host "FILE_CHECKING: $fileName"
    # (c) Check for Pattern A: DD-MM-YYYY or D-M-YYYY or D-MM-YYYY or DD-M-YYYY
    if ($fileName -match     '^(\d{1,2}|\d{2})[-_.](\d{1,2}|\d{2})[-_.](\d{4})(.*)$') {
        $matchedPart = $matches[0]
        Write-Host "FILE_MATCH (c): '$fileName' Matched Part: '$matchedPart'"
		$datePart_1 = $matches[1..3] -join '-'
		$datePart_2 = $matches[1..3] -join '_'
		$datePart_3 = $matches[1..3] -join '.'
		$newFileName = $fileName
		$newFileName = $newFileName -replace $datePart_1, ""
		$newFileName = $newFileName -replace $datePart_2, ""
		$newFileName = $newFileName -replace $datePart_3, ""
        $dayPart = $matches[1]
        $monthPart = $matches[2]
        $yearPart = $matches[3]
        #$newFileName = $newFileName -replace $matchedPart, ""
        $reformattedDate = '{0:yyyy-MM-dd}' -f [datetime]::ParseExact("$dayPart-$monthPart-$yearPart", 'd-M-yyyy', $null)
		$trimmedFileName = $newFileName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
		if ($trimmedFileName -eq '') {
		    $newFileName = $reformattedDate
		} else {
    		$newFileName = $reformattedDate + '_' + $trimmedFileName
		}
		$newFileName = $newFileName -replace '_+', '_'
    }
    # (d) Check for Pattern B: YYYY-MM-DD or YYYY-M-D or YYYY-MM-D or YYYY-M-DD
    elseif ($fileName -match '^(\d{4})[-_.](\d{1,2}|\d{2})[-_.](\d{1,2}|\d{2})(.*)$') {
        #$matchedPart = $matches[0]
        Write-Host "FILE_MATCH (d): '$fileName' Matched Part: '$matchedPart'"
		$datePart_1 = $matches[1..3] -join '-'
		$datePart_2 = $matches[1..3] -join '_'
		$datePart_3 = $matches[1..3] -join '.'
		$newFileName = $fileName
		$newFileName = $newFileName -replace $datePart_1, ""
		$newFileName = $newFileName -replace $datePart_2, ""
		$newFileName = $newFileName -replace $datePart_3, ""
        $yearPart = $matches[1]
        $monthPart = $matches[2]
        $dayPart = $matches[3]
        #$newFileName = $newFileName -replace $matchedPart, ""
        $reformattedDate = '{0:yyyy-MM-dd}' -f [datetime]::ParseExact("$dayPart-$monthPart-$yearPart", 'd-M-yyyy', $null)
        $trimmedFileName = $newFileName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
		if ($trimmedFileName -eq '') {
		    $newFileName = $reformattedDate
		} else {
    		$newFileName = $reformattedDate + '_' + $trimmedFileName
		}
		$newFileName = $newFileName -replace '_+', '_'
        #Write-Host "FILE_MATCH (d): '$fileName' Matched Part: '$matchedPart'  newFolderName reformatted: '$newFileName'"
    }
    else {
        #Write-Host "FILE_NO_MATCH: $fileName"
    }
    # Only print if the file name is changing
	$newFileName = $newFileName -replace '\ ', '_'
	$newFileName = $newFileName -replace '\"', '_'
	$newFileName = $newFileName -replace '\''', '_'
	$newFileName = $newFileName -replace '\,', '_'
	$newFileName = $newFileName -replace '\+', '_'
	$newFileName = $newFileName -replace '\&', '_'
	$newFileName = $newFileName -replace '\!', '_'
	$newFileName = $newFileName -replace '\(', '_'
	$newFileName = $newFileName -replace '\)', '_'

	$newFileName = $newFileName -replace '_-_', '-'
	$newFileName = $newFileName -replace '-_', '-'
	$newFileName = $newFileName -replace '_-', '-'
	
	$newFileName = $newFileName -replace '_+', '_'	# not the same as the others
    $newFileName = $newFileName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
    if ($newFileName -ne $fileName) {
        #Write-Host "FILE Current Name: '$filePath' Proposed New Name: '$newFileName'"
        Write-Host "Rename-Item -LiteralPath $filePath -NewName $newFileName -Force"
        # Uncomment the line below to perform the rename
        # Rename-Item -LiteralPath $filePath -NewName $newFileName -Force
    }
}




FIX SO  THYE DATE STUFF LOOKS  A BIT LIKE THIS



# Pass 1: Update folder names
Get-ChildItem -Path $TopFolder -Recurse -Directory | ForEach-Object {
    $folderPath = $_.FullName
    $folderName = $_.Name

    $newFolderName = $folderName

    # (a) Check for Pattern A: DD-MM-YYYY or D-M-YYYY or D-MM-YYYY or DD-M-YYYY
    if ($folderName -match '^(\d{1,2}|\d{2})[-_.](\d{1,2}|\d{2})[-_.](\d{4})(.*)$') {
        $matchedPart = $matches[0]
        Write-Host "FOLDER_MATCH (a): '$folderName' Matched Part: '$matchedPart'"
        $dayPart = $matches[1]
        $monthPart = $matches[2]
        $yearPart = $matches[3]

        # Validate the date
        if ([DateTime]::TryParseExact("$dayPart-$monthPart-$yearPart", 'd-M-yyyy', $null, [System.Globalization.DateTimeStyles]::None, [ref]$null)) {
            $reformattedDate = '{0:yyyy-MM-dd}' -f [datetime]::ParseExact("$dayPart-$monthPart-$yearPart", 'd-M-yyyy', $null)
            $trimmedFolderName = $folderName -replace $matchedPart, ''
            $trimmedFolderName = $trimmedFolderName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
            if ($trimmedFolderName -eq '') {
                $newFolderName = $reformattedDate
            } else {
                $newFolderName = $reformattedDate + '_' + $trimmedFolderName
            }
            $newFolderName = $newFolderName -replace '_+', '_'
        }
    }
    # (b) Check for Pattern B: YYYY-MM-DD or YYYY-M-D or YYYY-MM-D or YYYY-M-DD
    elseif ($folderName -match '^(\d{4})[-_.](\d{1,2}|\d{2})[-_.](\d{1,2}|\d{2})(.*)$') {
        $matchedPart = $matches[0]
        Write-Host "FOLDER_MATCH (b): '$folderName' Matched Part: '$matchedPart'"
        $yearPart = $matches[1]
        $monthPart = $matches[2]
        $dayPart = $matches[3]

        # Validate the date
        if ([DateTime]::TryParseExact("$dayPart-$monthPart-$yearPart", 'd-M-yyyy', $null, [System.Globalization.DateTimeStyles]::None, [ref]$null)) {
            $isLeapYear = [DateTime]::IsLeapYear($yearPart)
            $dateFormat = if ($isLeapYear) { 'd-M-yyyy' } else { 'd-M-yyyy' }
            $reformattedDate = '{0:yyyy-MM-dd}' -f [datetime]::ParseExact("$dayPart-$monthPart-$yearPart", $dateFormat, $null)
            $trimmedFolderName = $folderName -replace $matchedPart, ''
            $trimmedFolderName = $trimmedFolderName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
            if ($trimmedFolderName -eq '') {
                $newFolderName = $reformattedDate
            } else {
                $newFolderName = $reformattedDate + '_' + $trimmedFolderName
            }
            $newFolderName = $newFolderName -replace '_+', '_'
        }
    }

    # Rename the folder if necessary
    if ($newFolderName -ne $folderName) {
        $newFolderPath = Join-Path -Path $folderPath -ChildPath $newFolderName
        Rename-Item -Path $folderPath -NewName $newFolderName -Force
        Write-Host "Renamed folder: '$folderPath' to '$newFolderPath'"
    }
}
