# RCO_Scramble

RCO_Scramble is a Python script designed to generate pairings for an RCO scramble tournament. Its primary goals are to minimize repeated pairings and ensure each player receives a balanced schedule.

## Features

- Generates pairings for RCO scramble tournaments, when players enter as individuals and are paired with opposite-gender partners each round to face new opponents
- Minimizes repeat partners and repeat opponents
- Provides fair scheduling for all participants by minimizing repeat partners and repeat opponents, and evenly sharing games
- Configurable number of simultaneous courts and total rounds
- Supports different number of men and of women
- Deterministic; running the scheduler with the same inputs (algorithm parameters, number of courts, number of rounds, number of men, and number of women) will generate the same schedule
- Algorithm can be tuned to adjust weighting given to repeat partners, repeat opponents, uneven game distribution, and back-to-back games

## Usage

## Current Branches

- **main**: Stable release with core pairing logic and basic scheduling, meant for use as Python script with an IDE
- **dev**: Development branch for new features of the core algorithm/pairing logic
- **Render-deployed**: Stable release the website is built off of, includes Flask and the webpage frontend for the algorithm.
- **render-deploy-dev**: Development branch for new features of the website.

