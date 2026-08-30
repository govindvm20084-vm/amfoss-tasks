I started by finding out how I could get system information through Python. I used the psutil library for this.
First, I used psutil.process_iter() to go through the running processes and collected their PID, name, CPU usage, and memory usage. I then stored this information and sorted it by CPU usage so that the processes using the most CPU would be shown first.
After that, I created a simple function to display CPU and memory usage as bars using # and -.
For the actual terminal interface, I used the curses library. I used it to display the system information, process list, and different colors in the terminal. The screen is refreshed every 0.7 seconds so the information stays updated.
I also added error handling for processes that cannot be accessed or that disappear while the program is running. Finally, I added the q key to exit the program.

New Concepts I Learned :
.Using external Python libraries
.Getting system information using psutil
.Getting information about running processes
.Using curses to create a terminal interface
.Updating information continuously
.Sorting data using a key
.Handling exceptions such as NoSuchProcess and AccessDenied
.Using CPU and memory percentages
.Working with terminal colors
