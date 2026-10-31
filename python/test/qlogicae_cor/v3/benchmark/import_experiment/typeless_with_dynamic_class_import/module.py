# typeless_with_dynamic_class_import

__all__ = (
    "Subject"
)

_Subject = None
_handle_dyamic_imports = None

def _handle_dyamic_imports():
    import abc
    import argparse
    import array
    import ast
    import asyncio
    import atexit
    import base64
    import binascii
    import bisect
    import builtins
    import bz2
    import calendar
    import cmath
    import cmd
    import code
    import codecs
    import codeop
    import collections
    import collections.abc
    import colorsys
    import compileall
    import concurrent
    import concurrent.futures
    import configparser
    import contextlib
    import contextvars
    import copy
    import csv
    import ctypes
    import dataclasses
    import datetime
    import decimal
    import difflib
    import dis
    import doctest
    import email
    import email.mime
    import enum
    import errno
    import faulthandler
    import filecmp
    import fileinput
    import fnmatch
    import fractions
    import functools
    import gc
    import getopt
    import getpass
    import gettext
    import glob
    import graphlib
    import gzip
    import hashlib
    import heapq
    import hmac
    import html
    import html.entities
    import html.parser
    import http
    import http.client
    import http.cookies
    import http.server
    import importlib
    import importlib.machinery
    import importlib.metadata
    import importlib.resources
    import inspect
    import io
    import ipaddress
    import itertools
    import json
    import keyword
    import linecache
    import locale
    import logging
    import lzma
    import mailbox
    import math
    import mimetypes
    import mmap
    import modulefinder
    import multiprocessing
    import multiprocessing.pool
    import netrc
    import numbers
    import operator
    import optparse
    import os
    import pathlib
    import pdb
    import pickle
    import pickletools
    import pkgutil
    import platform
    import plistlib
    import poplib
    import pprint
    import profile
    import pstats
    import pty
    import pwd
    import py_compile
    import pyclbr
    import pydoc
    import queue
    import quopri
    import random
    import re
    import readline
    import reprlib
    import resource
    import rlcompleter
    import runpy
    import sched
    import secrets
    import select
    import selectors
    import shelve
    import shlex
    import shutil
    import signal
    import site
    import smtplib
    import socket
    import socketserver
    import sqlite3
    import ssl
    import stat
    import statistics
    import string
    import stringprep
    import struct
    import subprocess
    import sys
    import sysconfig
    import tabnanny
    import tarfile
    import tempfile
    import textwrap
    import threading
    import time
    import timeit
    import tkinter
    import tkinter.ttk
    import token
    import tokenize
    import trace
    import traceback
    import tracemalloc
    import tty
    import types
    import typing
    import unicodedata
    import unittest
    import urllib
    import urllib.error
    import urllib.parse
    import urllib.request
    import uuid
    import warnings
    import wave
    import weakref
    import webbrowser
    import wsgiref
    import wsgiref.simple_server
    import xml
    import xml.dom
    import xml.etree
    import xml.etree.ElementTree
    import xml.parsers
    import xml.sax
    import xmlrpc
    import xmlrpc.client
    import xmlrpc.server
    import zipapp
    import zipfile
    import zipimport
    import zlib

    _handle_dyamic_imports = lambda: None


def Subject():
    global _Subject
    global _handle_dyamic_imports

    if _Subject:
        return _Subject    

    class __Subject:
        _singleton = None

        def __init__(self):
            _handle_dyamic_imports()

        @classmethod
        def get_singleton(cls):
            if cls._singleton:
                return cls._singleton

            cls._singleton = cls()

            return cls._singleton

    _Subject = __Subject

    return _Subject


# a = Subject().get_singleton()
# b = Subject().get_singleton()
# print(a)
# print(b)
# print(a == b)
