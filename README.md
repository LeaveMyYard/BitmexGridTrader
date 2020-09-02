

<p align="center"><img src="assets/screenshot.png?raw=true" alt="re-frame logo"></p>

## Bitmex Grid Bot

[![GitHub issues](https://img.shields.io/github/issues-raw/LeaveMyYard/BitmexGridTrader?style=flat-square)](https://github.com/LeaveMyYard/BitmexGridTrader/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/LeaveMyYard/BitmexGridTrader?style=flat-square)](https://github.com/LeaveMyYard/BitmexGridTrader/pulls)
[![License](https://img.shields.io/github/license/day8/re-frame.svg?style=flat-square)](LICENSE.txt)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

## Overview

This is the bitmex trading bot, created for Grid strategy on XBTUSD futures pair.

Build with python, all sourse code provided.

It has a PyQt5 user interface, that is easy to use.

Keep in mind, that using different settings could result in different profits and losses. This program is not guaranteed to contain a money-making machine.

Also, this program is new and could contain bugs, that could result in losing some bitcoins. I am not responsible for that, but feel free to report those bugs and I will try to get rid of them

## Installation

Copy this repository's code from github. It was written using Python 3.7.7, but other versions should be compatable also.

Make `cd` to the project's folder and make `pip install -r requirements.txt`

After that, make `python trade.py` and the program will start with the UI.

## Known bugs

* The "Stop bot" button will not stop the bot from updating a grid.

## TODO

- [ ] Add more exchanges to trade on (Binance Futures, BitFinex etc)
- [x] ~~Move exchange handlers to the other repo, make it a package~~
- [ ] Make it into a pip package and make possible for program to be used from code
- [ ] Compile a documentation

## Licence

Bitmex Grid Bot is [MIT licenced](LICENSE.txt)
