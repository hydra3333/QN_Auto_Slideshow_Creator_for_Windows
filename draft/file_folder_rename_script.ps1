# Copyright (C) <2023> <ongoing>  <hydra3333>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Sanitize FolderNames and FileNames in a folder tree.
# Remove commas, ampersands, spaces and whatnot and replace them with underscores.
# Identify a date in a Folder/File name and rename the folder/file with that date moved
# to the front of the name in the format YYYY-MM-DD ... greatly assists with sorting.
#
# NEVER use this on an original source tree - it renames files/folders
# ... you know before you start that you'll not get the original folder/file names back again.
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
if ($true) {
Write-Host "START FOLDER RENAMES"
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
		Rename-Item -LiteralPath $folderPath -NewName $newFolderName -Force
	}
}
Write-Host "END FOLDER RENAMES"
}

if ($true) {
Write-Host "START FILE FOLDER RENAMES"
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
		Rename-Item -LiteralPath $filePath -NewName $newFileName -Force
	}
}
Write-Host "END FILE RENAMES"
}