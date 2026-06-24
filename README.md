# LogSentinal
***Real Time Multiple Log Files Monitoring System***


---
## To run the System:

1. Clone the repository in your system.
2. Open a new terminal in the cloned folder.
3. Run the following commands in order:

    ```python
    pip install -r requirements.txt

    cd Frontend/LogSentinal
    npm run dev
    ```
4. Open a New Terminal from the base directory and run the following commands
    ```python
    cd Backend
    python server.py
    ``` 
---
## Notes:
1. Summary Reports will be created in the folder SummaryReports.
2. Databases will be present in the Databases folder present in Backend Directory.
3. 3. Currently the threshold values are less for Development only. Also the flushing of new data happens every 1 min...
