""" 

 TODO:
 - Add buttons to digitally sign on client vs. user accounts to accept testpoints, make buttons disabled until all fields filled in
 - Add a popover/tooltip to show who clicked the button and when
 - Add calibration equipment records to each test point, including the cal due dates

 - Add ability to change units on a testpoint in the channel list view
 - Add ability to convert between similar unit types (psig -> psia, degC to degF, Ohms -> degC (Pt100)) in new channel form or channel list view

 - Create enum types for all the integers stored in the database
 - Add dividers to the testpoint progress bars
 - Add colours into the min/max of the measured column if error is exceeded, maybe make text too
 - Move all the if statements in the _testpoint.html file into the routes file to pre-prep the form fields
 - Add an info button on a channel to peek at the remaining undisplayed data from the creation of the channel
 - Add badges into the channel list header to show number of pass/fail/posts
 - Add an edit button in the channel view to make visible new buttons to add/remove testpoints in a row
 - Create a calibration equipment table and form to create a list of them to store
 - Create an ajax queue handler to avoid the read/write database locking for the channel list editing
 - Create a user history that logs all the users signature button clicks and commissioning info

 Future TODO:
 - Add a chart to the testpoint view
 - Add ability to import MCL data to populate the ICT for a project
 - Add ability to create a new like on existing channel definitions

 """