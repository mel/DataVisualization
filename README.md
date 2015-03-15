# DataVisualization
Python script to push data to Elastic Search. Here is the high level overview
> An external source collects data and provide a CSV file as input to this script. First the file is copied 
from the source location to a destination location. Delete the file from the source location so that we do not end up
in lot many files since the external data gatherer collects data every hour and dumps it into a new file with timestamp. 
Create an excel worksheet from the CSV file. Create an elastcis earch index and populate the data. View the 
data in Kibana dashboard
