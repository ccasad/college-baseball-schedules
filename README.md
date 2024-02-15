TO DO

* (DONE) Create a git repo

* (DAD) Get schedules
  - (DONE) from all schools in google spreadsheet (D1, D2, D3 if possible, but start with D1)
  - (DONE) read in the google spreadsheet and loop through the schools
  - (DONE) parse out the schedules and write each to a file using the IPEDS number for the file name
  - issue with processor_alpha: schedule away games seems to have opponent as the home team?

* (TREV) Build calendar files
  - go through each schedule file to make a calendar.ics file from it
  - using the google spreadsheet find the school using the IPEDS number the file is named from

* (TREV) Build a dynamic calendar builder script
  - ask the user for list of IPEDS (schools) they are interested in
  - ask the user if they want home and/or away games
  - using the list of IPEDS numbers grab the schedule data and build a combined calendar.ics file from it

More advanced stuff
* Put the data either in AWS S3 buckets, DynamoDB or PostgreSQL
* create an api that others can hit that returns the schedule and/or calendar.ics
* Build a calendar of all the schools within X miles?
