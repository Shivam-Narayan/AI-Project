1.To create a virtual environment, open the terminal and navigate to the directory where you want to create the environment. Then type the following command:
```bash
python -m venv hr_portal
```
This will create a new virtual environment named "hr_portal".git 



```
2.Install the required dependencies using pip:

For installing the python dependencies required for the project, run the following command by going into the project directory.
 ```bash
 pip install -r requirements.txt
 ```


>Run the requirement installation command again



3. Set up the database by running the following commands:
   _By default the test database will be loaded which will have demo data inside it. If you wish to start with a fresh database, you can  change the name of the database inside the horilla/settings.py file. 
```bash
python manage.py makemigrations
python manage.py migrate
```


4. Running the project
To run the project locally, execute the following command:

```bash
python manage.py runserver
```
