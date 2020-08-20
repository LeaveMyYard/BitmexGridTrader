

<p align="center"><img src="assets/screenshot.png?raw=true" alt="re-frame logo"></p>

## Bitmex Grid Bot

[![GitHub issues](https://img.shields.io/github/issues-raw/LeaveMyYard/BitmexGridTrader?style=flat-square)](https://github.com/LeaveMyYard/BitmexGridTrader/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/LeaveMyYard/BitmexGridTrader?style=flat-square)](https://github.com/LeaveMyYard/BitmexGridTrader/pulls)
[![License](https://img.shields.io/github/license/day8/re-frame.svg?style=flat-square)](LICENCE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

## Overview

This is the bitmex trading bot, created for Grid strategy on XBTUSD futures pair.

It has a PyQt5 user interface, that is easy to use.

## Installation

Copy this repository's code from github. It was written using Python 3.7.7, but other versions should be compatable also.

Make `cd` to the project's folder and make `pip install -r requirements.txt`

After that, make `python trade.py` and the program will start with the UI.

<!-- ## Documentation 

The documentation is [available here](http://day8.github.io/re-frame/). -->

## TODO

* Add more exchanges to trade on (Binance Futures, BitFinex etc)
* Move exchange handlers to the other repo, make it a package
* Make it into a pip package and make possible for program to be used from code
* Compile a documentation


## Licence

Bitmex Grid Bot is [MIT licenced](LICENCE)