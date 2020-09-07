# USGA Database
1. load_courses.py
    - Fetches a list of ids for every course in a given country
    - takes about 2.5 minutes to fetch all U.S. courses (~15,000)
2. get_course_info.py
    - Fetches details about a course, given an id
    - takes about 5 minutes for all U.S. courses
    - Saves it to local instance of AWS DynamoDB
    - NOTE: if running on OSX, [update certificates](https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org) first

## DynamoDB Setup
1. Setup AWS Account (may not actually be necessary yet)
2. Install AWS CLI (may not actually be necessary yet)
3. Install AWS DynamoDB

## Parallelism

