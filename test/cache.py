"""
Unit tests for nyx.cache.
"""

import tempfile
import unittest

import nyx

from mock import Mock, patch

FINGERPRINT = '3EA8E960F6B94CE30062AA8EF02894C00F8D1E66'
ADDRESS = '208.113.165.162'
PORT = 1443
NICKNAME = 'caersidi'


class TestCache(unittest.TestCase):
  def setUp(self):
    nyx.CACHE = None  # drop cached database reference

  @patch('nyx.data_directory', Mock(return_value = None))
  def test_memory_cache(self):
    """
    Create a cache in memory.
    """

    with nyx.cache() as cache:
      self.assertEqual((0, 'main', ''), cache.execute("PRAGMA database_list").fetchone())
      cache.execute('INSERT INTO relays(fingerprint, address, or_port, nickname) VALUES (?,?,?,?)', (FINGERPRINT, ADDRESS, PORT, NICKNAME))
      self.assertEqual(NICKNAME, cache.execute('SELECT nickname FROM relays WHERE fingerprint=?', (FINGERPRINT,)).fetchone()[0])

  def test_file_cache(self):
    """
    Create a new cache file, and ensure we can reload cached results.
    """

    with tempfile.NamedTemporaryFile(suffix = '.sqlite') as tmp:
      with patch('nyx.data_directory', Mock(return_value = tmp.name)):
        with nyx.cache() as cache:
          self.assertEqual((0, 'main', tmp.name), cache.execute("PRAGMA database_list").fetchone())
          cache.execute('INSERT INTO relays(fingerprint, address, or_port, nickname) VALUES (?,?,?,?)', (FINGERPRINT, ADDRESS, PORT, NICKNAME))
          cache.commit()

        nyx.CACHE = None

        with nyx.cache() as cache:
          self.assertEqual(NICKNAME, cache.execute('SELECT nickname FROM relays WHERE fingerprint=?', (FINGERPRINT,)).fetchone()[0])
