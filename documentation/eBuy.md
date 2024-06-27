# eBuy
SRT has worked to integrate eBuy Open's active RFQs into the scraper to determine 508 compliance. Due to the security this process as of now is manual.

## Manual Process
Note: Be sure to have the latest code updates, and verify you have the ebuy_csv.py file.

Additionally, for ease, with the latest code execute a ```pip install -e .``` inside the srt-fbo-scraper local repo. 
### Export CSV
1. Navigate to [eBuy Open](https://www.ebuy.gsa.gov/ebuyopen/)
2. Log into the web interface
3. Go up to the columns button and select the following options:
   - RFQID
   - Attachments
   - AttachmentCount
   - BuyerAgency
   - BuyerEmail
   - Category
   - CategoryName
   - Description
   - IssueDate
   - Source
   - Status 
   - Title
4. Export the CSV
5. Place csv into the ebuy folder (srt-fbo-scraper/ebuy)

### Running ebuy_parser
Below is the help out for the ebuy_parser command line operation that should be avaliable after running the pip install above.

**Important:** Reach out to the lead developer at the time to obtain a local .env file that will provide you the postgres login data for the SRT databases on cloud.gov. **NEVER COMMIT THE .ENV FILE TO GITHUB!**

```
usage: ebuy_parser [-h] [-c _CONFIG] -f FILE [--model-name PREDICTION.MODEL_NAME] [--model-path PREDICTION.MODEL_PATH] [-e ENVIRONMENT]

options:
  -h, --help            show this help message and exit
  -c _CONFIG, --config _CONFIG
                        Define general configuration with yaml file
  -f FILE, --file FILE  eBuy CSV file to process

Prediction Model Options:
  --model-name PREDICTION.MODEL_NAME
                        Define the name to the prediction model in binaries folder.
  --model-path PREDICTION.MODEL_PATH
                        Define the absolute path to the prediction model.
  -e ENVIRONMENT, --environment ENVIRONMENT
                        Define the cloud.gov environment to run
```
1. In the command line you will specify multiple things, 1.) Exported csv file name, and 2.) Environment you want to insert the eBuy data into (defaults to local). 
2. Based on the environment the script will provide you with instructions on something to execute in a separate terminal window. Example:
```
cf ssh -L localhost:54000:<Service Database Name & password>:5432 srt-fbo-scraper-staging
```
This is to open local port to the postgres service instance in cloud.gov

3. Once that command is running, press enter to continue the ebuy_parser function.
4. Next, the parser will open up eBuy Open and that is when you will login with your credientials. 
5. Once logged in, you can press enter on your keyboard in the command line. The script obtained the security cookies needed to send out with each download request to eBuy's server. No security information will be saved once command is done.
6. Verify the script completes without errors, the RFQs are in the applicable environment, and you should be good to go. 