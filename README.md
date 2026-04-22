# nyc-taxi-pipeline
Practice pipeline building for NY Taxi dataset

## Phase 1: Data expliration
Practice some data exploration on paruet file using pandas
Define business questions and calculate for answers 

## Phase 2: Data ingesition
Creatig bucket for cloud project using Google Cloud Platform
Create dataset infraestructure to load data

### Data quality findings

- Original dataset contains 1,114320 trips
- 11,729 trips has less than 1 mitute or more than 300 minutes
- Those records will be filtered on transformatin phase
- Clean data represents %98.95 of original dataset