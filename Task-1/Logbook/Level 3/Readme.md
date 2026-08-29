In level 3 at first when i checked i didnt find anything so i changed the branch to little_garden and then in which i found three directory sectors alpha beta and gamma i then used find . -type f -name "*.log" -exec md5sum {} \; | sort | uniq -w32 -u
The find . searches from current directory 
-type f only considers the type file 
-name "*.log" takes the files ending with .log   
-exec md5sum {} \;  md5sum is a  command that creates a 32-character fingerprint (hash) for a file and {} inserts file name and /; ends the execution
| sort will sort the files 
| uniq -w32 -u  will tell uniq to compare only the first 32 characters — the MD5 hashes.

Using this command i found the file which was had the clue and then i inspected it and found the Poneglyph fragment 1
