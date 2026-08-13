"""Pytest root marker.

Its presence puts the repository root on ``sys.path``, so the test modules can
import the production packages as ``src.<stream>.<module>``.
"""
