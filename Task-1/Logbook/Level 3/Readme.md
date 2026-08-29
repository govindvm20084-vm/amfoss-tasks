In Level 3, I initially checked the available files but could not find anything useful. I then switched to the little_garden branch, where I found three directories sector_alpha, sector_beta, and sector_gamma.I then used find . -type f -name "*.log" -exec md5sum {} \; | sort | uniq -w32 -u

The find . searches from current directory 
-type f only considers the type file 
-name "*.log" takes the files ending with .log   
-exec md5sum {} \;  md5sum is a  command that creates a 32-character fingerprint (hash) for a file and {} inserts file name and /; ends the execution
| sort will sort the files 
| uniq -w32 -u  will tell uniq to compare only the first 32 characters — the MD5 hashes.

Using this command i found the file which had the clue and then i inspected it and found the Poneglyph fragment 1
