# MagicInvest

Automatization of the Magic formula using Python. The ground truth output is in ground_truth.xlsx

 All the data to be retrieved from macrotrends.net

## Note To Developers

Developers should use the same code checking tools that are being used by the Github actions. Those are automatically configured using configuration files in the repository and all the tools and plugins can be downloaded using:

```bash
pip install -r dev_requirements.txt
```

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
3. Retrieving company names based on some parameters (parameters are in JSON file) (Utku)
4. Given company names, get the desired statistics (Alp)
5. Calculate the necessary formula parameters, given company statistics (RAFIL)
6. Using all the data, create an automated excel file (with report) (tbd)

## Coding Practices

1. OOP approach
2. Code should be as abstract as possible, depending on the parameters in JSON files
3. Each class will have a test defined
4. Tests should be called automatically
