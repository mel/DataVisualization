# DataVisualization
Python script to push data to Elastic Search. Here is the high level overview

An external source collects data and provides a CSV file as input to this script. First the file is copied from the source location to a destination location. Once copied the script deletes the file from the source location so that we do not endup in lot many files since the external data collector gathers data every hour and dumps it into a new file with timestamp. We create an excel worksheet from the CSV file. Elastic search index is created and data populated. View the data in Kibana dashboard
