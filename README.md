# MagicInvest
Automatization of the Magic formula using Python. The ground truth output is in ground_truth.xlsx

 All the data to be retrieved from macrotrends.net


## Git Branch Naming Convention
1. No commit to master
2. FEATURES: feature/... 
3. BUGFIX: bugfix/...
4. SANDBOX: sandbox/...

## Tests
1. All modules will have their test script in tests/ folder
2. No commit to master without all tests being GREEN

## PARAMETERS
1. JSON files

## TODO - PLANNING
1. Web interface class (shared) (Utku) -> REUSABLE CODE 
2. Logger to be included in the classes (Alp)
2. Retrieving company names based on some parameters (parameters are in JSON file) (Utku)
3. Given company names, get the desired statistics (Alp)
4. Calculate the necessary formula parameters, given company statistics (RAFIL)
5. Using all the data, create an automated excel file (with report) (tbd)


## Coding Practices 
1. OOP approach
2. Code should be as abstract as possible, depending on the parameters in JSON files
3. Each class will have a test defined
4. Tests should be called automatically 