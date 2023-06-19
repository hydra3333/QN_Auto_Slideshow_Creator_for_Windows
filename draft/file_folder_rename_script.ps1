# "file_folder_rename_script.ps1"
#
# Invoke Like:
#	@echo off
#	REM DRAG AND DROP A FOLDER NAME ONTO THIS BAT
#	set "TopFolder=%~1"
#	powershell.exe -ExecutionPolicy Bypass -File "file_folder_rename_script.ps1" -TopFolder "%TopFolder%"

param( [Parameter(Mandatory = $true)] [string]$TopFolder )


# https://stackoverflow.com/questions/76503659/powershell-match-not-matching-as-hoped-seeking-advice
$regex_date_format_both = '(?x)	# DD-MM-YYYY D-M-YYYY D-MM-YYYY DD-M-YYYY YYYY-MM-DD YYYY-M-D YYYY-MM-D YYYY-M-DD
\b(?:
	(?<day>[0-9]{1,2})[-_.]
	(?<month>[0-9]{1,2})[-_.]
	(?<year>[0-9]{4})
  |
	(?<year>[0-9]{4})[-_.]
	(?<month>[0-9]{1,2})[-_.]
	(?<day>[0-9]{1,2})
)'
$regex_date_format_DDMMYYYY = '(?x)	# DD-MM-YYYY D-M-YYYY D-MM-YYYY DD-M-YYYY
\b(?:
	(?<day>[0-9]{1,2})[-_.]
	(?<month>[0-9]{1,2})[-_.]
	(?<year>[0-9]{4})
)'

$regex_date_format_YYYYMMDD = '(?x)	# YYYY-MM-DD YYYY-M-D YYYY-MM-D YYYY-M-DD
\b(?:
	(?<year>[0-9]{4})[-_.]
	(?<month>[0-9]{1,2})[-_.]
	(?<day>[0-9]{1,2})
)'
#
$regex_month_format_both = '(?x)	# MM-YYYY M-YYYY YYYY-MM YYYY-M
\b(?:
	(?<month>[0-9]{1,2})[-_.]
	(?<year>[0-9]{4})
  |
	(?<year>[0-9]{4})[-_.]
	(?<month>[0-9]{1,2})
)'
$regex_month_format_MMYYYY = '(?x)	# MM-YYYY M-YYYY
\b(?:
	(?<month>[0-9]{1,2})[-_.]
	(?<year>[0-9]{4})
)'
$regex_month_format_YYYYMM = '(?x)	# YYYY-MM YYYY-M
\b(?:
	(?<year>[0-9]{4})[-_.]
	(?<month>[0-9]{1,2})
)'


# Pass 1: Update folder names
Get-ChildItem -Path $TopFolder -Recurse -Directory | ForEach-Object {
	$folderPath = $_.FullName
	$folderName = $_.Name
	$newFolderName = $folderName
	#
	if ($folderName -match $regex_date_format_both) {	# DD-MM-YYYY D-M-YYYY D-MM-YYYY DD-M-YYYY
		$matched_text = $Matches[0]
		#Write-Host "FOLDER_MATCH FULL_DATE: '$folderName' cotained '$matched_text'"
		$year  = $Matches['year']
		$month = $Matches['month'].PadLeft(2, '0')
		$day   = $Matches['day'].PadLeft(2, '0')
		$newFolderName = $newFolderName -replace $matched_text, ""
		$newFolderName = $newFolderName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
		$reformattedDate = $year + "_" + $month + "_" + $day
		if ($newFolderName -eq '') {
			$newFolderName = $reformattedDate
		} else {
			$newFolderName = $reformattedDate + '_' + $newFolderName
		}
	} elseif ($folderName -match $regex_month_format_both) {
		$matched_text = $Matches[0]
		#Write-Host "FOLDER_MATCH MONTH_DATE: '$folderName' contained '$matched_text'"
		$year  = $Matches['year']
		$month = $Matches['month'].PadLeft(2, '0')
		$newFolderName = $newFolderName -replace $matched_text, ""
		$newFolderName = $newFolderName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
		$reformattedDate = $year + "_" + $month
		if ($newFolderName -eq '') {
			$newFolderName = $reformattedDate
		} else {
			$newFolderName = $reformattedDate + '_' + $newFolderName
		}
	} else {
		#Write-Host "FOLDER_NO_MATCH: $folderName"
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
	#
	if ($fileName -match $regex_date_format_both) {	# DD-MM-YYYY D-M-YYYY D-MM-YYYY DD-M-YYYY
		$matched_text = $Matches[0]
		#Write-Host "FILE_MATCH FULL_DATE: '$folderName' contained '$matched_text'"
		$year  = $Matches['year']
		$month = $Matches['month'].PadLeft(2, '0')
		$day   = $Matches['day'].PadLeft(2, '0')
		$newFileName = $newFileName -replace $matched_text, ""
		$newFileName = $newFileName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
		$reformattedDate = $year + "_" + $month + "_" + $day
		if ($newFileName -eq '') {
			$newFileName = $reformattedDate
		} else {
			$newFileName = $reformattedDate + '_' + $newFileName
		}
	#} elseif ($fileName -match $regex_month_format_both) {
	#	$matched_text = $Matches[0]
	#	#Write-Host "FILE_MATCH MONTH_DATE: '$folderName' cotained '$matched_text'"
	#	$year  = $Matches['year']
	#	$month = $Matches['month'].PadLeft(2, '0')
	#	$newFileName = $newFileName -replace $matched_text, ""
	#	$newFileName = $newFileName.Trim().TrimStart('_').TrimEnd('_').TrimStart('-').TrimEnd('-').TrimStart('.').TrimEnd('.')
	#	$reformattedDate = $year + "_" + $month
	#	if ($newFileName -eq '') {
	#		$newFileName = $reformattedDate
	#	} else {
	#		$newFileName = $reformattedDate + '_' + $newFileName
	#	}
	} else {
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
